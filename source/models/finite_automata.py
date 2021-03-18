import json
import copy
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
        if state with id equal to initial_state_id is in states list
        if has at least one final state, 
        if every state id in final states id list is in states list
        and if every state referenced by its states transitions in in the states list
    """
    def valid(self):
        if not(self.states) or self.initial_id == None or not(self.initial_id in self.states) or not(self.final_ids) or not(all(elem in list(self.states.keys()) for elem in self.final_ids)):
            return False

        for state_id, state in self.states.items():
            if not(all(elem in list(self.states.values()) for elem in [item for sublist in list(state.transition.values()) for item in sublist])):
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


    """
        returns automaton state after transitioning from state with "state_id" 
        by the character in "step" index of "word" 
    """
    def step_forward(self, state_id, step, word):
        #set curr_state state
        curr_state_id = self.initial_id
        if (state_id in self.states):
            curr_state_id = state_id

        if (not self.valid()):
            return {"processing":False, "accepted": False, "reason": "invalid"}

        if (len(word) == step):
            if (curr_state_id in self.final_ids):
                return {"processing":False, "accepted": True}
            return {"processing":False, "accepted": False, "reason": "rejected"}

        state = self.states[curr_state_id]
        curr_symbol = word[step]
        next_states = state.transition.get(curr_symbol)
        next_episilon_states = state.transition.get('&')
        next_state_ids = []
        next_episilon_state_ids = []

        if (next_states == None and next_episilon_states == None):
            return {"processing":False, "accepted": False, "curr_state": curr_state_id, "next_states":[]}
        else:
            if (next_states != None):
                for next_state in next_states:
                    next_state_ids.append(next_state.id)
            if (next_episilon_states != None):
                for next_episilon_state in next_episilon_states:
                    next_episilon_state_ids.append(next_episilon_state.id)
            return {"processing":True, "accepted": False, "next_states": next_state_ids, "next_episilon_states": next_episilon_state_ids}


    def fast_run(self,word):
        step = 0
        state_id = self.initial_id
        result = {}

        determinized_automaton = FiniteAutomata.determinize(self)

        while (len(word) >= step):
            result = self.step_forward(state_id,step,word)
            if not result["processing"]:
               break

            step += 1
            state_id = result["next_states"][0]

        return result

    #returns a map of state_id to its epsilon closure
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

    """
        returns determinized automaton
        it also removes unreachable states of the automaton
    """
    def determinize(automaton_in):
        automaton = copy.deepcopy(automaton_in)

        new_automata = FiniteAutomata()
        new_states = {}
        epsilon_closure = automaton.epsilon_closure()
        initial_closure_name = FiniteAutomata.to_closure_string(epsilon_closure[automaton.initial_id])

        FiniteAutomata.determinization_recursion(automaton, epsilon_closure[automaton.initial_id], epsilon_closure, new_states)

        name_to_id = {}
        id_count = 0

        for name, transitions in new_states.items():
            if(initial_closure_name == name):
                new_automata.initial_id = id_count

            if (any(item in FiniteAutomata.to_closure_ids(name) for item in automaton.final_ids)):
                new_automata.final_ids.append(id_count)

            name_to_id[name] = id_count
            new_automata.states[id_count] = State(id_count, name)
            id_count += 1


        for name, transitions in new_states.items():
            state = new_automata.states[name_to_id[name]]

            for symbol, states in transitions.items():
                next_name = FiniteAutomata.to_closure_string(states)
                next_id = name_to_id[next_name]
                next_state = new_automata.states[next_id]

                state.add_transition(symbol,next_state)

        """ transforms states names, that are the ids set in a string, 
            to original names set in a string
        """
        for state_id, state in new_automata.states.items():
            name_compound = "{"
            states_ids = FiniteAutomata.to_closure_ids(state.name)
            for id_string in states_ids:
                name_compound += automaton.states[int(id_string)].name + ","
            name_compound = name_compound[:-1]
            name_compound += "}"
            state.name = name_compound

        return new_automata


    """
        records in new_states the states and its transitions of this automaton determinzed
        the function recursively calls itself for each state in the transitions of the current
        state that hasn't been recorded yet
    """
    def determinization_recursion(automaton, closure, epsilon_closure, new_states):
        name = FiniteAutomata.to_closure_string(closure)
        new_states[name] = {}

        #records the "line" of the state in "closure" parameter in the determinized transition table
        for state_id in closure:
            for symbol, next_states in automaton.states[state_id].transition.items():
                if symbol == '&':
                    continue
                if not (symbol in new_states[name]):
                    new_states[name][symbol] = []
                for next_state in next_states:
                    for next_state_in_closure in epsilon_closure[next_state.id]:
                        if not(next_state_in_closure in new_states[name][symbol]):
                            new_states[name][symbol].append(next_state_in_closure)

        #calls determinization_recursion for each reacheble state
        for symbol, state_list in new_states[name].items():
            if not (FiniteAutomata.to_closure_string(state_list) in new_states):
                FiniteAutomata.determinization_recursion(automaton, state_list, epsilon_closure, new_states)



    """
        returns the unification of two given automata
    """
    def unify(automaton_1_in, automaton_2_in):
        automaton_1 = copy.deepcopy(automaton_1_in)
        automaton_2 = copy.deepcopy(automaton_2_in)

        new_automaton = FiniteAutomata()

        new_states = {}
        new_final_states = []


        new_automaton.states = new_states
        new_automaton.final_ids = new_final_states
        new_automaton.initial_id = 0

        """
            adds a new initial state
            wich epsilon transit to the initial states
            of the given automatum
        """
        inital_state = State(0,"q0")
        inital_state.add_transition('&',automaton_1.states[automaton_1.initial_id])
        inital_state.add_transition('&',automaton_2.states[automaton_2.initial_id])
        new_states[0] = inital_state

        #changes automaton_1 states ids
        for state_id, state in automaton_1.states.items():
            state.id = state_id+1
            new_states[state_id+1] = state
            if state_id in automaton_1.final_ids:
                new_final_states.append(state_id+1)

        #changes automaton_2 states ids
        automata_2_state_count = len(automaton_1.states);
        for state_id, state in automaton_2.states.items():
            automata_2_state_count += 1
            state.id = automata_2_state_count
            new_states[automata_2_state_count] = state
            if state_id in automaton_2.final_ids:
                new_final_states.append(automata_2_state_count)
        
        new_automaton.rename_states()

        return new_automaton

    """
        returns the complement of a given automaton
        if the automaton is non-deterministic, it is first determinized
    """
    def complement(automaton):

        if (not automaton.is_deterministic()):
            new_automaton = FiniteAutomata.determinize(automaton)
        else:
            new_automaton = copy.deepcopy(automaton)


        state_ids = list(new_automaton.states.keys())

        new_final_ids = [item for item in state_ids if item not in new_automaton.final_ids]

        new_automaton.final_ids = new_final_ids

        return new_automaton
 

    """
        returns the intersection of two given automata
        uses de morgan
    """
    def intersect(automaton_1, automaton_2):
        complement_1 = FiniteAutomata.complement(automaton_1)
        complement_2 = FiniteAutomata.complement(automaton_2)

        unification_of_complements = FiniteAutomata.unify(complement_1, complement_2)
        
        intesection = FiniteAutomata.complement(unification_of_complements)
        intesection.rename_states()

        return intesection

    """
        returns minimized deterministic finite automaton
    """
    def minimize(automaton_in):

        P = list(automaton_in.states.keys())
        Q = automaton_in.final_ids

        SIGMA = automaton_in.alphabet()

        #while (Q é não-vazio) do
        while (Q):
            print(len(Q))

            #escolha e remova um conjunto A de Q
            A = []
            A.append(Q.pop())
            if(Q):
                A.append(Q.pop())

            #for each c in ∑ do
            for c in SIGMA:

                #let X é o conjunto de estados para o qual uma transição sobre c leva a um estado em A
                X = []
                for state_id in list(automaton_in.states.keys()):
                    if (c in automaton_in.states[state_id].transition):
                        for state in automaton_in.states[state_id].transition[c]:
                            if state.id in A and not(state.id in X):
                                X.append(state.id)

                #for each conjunto Y in P para o qual X ∩ Y é não-vazio do
                every_Y_in_P = FiniteAutomata.powerset(P)

                for Y in every_Y_in_P:
                    Y_intersection_X = list(set(Y) & set(X))
                    Y_minus_X = [item for item in Y if item not in X]
                    if Y_intersection_X:
                        #substitua Y em P pelos dois conjuntos X ∩ Y e Y \ X
                        P = [item for item in P if item not in Y]
                        P = list(set(P) | set(Y_minus_X) | set(Y_intersection_X))

                        #if Y está contido em Q
                        if(set(Y).issubset(set(Q))):
                            #substitua Y em Q pelos mesmos dois conjuntos
                            Q = [item for item in Q if item not in Y]
                            Q = list(set(Q) | set(Y_minus_X) | set(Y_intersection_X))
                        #else
                        else:
                            #adicione o menor dos dois conjuntos à Q
                            if (len(Y_intersection_X) <= len(Y_minus_X)):
                                Q = list(set(Q) | set(Y_intersection_X))
                            else:
                                Q = list(set(Q) | set(Y_minus_X))

        print(*list(automaton_in.states.keys()), sep = ", ") 
        print(*P, sep = ", ")



    def powerset(s):
        power_set = []
        x = len(s)
        for i in range(1 << x):
            power_set.append([s[j] for j in range(x) if (i & (1 << j))])
        return power_set


    """
        rename states to q+state_id
    """
    def rename_states(self):
        for state_id, state in self.states.items():
            state.name = "q"+str(state_id)


    #returns state name given a list of states
    def to_closure_string(closure):
        name = ""
        closure.sort()
        for state_id in closure:
            name = name +','+ str(state_id)
        return name[1:]

    #inverse of closure_name
    def to_closure_ids(closure_name):
        return closure_name.split(',')

    #verify deterministic property
    def is_deterministic(self):
        for state_id, state in self.states.items():
            for symbol in state.transition:
                if (symbol == '&' or len(state.transition[symbol]) > 1):
                    return False
        return True

    #returns alphabet symbol list
    def alphabet(self):
        alphabet = set()
        for state_id, state in self.states.items():
            for symbol in list(state.transition.keys()):
                alphabet.add(symbol)

        return list(alphabet)

    #get state by name
    #returns none if no state found
    def get_state_by_name(self, name):
        for state_id, state in self.states.items():
            if(state.name == name):
                return state
        return None

    #adds state with name
    #automatic id assignment
    #returns the added state
    def add_state(self, name):
        state_id = max(list(self.states.keys()))+1
        self.states[state_id] = State(state_id, name)
        return self.states[state_id]

    #adds transition
    def add_transition(self, symbol, from_state, to_state):
        from_state.add_transition(symbol, to_state)

    #get transition
    def get_transitions(self, symbol, from_state):
        if (symbol in from_state.transition):
            return from_state.transition[symbol]
        return []

    #define as final state
    def add_final_state(self, final_state):
        if not(final_state.id in list(self.states.keys())):
            self.states[final_state.id] = final_state

        if not(final_state.id in self.final_ids):
            self.final_ids.append(final_state.id)

    #returns final states list
    def get_final_states(self):
        return [self.states[i] for i in self.final_ids]

    #set initial state
    def set_initial_state(self, initial_state):
        if not(initial_state.id in list(self.states.keys())):
            self.states[initial_state.id] = initial_state
        self.initial_id = initial_state.id

    #returns final states list
    def get_initial_state(self):
        return self.states[self.initial_id]