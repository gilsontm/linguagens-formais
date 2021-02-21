import json
from models.state import State


class FiniteAutomata:

    def __init__(self):
        #map of id to state
        self.states = {}
        #current state id
        self.curr_state_id = None
        #initial state id
        self.initial_id = None
        #finalstates state ids
        self.final_ids = []
        #input word
        self.word = None
        #current processing step
        self.step = 0

        self.json_automata = None

    def from_json(self, json_automata):
        self.json_automata = json_automata

        for state in self.json_automata['states']:
            self.states[state['id']] = State(state['id'], state['name'], state['final'])
            if (state['initial']):
                self.initial_id = state['id']
                self.curr_state_id = state['id']
            if (state['final']):
                self.final_ids.append(state['id'])

        for transition in self.json_automata['transitions']:
            symbols = transition['values']
            to_id = transition['to']
            to_state = self.states[to_id]
            from_id = transition['from']
            for symbol in symbols:
                self.states[from_id].add_transition(symbol, to_state)


    def valid(self):
        if ((not (self.curr_state_id in self.states)) or self.initial_id == None or len(self.states) == 0 or len(self.final_ids) == 0):
            return False
        return True

    def to_file(self, file_path):

        if (not self.valid()):
            return False

        transition_map = {}
        symbol_set = set()

        with open(file_path, "w") as f: 
            f.write(str(len(self.states))+ '\n')
            f.write(str(self.initial_id)+ '\n')
            for final_id in self.final_ids:
                f.write(str(final_id))
                if final_id != self.final_ids[-1]:
                    f.write(',')

            f.write('\n')

            self.to_json()
            for transition in self.json_automata['transitions']:
                for symbol in transition['values']:
                    symbol_set.add(symbol)
                    key = str(transition['from'])+","+symbol
                    if not(key in transition_map):
                        transition_map[key] = ""
                    transition_map[key] += str(transition['to'].id)+"-"

            symbol_set_string = ""
            for value in symbol_set:
                symbol_set_string+= value+","

            if symbol_set_string != "":
                f.write(symbol_set_string[:-1]+'\n')

            for key, value in transition_map.items():
                f.write(key+","+value[:-1]+'\n')
        return True

    def from_file(self, file_path):
        json_automata = {}
        with open(file_path) as f:
            lines = f.readlines()

            self.initial_id = int(lines[1])

            for final_state in lines[2].split(','):
                if(final_state != '\n'):
                    self.final_ids.append(int(final_state))

            for i in range(4,len(lines)):
                transition = lines[i].split(',')
                from_state = int(transition[0])
                if not (from_state in self.states):
                    self.states[from_state] = State(from_state, 'q'+str(from_state), (from_state in self.final_ids))
                symbol = transition[1]
                to_states = transition[2].split('-')
                for to_state in to_states:
                    to_state = int(to_state)
                    if not (to_state in self.states):
                        self.states[to_state] = State(to_state, 'q'+str(to_state), (to_state in self.final_ids))
                    self.states[from_state].add_transition(symbol, int(to_state))


    def to_json(self):
        transition_map = {}

        self.json_automata = {}
        self.json_automata['states'] = []
        self.json_automata['transitions'] = []
        for from_id, from_state in self.states.items():
            self.json_automata['states'].append({"id": from_state.id, "name": from_state.name, "final": (from_state.id in self.final_ids), "initial": (from_state.id == self.initial_id)})

            for symbol, to_states in from_state.transition.items():
                for to_id in to_states:
                    if not (from_id in transition_map):
                        transition_map[from_id] = {}
                    if not (to_id in transition_map[from_id]):
                        transition_map[from_id][to_id] = []
                    transition_map[from_id][to_id].append(symbol)

        for from_id, to_id_n_values in transition_map.items():
            for to_id, values in to_id_n_values.items():
                self.json_automata['transitions'].append({"from": from_id, "to": to_id, "values": values}) 
        return self.json_automata

    def set_word(self, word):
        self.word = word

    def set_step(self, step):
        self.step = step

    def set_state(self, state_id):
        if state_id in self.states:
            self.curr_state_id = state_id
        else:
            self.curr_state_id = self.initial_id
