import sys
from test import assert_true 
from test import assert_false
from test import assert_equal

sys.path.insert(1, '../utils')

from finite_automata import FiniteAutomata
from finite_automata import AFTransition
from automata import State

def test_deterministic_af():
	# L = {w ∈ {a, b, c}* e todos os a's etejam em posições pares de w}
	q0 = State('q0')
	q1 = State('q1')
	q2 = State('q2')
	af = FiniteAutomata()
	
	af.declare_state(q0)
	af.declare_state(q1)
	af.declare_state(q2)

	af.set_initial_state(q0)
	
	af.set_final_state(q0)
	af.set_final_state(q2)

	af.declare_transition(AFTransition(from_ = q0, to = q1, char = 'a'))
	af.declare_transition(AFTransition(from_ = q0, to = q2, char = 'b'))
	af.declare_transition(AFTransition(from_ = q0, to = q2, char = 'c'))

	af.declare_transition(AFTransition(from_ = q2, to = q0, char = 'a'))
	af.declare_transition(AFTransition(from_ = q2, to = q0, char = 'b'))
	af.declare_transition(AFTransition(from_ = q2, to = q0, char = 'c'))

	af.declare_transition(AFTransition(from_ = q1, to = q1, char = 'a'))
	af.declare_transition(AFTransition(from_ = q1, to = q1, char = 'b'))
	af.declare_transition(AFTransition(from_ = q1, to = q1, char = 'c'))

	assert_true(af.run('cabbba'))
	assert_true(af.run('bcccc'))
	assert_true(af.run('bccaca'))
	assert_true(af.run('bbbbbbba'))

	assert_false(af.run('a'))
	assert_false(af.run('cccca'))
	assert_false(af.run('bbabbb'))
	assert_false(af.run('bccbcca'))

	assert_true(af.is_deterministic())

def test_non_deterministic_af():
	# L = {w | w {a, b}* e #ab é igual a quantidade de #ba}
	# Descreveremos L*

	q0 = State('q0')
	q1 = State('q1')
	q2 = State('q2')
	q3 = State('q3')
	q4 = State('q4')

	af = FiniteAutomata()

	af.declare_transition(AFTransition(from_ = q0, to = q1, char = 'a')) 
	af.declare_transition(AFTransition(from_ = q0, to = q3, char = 'b'))

	af.declare_transition(AFTransition(from_ = q1, to = q1, char = 'a'))
	af.declare_transition(AFTransition(from_ = q1, to = q2, char = 'b'))

	af.declare_transition(AFTransition(from_ = q2, to = q1, char = 'a'))
	af.declare_transition(AFTransition(from_ = q2, to = q2, char = 'b'))

	af.declare_transition(AFTransition(from_ = q3, to = q4, char = 'a'))
	af.declare_transition(AFTransition(from_ = q3, to = q3, char = 'b'))

	af.declare_transition(AFTransition(from_ = q4, to = q4, char = 'a'))
	af.declare_transition(AFTransition(from_ = q4, to = q3, char = 'b'))

	af.set_final_state(q0)
	af.set_final_state(q1)
	af.set_final_state(q3)

	i = State('i')
	af.declare_transition(AFTransition(from_ = i, to = q0))
	for fstate in af.final_states:
		af.declare_transition(AFTransition(from_ = fstate, to = i))

	af.set_final_state(i)
	af.set_initial_state(i)

	assert_true(af.run('aba'))
	assert_true(af.run('bbbab'))
	assert_true(af.run('aaabaaba'))
	assert_true(af.run('bbbababab'))
	
	assert_true(af.run('abaaba'))
	assert_true(af.run('bbbabbbbab'))
	assert_true(af.run('aaabaabaaaabaaba'))
	assert_true(af.run('bbbabababbbbababab'))

	assert_false(af.run('abab'))
	assert_false(af.run('baba'))
	assert_false(af.run('bbabba'))
	assert_false(af.run('bbbbbba'))

	assert_false(af.run('abaabab'))
	assert_false(af.run('bbbabbaba'))
	assert_false(af.run('bbbabbbabba'))
	assert_false(af.run('bbbabbbbbbba'))

	assert_false(af.is_deterministic())

if __name__ == "__main__":
    test_deterministic_af()
    test_non_deterministic_af()
    print("Everything passed")