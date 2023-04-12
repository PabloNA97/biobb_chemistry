""" Common functions for package biobb_chemistry.acpype """
from pathlib import Path, PurePath
import glob
import shutil
import string
import random
import fileinput
from biobb_common.tools import file_utils as fu


def check_input_path(path, out_log, classname):
    """ Checks input file """
    if not Path(path).exists():
        fu.log(classname + ': Unexisting input file, exiting', out_log)
        raise SystemExit(classname + ': Unexisting input file')
    file_extension = PurePath(path).suffix
    if not is_valid_input(file_extension[1:]):
        fu.log(classname + ': Format %s in input file is not compatible' % file_extension[1:], out_log)
        raise SystemExit(classname + ': Format %s in input file is not compatible' % file_extension[1:])
    if (PurePath(path).name == path or not PurePath(path).is_absolute()):
        path = str(PurePath(Path.cwd()).joinpath(path))

    return path


def check_output_path(path, type, out_log, classname):
    """ Checks output path """
    if PurePath(path).parent and not Path(PurePath(path).parent).exists():
        fu.log(classname + ': Unexisting output %s output folder, exiting' % type, out_log)
        raise SystemExit(classname + ': Unexisting %s output folder' % type)
    file_extension = PurePath(path).suffix
    if type != file_extension[1:]:
        fu.log(classname + ': Format %s in %s input file is not compatible' % (file_extension[1:], type), out_log)
        raise SystemExit(classname + ': Format %s in %s input file is not compatible' % (file_extension[1:], type))

    return path


def get_binary_path(properties, type):
    """ Gets binary path """
    return properties.get(type, get_default_value(type))


def get_basename(basename, out_log):
    """ Checks if provided basename value is correct """
    bsn = str(basename)
    if basename == '':
        fu.log('No basename provided, default value %s assigned' % get_default_value('basename'), out_log)
        bsn = get_default_value('basename')

    return bsn


def get_charge(charge, out_log):
    """ Checks if provided charge value is correct """
    ch = charge
    if ch is None or ch == '':
        fu.log('Charge will be guessed by acpype.', out_log)
        return ch

    if not isinstance(ch, (int, None)):
        fu.log('Value %s is not compatible as a charge value, default value %d assigned' % (ch, get_default_value('charge')), out_log)
        ch = get_default_value('charge')

    return str(ch)


def create_unique_name(length=10, char=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return ''.join(random.choice(char) for x in range(length))


def get_default_value(key):
    """ Gives default values according to the given key """
    default_values = {
        "charge": 0,
        "basename": "BBB",
        "binary_path": "acpype",
        "AcpypeParamsGMX": {
            "topology": "GROMACS",
            "suffix": "_GMX."
        },
        "AcpypeParamsAC": {
            "topology": "Antechamber",
            "suffix": "_AC."
        },
        "AcpypeParamsGMXOPLS": {
            "topology": "OPLS/AA",
            "suffix": "_GMX_OPLS."
        },
        "AcpypeParamsCNS": {
            "topology": "GROMACS",
            "suffix": "_CNS."
        }
    }

    return default_values[key]


def is_valid_input(ext):
    """ Checks if input file format is compatible with Acpype """
    formats = ["pdb", "mdl", "mol2"]

    return ext in formats


def process_output(unique_name, files_folder, remove_tmp, basename, class_params, output_files, out_log):
    """ Moves and removes temporal files generated by the wrapper """
    path = files_folder
    suffix = class_params['suffix']
    src_files = glob.glob(path + '/' + basename + '.' + unique_name + suffix + '*')

    # copy files for the requested topology to the output_path
    for file_name in src_files:
        # replace random name by original name in all files
        with fileinput.FileInput(file_name, inplace=True) as file:
            for line in file:
                print(line.replace(basename + '.' + unique_name, basename), end='')

        if (Path(file_name).is_file()):
            file_extension = PurePath(file_name).suffix
            shutil.copy(file_name, output_files[file_extension[1:]])
            fu.log('File %s succesfully created' % output_files[file_extension[1:]], out_log)

    if remove_tmp:
        # remove temporary folder
        fu.rm(files_folder)
        fu.log('Removed temporary folder: %s' % files_folder, out_log)


def process_output_gmx(unique_name, files_folder, remove_tmp, basename, class_params, output_files, out_log):
    """ Moves and removes temporal files generated by the wrapper """
    path = files_folder
    suffix = class_params['suffix']
    src_files = glob.glob(path + '/' + basename + '.' + unique_name + suffix + '*')

    # copy files for the requested topology to the output_path
    for file_name in src_files:
        # replace random name by original name in all files
        with fileinput.FileInput(file_name, inplace=True) as file:
            for line in file:
                print(line.replace(basename + '.' + unique_name, basename), end='')

        if (Path(file_name).is_file()):
            file_extension = PurePath(file_name).suffix
            # in top files for gromacs, replace file.itp by name given by user
            if (file_extension[1:] == 'top'):
                with open(file_name) as f:
                    newText = f.read().replace(basename + '_GMX.itp', PurePath(output_files['itp']).name)
                with open(file_name, "w") as f:
                    f.write(newText)
            shutil.copy(file_name, output_files[file_extension[1:]])
            fu.log('File %s succesfully created' % output_files[file_extension[1:]], out_log)

    if remove_tmp:
        # remove temporary folder
        fu.rm(files_folder)
        fu.log('Removed temporary folder: %s' % files_folder, out_log)
