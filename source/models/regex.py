from xml.dom import minidom
import xml.dom.minidom
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
import json

def from_file(path):
	data = open(path, "r").read()
	xml = minidom.parseString(data)
	expression_node = xml.getElementsByTagName('expression')[0];
	expression = expression_node.childNodes[0].nodeValue;
	expression_dict = {Regex.DEFAULT_MAIN_EXP : expression}
	regex = RegexBuilder(expression_dict).build()
	return regex

def from_json(data):
	json_data = json.loads(data)
	regex = RegexBuilder(json_data['expressions']).build()
	return regex

class Regex:
	DEFAULT_MAIN_EXP = 'S'

	def __init__(self, expression_str_dict, main_exp = DEFAULT_MAIN_EXP):
		self.exp_to_str = expression_str_dict
		self.main_exp = main_exp
		self.dependencies = {}
		self.unsolved_dependencies = {}

	def declare_dependency(self, var, dep):
		if var not in self.dependencies:
			self.dependencies[var] = set()
			self.unsolved_dependencies = set()
		self.dependencies[var].add(dep)
		self.unsolved_dependencies[var].add(dep)

	def solve_dependency(self, var, dep):
		if var not in self.unsolved_dependencies:
			#raise exception
			pass
		self.unsolved_dependencies[var].remove(dep)

	def to_file(self, path):
		exp_var = self.main_exp
		exp_str = self.get_expression_str(exp_var)
		dependencies = self.get_dependencies(exp_var)
		for dependency in dependencies:
			d_exp = self.get_expression_str(dependency)
			exp_str = exp_str.replace(dependency, d_exp)
		structure = ET.Element('structure');
		type_ = ET.SubElement(structure, 'type')
		type_.text = 're'
		expression = ET.SubElement(structure, 'expression')
		expression.text = exp_str
		xmlstr = ET.tostring(structure, encoding='unicode', method='xml')
		with open(path, "w") as f:
			f.write(xmlstr)

	def get_dependencies(self, var):
		if var in self.dependencies:
			return self.dependencies[var]
		return set()

	def get_expression_str(self, var):
		if var in self.exp_to_str:
			return self.exp_to_str[var]
		return ""

	def get_vars(self):
		return self.exp.keys()

	def get_expression(self, var):
		if var in self.exp:
			return self.exp[var]
		return None

	def __get_exp_to_str_dict(self):
		return self.exp_to_str

	def to_json(self):
		expressions = '{\n\t\"expressions\" : \n'
		expressions += json.dumps(self.__get_exp_to_str_dict())
		expressions += "\n}"
		return expressions

class RegexBuilder:

	def __init__(self, expression_str_dict):
		self.regex = Regex(expression_str_dict)

	def build(self):
		# TODO
		return self.regex