"""
    State class
    Represents a state, with id name and its transitions;
    Stores references for each of its possible next States;
"""
class State:
    def __init__(self, id, name):
        #this state id
        self.id = id
        #name
        self.name = name
        #map of symbol to next state
        self.transition = {}

    """
        Adds a transition to a given State and symbol
        The State is stored in transitions dict with
        symbol as index;
        Each index is a list of States;
    """
    def add_transition(self, symbol, state):
        if not (symbol in self.transition):
            self.transition[symbol] = []
        self.transition[symbol].append(state)

    """
        Removes all transitions to a given state
    """
    def remove_transitions_to(self, state_id):
        for key in self.transition:
            self.transition[key] = [state for state in self.transition[key] if state.id != state_id]

    """
        Checks if state has at least one transition to another given state
    """
    def has_transition_to_state(self, state_id):
        for transitions in self.transition.values():
            for state in transitions:
                if state.id == state_id:
                    return True
        return False

    """
        Checks if state has a transition to another state by a given symbol
    """
    def has_transition_to_state_by_symbol(self, state_id, symbol):
        if symbol in self.transition:
            for state in self.transition[symbol]:
                if state.id == state_id:
                    return True
        return False

    """
        Returns name of state
    """
    def get_name(self):
        return self.name