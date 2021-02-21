class State:
    def __init__(self, id, name, final):
        #this state id
        self.id = id
        self.name = name
        #map of symbol to next state
        self.transition = {}
        self.final = final

    def add_transition(self, symbol, state):
        if not (symbol in self.transition):
            self.transition[symbol] = []
        self.transition[symbol].append(state)
