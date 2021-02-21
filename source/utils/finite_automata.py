from abc import ABCMeta, abstractmethod
from automata import Automata
from automata import Transition
from automata import AutomataState
from automata import FINITE_AUTOMATA

class FiniteAutomata(Automata):

	def __init__(self):
		super().__init__()
		self.type = FINITE_AUTOMATA 

	def apply_curr_state(self, automata_state):
		self.at = automata_state.at
		self.pointer = automata_state.pointer

	def create_curr_state(self):
		automata_state = AutomataState()
		automata_state.at = self.at
		automata_state.pointer = self.pointer
		return automata_state

	def accept(self):
		reed_word = self.pointer == len(self.word)
		is_final_state = self.at in self.final_states
		return reed_word and is_final_state

class AFTransition(Transition):

	def __init__(self, from_, to, char = Transition.EPSILON):
		super().__init__(from_, to, char)
		self.type = FINITE_AUTOMATA 
		
	def is_respected(self, af_automata):
		p = af_automata.pointer
		c = af_automata.word[p]
		return self.from_ == af_automata.at \
			and (self.char == c or self.char == Transition.EPSILON)
	
	def transit(self, af_automata):
		af_automata.at = self.to
		if self.char != Transition.EPSILON:
			af_automata.pointer += 1