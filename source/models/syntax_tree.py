from abc import ABCMeta, abstractmethod

import models.re_utils as re

class Tree:
	"""
		Estrutura que armazena informações sobre a árvore completa.
		A função principal é encontrar nodos específicos a partir de
		seu id.
	"""
	def __init__(self):
		self.node_from_id = {}
		self.root = None

	# Retorna o alfabeto na linguagem
	def get_alphabet(self):
		alph = set()
		def add_symbol_to_alph(set_, node):
			symbol = node.get_symbol()
			if re.is_operand(symbol) and symbol != '&' and symbol != '#':
				set_.add(symbol)
		root = self.get_root()
		root.recursive_call(lambda x: add_symbol_to_alph(alph, x))
		return alph

	def map_id(self, node, id_):
		self.node_from_id[id_] = node

	def get_node(self, id_):
		return self.node_from_id[id_]

	def has_root(self):
		return self.root is not None

	def set_root(self, root):
		self.root = root

	def get_root(self):
		return self.root

class TreeNode():
	"""
		Nodo da árvore, armazena informações sobre nodo pai,
		filho a esquerda e filho a direita.
		Atualmente lida principalmente com syntaxes em que nodos possuem 
		no máximo dois filhos
	"""
	def __init__(self, symbol, tree, id_ = -1):
		self.symbol = symbol
		self.id_ = id_
		self.left = None
		self.right = None
		self.father = None
		self.tree = tree
		self.tree.map_id(self, self.id_)

		self.nullable = None
		self.last_pos = None
		self.first_pos = None
		self.follow_pos = set()

	def get_symbol(self):
		return self.symbol

	# Insere um elemento filho a esquerda
	def insert_left(self, node):
		self.left = node
		node.father = self

	# Insere um elemento filho a direita
	def insert_right(self, node):
		self.right = node
		node.father = self

	# Retorna se existe um elemento filho a esquerda
	def has_left(self):
		return self.left != None

	# Retorna se existe um elemento filho a direita
	def has_right(self):
		return self.right != None

	# Função para calcular a 'primeira_pos' segundo o algoritmo de Aho
	def __calculate_first_pos(self):
		"""
			"If n is epsilon-node, then last_pos(n) is empty set"
		"""
		if self.symbol == '&':
			return set()

		"""
			"If n is a leaf labeled with position i, then first_pos(n) is {i}"
		"""
		if re.is_operand(self.symbol):
			return {self.id_}

		"""
			"If n is an union node with left child c1 and right child c2, 
			then first_pos(n) is first_pos(c1) U first_pos(c2)"
		"""
		if self.symbol == '+':
			return self.left.get_first_pos().union(self.right.get_first_pos())

		"""
			"If n is a cat-node with left child c1 and right child c2:

			if nullable(c1), then 
				first_pos(n) is first_pos(c1) U first_pos(c2),
			else, 
				first_pos(n) is first_pos(c1)
			"
		"""
		if self.symbol == '.':
			if self.left.get_nullable():
				return self.left.get_first_pos().union(self.right.get_first_pos())
			else:
				return self.left.get_first_pos()

		"""
			"If n is a star-node with child c1, then first_pos(n) is first_pos(c1)"
		"""
		if self.symbol == '*':
			return self.left.get_first_pos()

	# Função para calcular a 'last_pos' segundo o algoritmo de Aho
	def __calculate_last_pos(self):
		"""
			"If n is epsilon-node, then last_pos(n) is empty set"
		"""
		if self.symbol == '&':
			return set()

		"""
			"If n is a leaf-node labeled with position i, then last_pos(n) is {i}"
		"""
		if re.is_operand(self.symbol):
			return {self.id_}

		"""
			"If n is an union node with left child c1 and right child c2, 
			then last_pos(n) is last_pos(c1) U last_pos(c2)"
		"""
		if self.symbol == '+':
			return self.right.get_last_pos().union(self.left.get_last_pos())

		"""
			"If n is a cat-node with left child c1 and right child c2:

			if nullable(c2), then 
				last_pos(n) is last_pos(c1) U last_pos(c2),
			else, 
				last_pos(n) is last_pos(c2)
			"
		"""
		if self.symbol == '.':
			if self.right.get_nullable():
				return self.left.get_last_pos().union(self.right.get_last_pos())
			else:
				return self.right.get_last_pos()

		"""
			"If n is a star-node with child c1, then last_pos(n) is last_pos(c1)"
		"""
		if self.symbol == '*':
			return self.left.get_last_pos()

	# Função para calcular o 'nullable' segundo o algoritmo de Aho
	def __calculate_nullable(self):
		"""
			"If n is a leaf-node labeled epsilon, then nullable(n) is True"
		"""
		if self.symbol == '&':
			return True

		"""
			"If n is a leaf-node labeled with position i, then nullable(n) is False"
		"""
		if re.is_operand(self.symbol):
			return False

		"""
			"If n is an union node with left child c1 and right child c2, 
			then nullable(n) is nullable(c1) or nullable(c2)"
		"""
		if self.symbol == '+':
			return self.left.__calculate_nullable() or self.right.__calculate_nullable()
		
		"""
			"If n is a cat-node with left child c1 and right child c2,
			then nullable(n) is nullable(c1) and nullable(c2)"
		"""
		if self.symbol == '.':
			return self.left.__calculate_nullable() and self.right.__calculate_nullable()
		
		"""
			"If n is a star-node, then nullable(n) is True"
		"""
		if self.symbol == '*':
			return True

		return False

	def get_first_pos(self):
		if not self.first_pos:
			self.first_pos = self.__calculate_first_pos()
		return self.first_pos

	def get_last_pos(self):
		if not self.last_pos:
			self.last_pos = self.__calculate_last_pos()
		return self.last_pos

	def get_nullable(self):
		if not self.nullable:
			self.nullable = self.__calculate_nullable()
		return self.nullable

	def get_follow_pos(self):
		return self.follow_pos

	# Recebe uma função como parâmetro e aplica-a à todos os nodos recursivamente 
	def recursive_call(self, function):
		if self.left:
			self.left.recursive_call(function)
		function(self)
		if self.right:
			self.right.recursive_call(function)

	def debug_(self):
		if self.left:
			print('left:')
			self.left.debug_()
		print(self.symbol, self.get_first_pos(), self.get_last_pos(), self.get_follow_pos())
		if self.right:
			print('right:')
			self.right.debug_()
		print('out!')

	# insere uma sequência de IDs ao conjunto 'follow_pos' de um nodo
	def __append_follow_pos(self, positions):
		for pos in positions:
			self.follow_pos.add(pos)

	"""
		Função para calcular o 'follow_pos' segundo o algoritmo de Aho.
		"for finding followpos only star(*) and concat(.) nodes will
		 be considered"		
	"""
	def calculate_follow_pos(self):
		"""
			"if n is a star-node, and i is a position in lastpos(n),
			 then all positions in firstpos(n) are in followpos(i)"
		"""
		if self.symbol == '*':
			first_pos =  self.get_first_pos()
			last_pos = self.get_last_pos()
			for i in last_pos:
				self.tree.get_node(i).__append_follow_pos(first_pos)

		"""
			"if n is concatenation-node with left child c1 and right child c2,
			 and i is a position in lastpos(c1), then all positions in firstpos(c2)
			 are in followpos(i)"		
		"""
		if self.symbol == '.':
			last_pos_c1 = self.left.get_last_pos()
			first_pos_c2 = self.right.get_first_pos()
			for i in last_pos_c1:
				self.tree.get_node(i).__append_follow_pos(first_pos_c2)
