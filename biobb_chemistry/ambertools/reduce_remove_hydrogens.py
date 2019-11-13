#!/usr/bin/env python3

"""Module containing the Open Babel class and the command line interface."""
import os
import argparse
from biobb_common.configuration import settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_common.command_wrapper import cmd_wrapper
from biobb_chemistry.ambertools.common import *

class ReduceRemoveHydrogens():
    """Removes hydrogen atoms to small molecules.
    Wrapper of the Ambertools reduce module. Removes hydrogens from a given structure.
    Reduce is a program for adding hydrogens to a Protein DataBank (PDB) molecular structure file: http://ambermd.org/doc12/AmberTools12.pdf

    Args:
        input_path (str): Path to the input file. Accepted formats: pdb.
        output_path (str): Path to the output file. Accepted formats: pdb.
        properties (dic):
            * **reduce_path** (*str*) - ("reduce") Path to the reduce executable binary.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **container_path** (*string*) - (None) container path definition
            * **container_image** (*string*) - ('afandiadib/ambertools:serial') container image definition
            * **container_volume_path** (*string*) - ('/tmp') container volume path definition
            * **container_user_id** (*string*) - (None) container user_id definition
    """

    def __init__(self, input_path, output_path, properties=None, **kwargs):
        properties = properties or {}

        # Input/Output files
        self.io_dict = { 
            "in": { "input_path": input_path }, 
            "out": { "output_path": output_path } 
        }

        # Properties specific for BB
        self.reduce_path = get_binary_path(properties, 'reduce_path')
        self.properties = properties

        # container Specific
        self.container_path = properties.get('container_path')
        self.container_image = properties.get('container_image', 'afandiadib/ambertools:serial')
        self.container_volume_path = properties.get('container_volume_path', '/tmp')
        self.container_user_id = properties.get('user_id', str(os.getuid()))

        # Properties common in all BB
        self.can_write_console_log = properties.get('can_write_console_log', True)
        self.global_log = properties.get('global_log', None)
        self.prefix = properties.get('prefix', None)
        self.step = properties.get('step', None)
        self.path = properties.get('path', '')

        self.remove_tmp = properties.get('remove_tmp', True)
        self.restart = properties.get('restart', False)

    def create_cmd(self, container_io_dict, out_log, err_log):
        """Creates the command line instruction using the properties file settings"""
        instructions_list = []

        # executable path
        instructions_list.append(self.reduce_path)

        instructions_list.append('-Trim')

        instructions_list.append(container_io_dict["in"]["input_path"])
        instructions_list.append('>')
        instructions_list.append(container_io_dict["out"]["output_path"])

        return instructions_list

    def launch(self):
        """Launches the execution of the Open Babel module."""
        
        # Get local loggers from launchlogger decorator
        out_log = getattr(self, 'out_log', None)
        err_log = getattr(self, 'err_log', None)

        # Check the properties
        fu.check_properties(self, self.properties)

        if self.restart:
            output_file_list = [self.output_path]
            if fu.check_complete_files(output_file_list):
                fu.log('Restart is enabled, this step: %s will the skipped' % self.step, out_log, self.global_log)
                return 0

        # copy inputs to container
        container_io_dict = fu.copy_to_container(self.container_path, self.container_volume_path, self.io_dict)

        # create cmd and launch execution
        cmd = self.create_cmd(container_io_dict, out_log, err_log)
        cmd = fu.create_cmd_line(cmd, container_path=self.container_path, host_volume=container_io_dict.get("unique_dir"), container_volume=self.container_volume_path, user_uid=self.container_user_id, container_image=self.container_image, out_log=out_log, global_log=self.global_log)
        returncode = cmd_wrapper.CmdWrapper(cmd, out_log, err_log, self.global_log).launch()

        # copy output(s) to output(s) path(s) in case of container execution
        fu.copy_to_host(self.container_path, container_io_dict, self.io_dict)

        # remove temporary folder(s)
        if self.container_path: 
            fu.rm(container_io_dict['unique_dir'])
            fu.log('Removed: %s' % str(container_io_dict['unique_dir']), out_log)

        return returncode

def main():
    parser = argparse.ArgumentParser(description="Removes hydrogen atoms to small molecules.", formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')
    parser.add_argument('--system', required=False, help="Check 'https://biobb-common.readthedocs.io/en/latest/system_step.html' for help")
    parser.add_argument('--step', required=False, help="Check 'https://biobb-common.readthedocs.io/en/latest/system_step.html' for help")

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_path', required=True, help='Path to the input file. Accepted formats: pdb.')
    required_args.add_argument('--output_path', required=True, help='Path to the output file. Accepted formats: pdb.')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config, system=args.system).get_prop_dic()
    if args.step:
        properties = properties[args.step]

    # Specific call of each building block
    ReduceRemoveHydrogens(input_path=args.input_path, output_path=args.output_path, properties=properties).launch()

if __name__ == '__main__':
    main()
