import sys

from test import assert_true 
from test import assert_false
from test import assert_equal

sys.path.insert(1, '../utils')

import regex

def test_import_and_export_file():
	f = open('resources/regex.jff', 'r')
	file = f.read()
	f.close()

	regex_instance = regex.from_file(file)
	new_file = regex_instance.to_file()
	
	# Remove white spaces
	file = file.replace(' ', '')
	new_file = new_file.replace(' ', '')
	# Remove line breaks
	file = file.replace('\n', '')
	new_file = new_file.replace('\n', '')
	# Remove tabs
	file = file.replace('\t', '')
	new_file = new_file.replace('\t', '')

	assert_equal(file, new_file)
	

def test_import_and_export_json():
	f = open('resources/regex.json', 'r')
	file = f.read()
	f.close()

	regex_instance = regex.from_json(file)
	new_file = regex_instance.to_json()

	# Remove white spaces
	file = file.replace(' ', '')
	new_file = new_file.replace(' ', '')
	# Remove line breaks
	file = file.replace('\n', '')
	new_file = new_file.replace('\n', '')
	# Remove tabs
	file = file.replace('\t', '')
	new_file = new_file.replace('\t', '')
	# Replace double quotes for single quotes
	file = file.replace('\'', '\"')
	new_file = new_file.replace('\'', '\"')

	assert_equal(file, new_file)

if __name__ == "__main__":
    test_import_and_export_file()
    test_import_and_export_json()
    print("Everything passed")