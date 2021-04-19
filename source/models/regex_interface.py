from models.state import State
import models.regex_utils as re
from models.syntax_tree import Tree, TreeNode
from models.finite_automata import FiniteAutomata


class RegularExpressionInterface():

	def __init__(self):
		pass

	def parse_expression(self):
		pass

	# Função que retorna o peso do operador em uma expressão no formato infixa
	def __prec(self, c):
		if c == '*' or c == '?':
			return 3
		elif c == '.':
			return 2
		elif c == '+':
			return 1
		return -1

	"""
		Resolve o valor de caracteres especiais.
		Por exemplo, "\\s", não deve resultar no caractere 's', mas, em um espaço.
	"""
	def __resolve_char(self, ch):
		if ch == 's':
			return ' '
		return ch

	# Função adiciona operadores de concatenação, definidas por caracteres não espaçados na expressão
	def __insert_concatenation_operator(self, txt):
		opcnt = 0
		new_txt = ''

		length = len(txt)
		i = 0
		while i < length:
			ch = txt[i]
			i += 1
			if re.is_operand(ch) or ch == '\\' or ch == '#':
				opcnt += 1
				if ch == '\\':
					ch += txt[i]
					i += 1
				chrs = []
				while i < length and (re.is_operand(txt[i]) or txt[i] == '\\' or ch == '#'):
					chrs.append(ch)
					ch = txt[i]
					opcnt += 1
					i += 1
					if ch == '\\':
						ch += txt[i]
						i += 1
				chrs.append(ch)
				if len(chrs) == 1:
					new_txt += chrs[0]
				elif chrs:
					new_txt += '.'.join(chrs)
			else:
				if ch == '?':
					opcnt += 1
				new_txt += ch
		return new_txt, opcnt

	# Função, resolver extensão de ER, chaves.
	def __resolve_extension_brackets(self, exp):
		new_exp = ""
		length = len(exp)
		op_cnt = 0
		i = 0
		while i < length:
			ch = exp[i]
			i += 1

			if re.is_operand(ch) or ch == '?' or ch == '\\':
				op_cnt += 1

			if ch == '[':
				bracket = []
				while i < length:
					ch = exp[i]
					i += 1
					if ch == '\\':
						ch = exp[i]
						i += 1
					if ch == ']':
						break
					if ch == ' ':
						continue
					peek = exp[i]
					if i+2 < length and peek == '-':
						i += 1
						a = ord(ch)
						if exp[i] == '\\':
							i += 1
						b = ord(exp[i])
						if b >= a:
							for k in range(a, b+1):
								bracket.append(chr(k))
						i += 1
					else:
						bracket.append(ch)
				op_cnt += len(bracket)
				if len(bracket) != 0:
					new_exp += '(' + ' + '.join(bracket) + ')'
			else:
				if ch == '\\':
					ch += exp[i]
					i += 1
				new_exp += ch
		return new_exp, op_cnt

	"""
		Referência: https://www.geeksforgeeks.org/stack-set-2-infix-to-postfix/
		Algorithm
		1. Scan the infix expression from left to right.
		2. If the scanned character is an operand, output it.
		3. Else,
		      3.1 If the precedence of the scanned operator is greater than the precedence of the operator in the stack(or the stack is empty           or the stack contains a ‘(‘ ), push it.
		      3.2 Else, Pop all the operators from the stack which are greater than or equal to in precedence than that of the scanned operator. After doing that Push the scanned operator to the stack. (If you encounter parenthesis while popping then stop there and push the scanned operator in the stack.)
		4. If the scanned character is an ‘(‘, push it to the stack.
		5. If the scanned character is an ‘)’, pop the stack and and output it until a ‘(‘ is encountered, and discard both the parenthesis.
		6. Repeat steps 2-6 until infix expression is scanned.
		7. Print the output
		8. Pop and output from the stack until it is not empty.
	"""
	def __infix_to_postfix(self, txt):
		stack = []
		symbols = []

		length = len(txt)
		i = 0
		while i < length:
			ch = txt[i]
			i += 1
			if ch == ' ':
				continue
			# Se c for um caracter maiúsculo:
			if ch == '<':
				var = ''
				while i < length and txt[i] != '>':
					var += ch
					ch = txt[i]
					i += 1
				var += ch
				symbols.append(var)
			# Se c for um operando:
			elif re.is_operand(ch):
				symbols.append(ch)
			# Se c for um operando especial
			elif ch == '\\':
				ch += txt[i];
				i += 1
				symbols.append(ch)
			elif ch == '(':
				stack.append('(')
			elif ch == ')':
				while stack and stack[-1] != '(':
					c = stack.pop()
					if c == '?':
						symbols.append('&')
						c = '+'
					symbols.append(c)
				# Sempre será '(' se a expressão estiver correta
				if stack[-1] == '(':
					c = stack.pop()
			else:
				# É um operador
				while stack and self.__prec(ch) <= self.__prec(stack[-1]):
					c = stack.pop()
					if c == '?':
						symbols.append('&')
						c = '+'
					symbols.append(c)
				stack.append(ch)

		while stack:
			c = stack.pop()
			if c == '?':
				symbols.append('&')
				c = '+'
			symbols.append(c)
		return symbols

	"""
		Constrói uma árvore sintática a partir de uma expressão
		no formato postfix.
	"""
	def __postfix_to_syntax_tree(self, posfix, opcnt):
		tree = Tree()
		stack = []
		for ch in posfix:
			if ch == ',':
				ch = '.'
			if ch.startswith('\\'):
				ch = self.__resolve_char(ch[1])
				stack.append(TreeNode(symbol=ch, tree=tree, type_= Tree.OPERAND,id_=opcnt))
				opcnt -= 1
			elif re.is_operand(ch):
				stack.append(TreeNode(symbol=ch, tree=tree, type_= Tree.OPERAND, id_=opcnt))
				opcnt -= 1
			elif ch == '*':
				node = stack.pop()
				opnode = TreeNode(symbol=ch, tree=tree, type_= Tree.OPERATOR)
				opnode.insert_left(node)
				stack.append(opnode)
			else:
				node1 = stack.pop()
				node2 = stack.pop()
				opnode = TreeNode(symbol=ch, tree=tree, type_= Tree.OPERATOR)
				opnode.insert_left(node2)
				opnode.insert_right(node1)
				stack.append(opnode)
		if len(stack) != 1:
			return -1
		tree.set_root(stack[0])
		return tree

	def __state_string(self, positions):
		if len(positions) != 0:
			name = '[q' + ",q".join(str(i) for i in positions) + ']'
		else:
			name = ''
		return name

	def __positions_integer(self, name):
		if len(name) > 3:
			name = name[1:-1:]
			aux = name.replace('q', '')
			aux = aux.split(',')
			aux = [int(nstr) for nstr in aux]
			return aux
		return []

	"""
		Algoritmo de Aho, constrói-se uma AFD a partir de uma
		arvore sintática seus atributos (first_pos, last_pos, nullable, follow_pos)
	"""
	def __create_dfa(self, tree):
		root = tree.get_root()
		root.recursive_call(TreeNode.calculate_follow_pos)
		unmarked_states = set()
		states_d = set()
		dfa = FiniteAutomata()

		initial_state_name = self.__state_string(root.get_first_pos())
		state = dfa.add_state(name=initial_state_name)
		dfa.set_initial_state(state)
		p_list = self.__positions_integer(initial_state_name)
		final = not(all(tree.get_node(p).get_symbol() != '#' for p in p_list))
		if final:
			dfa.add_final_state(state)
		unmarked_states.add(state)
		states_d.add(initial_state_name)
		alphabet = tree.get_alphabet()

		while len(unmarked_states) != 0:
			state = unmarked_states.pop()
			name = state.get_name()
			p_list = self.__positions_integer(name)
			for a in alphabet:
				u = set()
				final = False
				for p in p_list:
					node = tree.get_node(p)
					if node.get_symbol() == a:
						follow_pos = node.get_follow_pos()
						u = u.union(follow_pos)
				u_name = self.__state_string(u)
				if len(u) != 0 and u_name not in states_d:
					final = not(all(tree.get_node(i).get_symbol() != '#' for i in u))
					new_state = dfa.add_state(u_name)
					unmarked_states.add(new_state)
					states_d.add(u_name)
					if final:
						dfa.add_final_state(new_state)
				elif len(u) == 0:
					continue;
				else:
					new_state = dfa.get_state_by_name(u_name)
				dfa.add_transition(symbol=a, from_state=state, to_state=new_state)
		return dfa

	def build_dfa(self, exp):
		exp = '(' + exp + ').#'
		# "__resolve_extension_brackets" deve ser resolvido antes de "__insert_extension_operator"
		exp, opcnt = self.__resolve_extension_brackets(exp)
		exp, opcnt = self.__insert_concatenation_operator(exp)
		postfix = self.__infix_to_postfix(exp)
		tree = self.__postfix_to_syntax_tree(postfix, opcnt)
		dfa = self.__create_dfa(tree)
		return dfa
