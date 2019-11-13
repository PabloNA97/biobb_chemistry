#!/usr/bin/env python3

"""Module containing the Acpype class and the command line interface."""
import os
import argparse
from biobb_common.configuration import  settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_common.command_wrapper import cmd_wrapper
from biobb_chemistry.acpype.common import *

class AcpypeParamsGMXOPLS():
    """Small molecule parameterization for OPLS/AA MD package.
    Wrapper for the Acpype module. Generation of topologies for OPLS/AA.
    Acpype is a tool based in Python to use Antechamber to generate topologies for chemical
    compounds and to interface with others python applications like CCPN or ARIA. 
    Visit the official page: https://github.com/alanwilter/acpype

    Args:
        input_path (str): Path to the input file. Accepted formats: pdb, mdl, mol2.
        output_path_itp (str): Path to the ITP output file. Accepted formats: itp.
        output_path_top (str): Path to the TOP output file. Accepted formats: top.
        properties (dic):
            * **basename** (*str*) - ("BBB") A basename for the project (folder and output files).
            * **charge** (*int*) - (0) Net molecular charge, for gas default is 0.
            * **acpype_path** (*str*) - ("acpype") Path to the acpype executable binary.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **container_path** (*string*) - (None) container path definition
            * **container_image** (*string*) - ('afandiadib/ambertools:serial') container image definition
            * **container_volume_path** (*string*) - ('/tmp') container volume path definition
            * **container_user_id** (*string*) - (None) container user_id definition
    """

    def __init__(self, input_path, output_path_itp, output_path_top, properties=None, **kwargs):
        properties = properties or {}

        # Input/Output files
        self.io_dict = { 
            "in": { "input_path": input_path }, 
            "out": { "output_path_itp": output_path_itp, "output_path_top": output_path_top } 
        }

        # Properties specific for BB
        self.basename = properties.get('basename', '')
        self.charge = properties.get('charge', '')
        self.acpype_path = get_binary_path(properties, 'acpype_path')
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

    def check_data_params(self, out_log, err_log):
        """ Checks all the input/output paths and parameters """
        self.io_dict["in"]["input_path"] = check_input_path(self.io_dict["in"]["input_path"], out_log, self.__class__.__name__)
        self.io_dict["out"]["output_path_itp"] = check_output_path(self.io_dict["out"]["output_path_itp"], 'itp', out_log, self.__class__.__name__)
        self.io_dict["out"]["output_path_top"] = check_output_path(self.io_dict["out"]["output_path_top"], 'top', out_log, self.__class__.__name__)
        self.output_files = {
            'itp': self.io_dict["out"]["output_path_itp"],
            'top': self.io_dict["out"]["output_path_top"],
        }

    def create_cmd(self, container_io_dict, out_log, err_log):
        """Creates the command line instruction using the properties file settings"""
        instructions_list = []

        # generating output path and adding cd /tmp; in case of container because ACPYPE needs writting permissions in the 
        # execution folder for a temporary folder creation (.acpype_tmp_BBB.<3Q3Atz>)
        if self.container_path:
            instructions_list.append('cd ' + self.container_volume_path + ';')
            out_pth = self.container_volume_path + '/' + get_basename(self.basename, out_log) + '.' + self.unique_name
        else:
            out_pth = get_basename(self.basename, out_log) + '.' + self.unique_name

        # executable path
        instructions_list.append(self.acpype_path)

        # generating input 
        ipath = '-i ' + container_io_dict["in"]["input_path"]
        instructions_list.append(ipath)

        # generating output 
        basename = '-b ' + out_pth
        instructions_list.append(basename)

        # adding charge
        charge = '-n ' + get_charge(self.charge, out_log)
        instructions_list.append(charge)

        return instructions_list

    @launchlogger
    def launch(self):
        """Launches the execution of the Open Babel module."""
        
        # Get local loggers from launchlogger decorator
        out_log = getattr(self, 'out_log', None)
        err_log = getattr(self, 'err_log', None)

        # check input/output paths and parameters
        self.check_data_params(out_log, err_log)

        # Check the properties
        fu.check_properties(self, self.properties)

        if self.restart:
            output_file_list = [self.output_path_itp, self.output_path_top]
            if fu.check_complete_files(output_file_list):
                fu.log('Restart is enabled, this step: %s will the skipped' % self.step, out_log, self.global_log)
                return 0

        # copy inputs to container
        container_io_dict = fu.copy_to_container(self.container_path, self.container_volume_path, self.io_dict)

        # create unique name for temporary folder (created by acpype)
        self.unique_name = create_unique_name(6)

        # create command line instruction
        cmd = self.create_cmd(container_io_dict, out_log, err_log) 

        # execute cmd
        fu.log('Running %s, this execution can take a while' % self.acpype_path, out_log)
        cmd = fu.create_cmd_line(cmd, container_path=self.container_path, host_volume=container_io_dict.get("unique_dir"), container_volume=self.container_volume_path, user_uid=self.container_user_id, container_image=self.container_image, out_log=out_log, global_log=self.global_log)
        returncode = cmd_wrapper.CmdWrapper(cmd, out_log, err_log, self.global_log).launch()

        # move files to output_path and removes temporary folder
        if self.container_path:
            process_output_gmx(self.unique_name, container_io_dict['unique_dir'], self.remove_tmp, self.basename, get_default_value(self.__class__.__name__), self.output_files, out_log)
        else:
            process_output_gmx(self.unique_name, self.basename + "." + self.unique_name + ".acpype", self.remove_tmp, self.basename, get_default_value(self.__class__.__name__), self.output_files, out_log)

        # create command line instruction
        """cmd = self.create_cmd(out_log, err_log) 

        # execute cmd
        fu.log('Running %s, this execution can take a while' % self.acpype_path, out_log)
        returncode = cmd_wrapper.CmdWrapper(cmd, out_log, err_log, self.global_log).launch()
        # move files to output_path and removes temporary folder
        process_output_gmx(self.unique_name, self.basename + "." + self.unique_name + ".acpype", self.remove_tmp, self.basename, get_default_value(self.__class__.__name__), self.output_files, out_log)"""

        return returncode

def main():
    parser = argparse.ArgumentParser(description="Small molecule parameterization for OPLS/AA MD package.", formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')
    parser.add_argument('--system', required=False, help="Check 'https://biobb-common.readthedocs.io/en/latest/system_step.html' for help")
    parser.add_argument('--step', required=False, help="Check 'https://biobb-common.readthedocs.io/en/latest/system_step.html' for help")

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_path', required=True, help='Path to the input file. Accepted formats: pdb, mdl, mol2.')
    required_args.add_argument('--output_path_itp', required=True, help='Path to the ITP output file. Accepted formats: itp.')
    required_args.add_argument('--output_path_top', required=True, help='Path to the TOP output file. Accepted formats: top.')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config, system=args.system).get_prop_dic()
    if args.step:
        properties = properties[args.step]

    # Specific call of each building block
    AcpypeParamsGMXOPLS(input_path=args.input_path, output_path_itp=args.output_path_itp, output_path_top=args.output_path_top, properties=properties).launch()

if __name__ == '__main__':
    main()
