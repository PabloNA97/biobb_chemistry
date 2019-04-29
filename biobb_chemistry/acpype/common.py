""" Common functions for package biobb_chemistry.acpype """
import os.path
import re
from biobb_common.tools import file_utils as fu

def check_input_path(path):
	""" Checks input file """ 
	if not os.path.exists(path):
		raise SystemExit('Unexisting input file')
	filename, file_extension = os.path.splitext(path)
	if not is_valid_input(file_extension[1:]):
		raise SystemExit('Format %s in input file is not compatible' % file_extension[1:])
	return path

def check_output_path(path):
	""" Checks output path """ 
	if not os.path.exists(path):
		raise SystemExit('Unexisting output folder')
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
	if ch == '':
		fu.log('No charge provided, default value %s assigned' % get_default_value('charge'), out_log)
		ch = get_default_value('charge')

	if not isinstance(ch, int):
		fu.log('Value %s is not compatible as a charge value, default value %d assigned' % (ch, get_default_value('charge')), out_log)
		ch = get_default_value('charge')

	return str(ch)

def get_default_value(key):
	""" Gives default values according to the given key """
	default_values = {
		"charge": 0,
		"basename": "BBB",
		"acpype_path": "acpype"
	}

	return default_values[key]

def is_valid_input(ext):
	""" Checks if input file format is compatible with Acpype """
	formats = ["pdb", "mdl", "mol2"]
	return ext in formats