import json
from models.state import State



"""
    Finite automata class;
    The automata structure stores separetly the initial and final states ids;
    The states property stores each State of the automata;
    A State structure points to each State on the arrow side of each of it's transitions;
"""
class FiniteAutomata:

    def __init__(self):
        #map of id to state
        self.states = {}
        #initial state id
        self.initial_id = None
        #finalstates state ids
        self.final_ids = []

        #automata as python dict directly from json
        self.json_automata = None


    """
        Builds this finite automata from a json;
        The json reference, already a python dict, is stored in json_automata;
        The json_automata dict has a 'states' index and a 'transitions' index;
        Each states index enrty has its 'id', 'name', and 'initial' and final flags;
        Each transition index enrty has its 'from', 'to', and 'symbol' list;
        Each state, of State type, followed by it's transitions is stored in states dict, 
            a python dict from id to State object;
    """
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

    """
        Checks if this automata has a initial state, 
        at least one final state, 
        and the states ids are on the states dict
    """
    def valid(self):
        if ((not (self.curr_state_id in self.states)) or self.initial_id == None or len(self.states) == 0 or len(self.final_ids) == 0):
            return False
        return True

    """
        Writes to file this automata, if valid, in specifc format given a file_path;
        First the json representation is built,
        then is the required format;
    """
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

    """
        Builds this automata from formated file from a given file_path;
    """
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

    """
        Translates this automata to a python dict
        then stores it in 'json_automata';

        Since the json structure splits states and transitions, 
        diferently of this automata structure,
        it is created a transition_map to hold the transitions
        before appending then to the dict;
    """
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

