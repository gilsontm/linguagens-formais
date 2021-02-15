from abc import ABCMeta, abstractmethod
from automata import Automata
from automata import Transition
from automata import AutomataState

class FiniteAutomata(Automata):

	def __init__(self, initial_state):
		super().__init__(initial_state)
		self.type = automata.__FINITE_AUTOMATA 

	@abstractmethod
	def apply_curr_state(self, automata_state):
		self.at = automata_state.at
		self.pointer = automata_state.pointer

	@abstractmethod
	def create_curr_state(self):
		automata_state = AutomataState()
		automata_state.at = self.at
		automata_state.pointer = automata_state.pointer
		return automata_state

class AFTransition(Transition):

	def __init__(self, char):
		super().__init__(char)
		self.type = automata.__FINITE_AUTOMATA 
		
	def is_respected(self, af_automata):
		p = af_automata.pointer
		c = af_automata.word[p]
		return self.from_ == af_automata.at \
			and (self.char == c or self.char == Transition.EPSILON)
	
	def transit(self, af_automata):
		af_automata.at = self.to
		if self.char != Transition.EPSILON:
			af_automata.pointer += 1