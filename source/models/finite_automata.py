import json
from models.state import State



"""
    Finite automata class;
    The automata structure stores separetly the initial and final states ids;
    The states property stores each ZState of the automata;
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
            self.states[state['id']] = State(state['id'], state['name'])
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
                    transition_map[key] += str(transition['to'])+"-"

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
                    self.states[from_state] = State(from_state, 'q'+str(from_state))
                symbol = transition[1]
                to_states = transition[2].split('-')
                for to_state in to_states:
                    to_state = int(to_state)
                    if not (to_state in self.states):
                        self.states[to_state] = State(to_state, 'q'+str(to_state))
                    self.states[from_state].add_transition(symbol, self.states[to_state])

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

        for from_id, to_state_n_values in transition_map.items():
            for to_state, values in to_state_n_values.items():
                self.json_automata['transitions'].append({"from": from_id, "to": to_state.id, "values": values}) 
        return self.json_automata

    def set_word(self, word):
        self.word = word

    def set_step(self, step):
        self.step = step

    def set_state(self, state_id):
        if state_id == -1:
            self.curr_state_id = self.initial_id
        elif (state_id in self.states):
            self.curr_state_id = state_id


    #step forward once processing word
    def step_forward(self):
        if (not self.valid()):
            return {"processing":False, "accepted": False, "reason": "invalid"}

        if (len(self.word) == self.step):
            if (self.curr_state_id in self.final_ids):
                return {"processing":False, "accepted": True}
            return {"processing":False, "accepted": False, "reason": "rejected"}

        state = self.states[self.curr_state_id]
        curr_symbol = self.word[self.step]
        next_states = state.transition.get(curr_symbol)
        next_episilon_states = state.transition.get('&')
        next_state_ids = []
        next_episilon_state_ids = []

        if (next_states == None and next_episilon_states == None):
            return {"processing":False, "accepted": False, "curr_state": self.curr_state_id, "next_states":[]}
        else:
            if (next_states != None):
                for next_state in next_states:
                    next_state_ids.append(next_state.id)
            if (next_episilon_states != None):
                for next_episilon_state in next_episilon_states:
                    next_episilon_state_ids.append(next_episilon_state.id)
            return {"processing":True, "accepted": False, "next_states": next_state_ids, "next_episilon_states": next_episilon_state_ids}


    def determinization(self):
        new_automata = FiniteAutomata()
        new_states = {}
        epsilon_closure = self.epsilon_closure()
        initial_closure_name = self.closure_name(epsilon_closure[self.initial_id])

        self.determinization(epsilon_closure[self.states[self.initial_id].id], epsilon_closure, new_states)

        name_to_id = {}
        id_count = 0

        for name, transitions in new_states.items():
            if(initial_closure_name == name):
                new_automata.initial_id = id_count

            if (any(item in self.name_to_ids(name) for item in self.final_ids)):
                new_automata.final_ids.append(id_count)

            name_to_id[name] = id_count
            new_automata.states[id_count] = State(id_count, name)
            id_count += 1


        for name, transitions in new_states.items():
            state = new_automata.states[name_to_id[name]]

            for symbol, states in transitions.items():
                next_name = self.closure_name(states)
                next_id = name_to_id[next_name]
                next_state = new_automata.states[next_id]

                state.add_transition(symbol,next_state)

        return new_automata


    """
    A determinização
    """
    def determinization(self, closure, epsilon_closure, new_states):
        name = self.closure_name(closure)
        new_states[name] = {}
        for state_id in closure:    
            for symbol, next_states in self.states[state_id].transition.items():
                if symbol == '&':
                    continue
                if not (symbol in new_states[name]):
                    new_states[name][symbol] = []
                for next_state in next_states:
                    for next_state_in_closure in epsilon_closure[next_state.id]:
                        if not(next_state_in_closure in new_states[name][symbol]):
                            new_states[name][symbol].append(next_state_in_closure)


        for symbol, state_list in new_states[name].items():
            if not (self.closure_name(state_list) in new_states):
                self.determinization(state_list, epsilon_closure, new_states)


    def closure_name(self, closure):
        name = ""
        for state_id in closure:
            name = name + 'q' + str(state_id)

        return name

    def name_to_ids(self, name):
        string_ids = name.split("q")
        string_ids.remove('')
        return [int(i) for i in string_ids]

    def epsilon_closure(self):
        closure = {}

        for state_id, state in self.states.items():
            closure[state_id] = [state_id]
            self.epsilon_closure_of(state_id,closure[state_id])

        return closure

    #stores closure states ids list in closure
    def epsilon_closure_of(self, state_id, closure):
        if('&' in self.states[state_id].transition):
            for state in self.states[state_id].transition['&']:
                if not (state.id in closure):
                    closure.append(state.id)
                    self.epsilon_closure_of(state.id, closure)

    def is_epsilon(self):
        for state_id, state in self.states.items():
            if ('&' in state.transition):
                return True
        return False

    def unify(automata_1, automata_2):

        new_automata = FiniteAutomata()

        new_states = {}
        new_final_states = []
        inital_state = State(0,"q0")


        new_automata.states = new_states
        new_automata.final_ids = new_final_states
        new_automata.initial_id = 0

        inital_state.add_transition('&',automata_1.states[automata_1.initial_id])
        inital_state.add_transition('&',automata_2.states[automata_2.initial_id])

        new_states[0] = inital_state

        for state_id, state in automata_1.states.items():
            state.id = state_id+1
            new_states[state_id+1] = state
            if state_id in automata_1.final_ids:
                new_final_states.append(state_id+1)

        automata_2_state_count = len(automata_1.states);
        for state_id, state in automata_2.states.items():
            automata_2_state_count += 1
            state.id = automata_2_state_count
            new_states[automata_2_state_count] = state
            if state_id in automata_2.final_ids:
                new_final_states.append(automata_2_state_count)

        return new_automata

 
