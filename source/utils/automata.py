from abc import ABCMeta, abstractmethod
from queue import Queue

__FINITE_AUTOMATA = 0
__PUSH_DOWN_AUTOMATA = 1
__LINEAR_BOUNDED_AUTOMATA = 2

class AutomataException(Exception):
	pass

class Automata:

	__OVERFLOW_SIZE = 1000

	__metaclass__ = ABCMeta

	def __init__(self, initial_state):
		self.states = set()
		self.transitions = set()
		self.adjacent = {}
		self.r_adjacent = {}
		
		self.initial_state = initial_state
		self.final_states = set()

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
		if transition is not Transition or self.type != transition.type:
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
			adj = self.get_adjacents(self.word[p], self.at)
			curr_state = self.create_curr_state()
			for transition in adj:
				if transition.is_respected(self):
					transition.transit(self)
					self.queue_current_state()
					self.apply_curr_state(curr_state)

		return self.accepted

	@abstractmethod
	def apply_curr_state(self, automata_state):
		pass

	@abstractmethod
	def create_curr_state(self):
		pass

	def queue_current_state(self):
		automata_state = self.create_curr_state()
		self.queue.put(automata_state)

	def dequeue_state(self):
		automata_state = self.queue.get()
		apply_curr_state(automata_state)

	def is_deterministic(self):
		# Iterate over all states
		for state in self.states:
			keys = self.get_all_adjacents(state)
			# Iterate over all alphabet chars that generate transitions
			for key in keys:
				key_transitions = self.get_adjacents(key, state)
				# Iterate over all transitions of that alphabet char
				for transitions in key_transitions:
					#     /-a-|q1|
					# |q0|--&-|q2| alfa has many transitions or alfa is EPSILON?
					#     \-a-|q3|
					if len(transitions) > 1 or key == Transition.EPSILON:
						return False
		return True

class State:

	def __init__(self, state_name):
		self.name = state_name
		self.description = ''

	def __init__(self, state_name, state_description):
		self.name = state_name
		self.description = state_description
		
class Transition:

	EPSILON = '&'
	
	__metaclass__ = ABCMeta

	def __init__(self, char):
		self.from_ = None
		self.to = None
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