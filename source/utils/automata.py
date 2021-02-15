from abc import ABCMeta, abstractmethod
from queue import Queue

FINITE_AUTOMATA = 0
PUSH_DOWN_AUTOMATA = 1
LINEAR_BOUNDED_AUTOMATA = 2

class AutomataException(Exception):
	pass

class Automata:

	__OVERFLOW_SIZE = 10000

	__metaclass__ = ABCMeta

	def __init__(self):
		self.states = set()
		self.transitions = set()
		self.adjacent = {}
		self.r_adjacent = {}
		
		self.initial_state = None
		self.final_states = set()

	def set_initial_state(self, state):
		if state not in self.states:
			raise AutomataException('')
		self.initial_state = state

	def set_final_state(self, state):
		if state not in self.states:
			raise AutomataException('')
		self.final_states.add(state)

	def declare_state(self, state):
		if state in self.states:
			raise AutomataException('State already exist')
		self.states.add(state)

	def has_state(self, state):
		return state in self.states
	
	def insert_adjacent(self, state, transition):
		char = transition.char
		if state not in self.adjacent:
			self.adjacent[state] = {}
		if char not in self.adjacent[state]:
			self.adjacent[state][char] = []
		self.adjacent[state][char].append(transition)
	
	def get_adjacents(self, char, state):
		if state not in self.adjacent:
			self.adjacent[state] = {}
		if char not in self.adjacent[state]:
			self.adjacent[state][char] = []
		return self.adjacent[state][char]
	
	def get_all_adjacents(self, state):
		if state not in self.adjacent:
			self.adjacent[state] = {}
		return self.adjacent[state]

	def insert_r_adjacent(self, state, transition):
		char = transition.char
		if state not in self.r_adjacent:
			self.r_adjacent[state] = {}
		if char not in self.r_adjacent[state]:
			self.r_adjacent[state][char] = []
		self.r_adjacent[state][char].append(transition)
	
	def get_r_adjacents(self, char, state):
		if state not in self.r_adjacent:
			self.r_adjacent[state] = {}
		if char not in self.r_adjacent[state]:
			self.r_adjacent[state][char] = []
		return self.r_adjacent[state][char]

	def get_all_r_adjacents(self, state):
		if state not in self.r_adjacent:
			self.r_adjacent[state] = {}
		return self.r_adjacent[state]

	def declare_transition(self, transition):
		if self.type != transition.type:
			raise AutomataException('Transition and automata type missmatch')
		
		s1 = transition.from_
		s2 = transition.to
		if not self.has_state(s1):
			self.declare_state(s1)
		if not self.has_state(s2):
			self.declare_state(s2)
		
		self.transitions.add(transition)
		self.insert_adjacent(s1, transition)
		self.insert_r_adjacent(s2, transition)
	
	def run(self, word):
		self.queue = Queue(maxsize = Automata.__OVERFLOW_SIZE)
		self.word = word
		self.pointer = 0
		self.at = self.initial_state
		self.queue_current_state()
		self.accepted = False

		while not self.accepted and not self.queue.empty():
			self.dequeue_state()

			p = self.pointer
			if p == len(self.word):
				break
			adj = self.get_adjacents(self.word[p], self.at) \
				+ self.get_adjacents(Transition.EPSILON, self.at)

			curr_state = self.create_curr_state()
			for transition in adj:
				if transition.is_respected(self):
					transition.transit(self)

					if self.accept():
						self.accepted = True
						break

					self.queue_current_state()
					self.apply_curr_state(curr_state)

		return self.accepted

	@abstractmethod
	def accept(self):
		pass

	@abstractmethod
	def apply_curr_state(self, automata_state):
		pass

	@abstractmethod
	def create_curr_state(self):
		pass

	def queue_current_state(self):
		if self.queue.qsize() == self.queue.maxsize:
			raise AutomataException()
		automata_state = self.create_curr_state()
		self.queue.put(automata_state)

	def dequeue_state(self):
		automata_state = self.queue.get()
		self.apply_curr_state(automata_state)

	def is_deterministic(self):
		# Iterate over all states
		for state in self.states:
			keys = self.get_all_adjacents(state)
			# Iterate over all alphabet chars that generate transitions
			for key in keys:
				transitions = self.get_adjacents(key, state)
				#     /-a-|q1|
				# |q0|--&-|q2| alfa has many transitions or alfa is EPSILON?
				#     \-a-|q3|
				if len(transitions) > 1 or transitions and key == Transition.EPSILON:
					return False
		return True

class State:

	def __init__(self, state_name, state_description = ''):
		self.name = state_name
		self.description = state_description
		
class Transition:

	EPSILON = '&'

	__metaclass__ = ABCMeta

	def __init__(self, from_, to, char):
		self.from_ = from_
		self.to = to
		self.char = char 

	# Returns if transition rules are respected
	# # PDA will check char at the top of stack, etc.
	@abstractmethod
	def is_respected(self, automata):
		pass

	# Operates acordintly to each automata
	# # TM have to move head to the left or right, etc.
	@abstractmethod
	def transit(self, automata):
		pass

class AutomataState:

	def __init__(self):
		pass