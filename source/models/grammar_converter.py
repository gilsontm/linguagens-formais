from models.finite_automata import FiniteAutomata
from models.grammar import Grammar


class GrammarConverter:

    def __init__(self):
        self.grammar = {}
        self.automata = {}
        self.final_name = "F*"
        self.empty_derivation = "&"
        self.initial_name = "S"

    """
    Coverts a regular grammar into a finite state automata.
    """
    def grammar_to_automata(self, grammar):
        self.grammar = grammar
        automata = FiniteAutomata()

        grammar_variables = grammar.get_variables()

        # Creates new final state and adds it to automata's final states list
        automata.add_final_state(automata.add_state(self.final_name))

        # Creates initial state
        initial_state = automata.add_state(self.initial_name)
        automata.set_initial_state(initial_state)

        for state_name in grammar_variables:
            if automata.get_state_by_name(state_name) is None:
                automata.add_state(state_name)

            derivations = grammar.get_derivations(state_name)

            for derivation in derivations:
                if derivation == self.empty_derivation:
                    automata.add_final_state(automata.get_state_by_name(state_name))
                else:
                    trans_symbol = derivation[0]
                    trans_state = derivation[-1]  # Just so we don't go out of bounds
                    from_state = automata.get_state_by_name(state_name)

                    if trans_state == trans_symbol:
                        final_state = automata.get_state_by_name(self.final_name)
                        automata.add_transition(trans_symbol, from_state, final_state)
                    else:
                        if automata.get_state_by_name(trans_state) is None:
                            automata.add_state(trans_state)
                        to_state = automata.get_state_by_name(trans_state)
                        automata.add_transition(trans_symbol, from_state, to_state)

        self.automata = automata
        return automata

    """
    Coverts a deterministic finite state automata into a regular grammar.
    """
    def automata_to_grammar(self, automata):
        grammar = Grammar()

        states = automata.states
        # Get states id's
        states_id = states.keys()

        final_states_id = automata.final_ids
        initial_state_id = automata.initial_id

        # Force the initial state to be S
        states[initial_state_id].name = self.initial_name

        for state_id in states_id:
            state = states[state_id]
            transitions = state.transition
            transitions_symbols = list(state.transition.keys())

            grammar.add_key(state.name, list())
            for symbol in transitions_symbols:
                # gets states in which you transition into from symbol
                transition_states = transitions[symbol]
                for s in transition_states:
                    if s.id in final_states_id:
                        grammar.add_derivation(state.name, symbol)
                    grammar.add_derivation(state.name, symbol + s.name)

        self.grammar = grammar
        return grammar
