"""
    State class
    Represents a state, with id name and if its final;
    Stores references for each of its possible next States;
"""
class State:
    def __init__(self, id, name, final):
        #this state id
        self.id = id
        #name 
        self.name = name
        #map of symbol to next state
        self.transition = {}
        #final flag
        self.final = final

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
