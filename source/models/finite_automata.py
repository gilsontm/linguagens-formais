import re
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
        if not(self.states):
            #Lista de estados está vazia
            return False
        elif self.initial_id == None:
            #Não possui estado inicial
            return False
        elif not(self.initial_id in self.states):
            #Estado inicial não está decladado na lista de estados
            return False
        elif self.final_ids == None:
            #Lista de estados finais pode ser vazia, porém, não nula
            return False
        elif not(all(elem in list(self.states.keys()) for elem in self.final_ids)):
            #Alguma estado final não está declarado na lista de estados
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
    def to_file(self, file_path, with_names=True):
        if not self.valid():
            return False

        with open(file_path, "w") as f:
            f.write(f"{len(self.states)}\n")
            f.write(f"{self.initial_id}\n")
            f.write(f"{','.join([str(final_id) for final_id in self.final_ids])}\n")
            alphabet = self.alphabet()
            f.write(f"{','.join(alphabet)}\n")

            for from_id, from_state in self.states.items():
                for symbol in from_state.transition:
                    to_ids = [str(to_state.id) for to_state in from_state.transition[symbol]]
                    f.write(f"{from_id},{symbol},{'-'.join(to_ids)}\n")

            if with_names:
                for state_id, state in self.states.items():
                    f.write(f"{state_id}:{state.name}\n")
        return True

    """
        Builds this automata from formated file from a given file_path;
    """
    def from_file(self, file_path):
        json_automata = {}
        with open(file_path) as f:
            lines = f.readlines()

            self.initial_id = int(lines[1])

            for final_state in lines[2].split(","):
                if final_state != "\n":
                    self.final_ids.append(int(final_state))

            # matches [number]:[name]
            naming_regex = re.compile(r"(\d+):(.+)")
            # matches [number],[one character],[name]
            transition_regex = re.compile(r"(\d+),(.{1}),(\d+[\-\d+]*)")

            for line in lines[4:]:
                naming = naming_regex.match(line)
                if naming:
                    state_id, name = naming.groups()
                    self.states[int(state_id)].name = name.replace("\n", "")
                    continue
                from_state, symbol, to_states = transition_regex.match(line).groups()
                from_state = int(from_state)
                to_states = to_states.split("-")

                if not (from_state in self.states):
                    self.states[from_state] = State(from_state, "q"+str(from_state))

                for to_state in to_states:
                    to_state = int(to_state)
                    if not (to_state in self.states):
                        self.states[to_state] = State(to_state, "q"+str(to_state))
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
            self.json_automata['states'].append({
                "id": from_state.id,
                "name": from_state.name,
                "final": (from_state.id in self.final_ids),
                "initial": (from_state.id == self.initial_id)
            })

            for symbol, to_states in from_state.transition.items():
                for to_id in to_states:
                    if not (from_id in transition_map):
                        transition_map[from_id] = {}
                    if not (to_id in transition_map[from_id]):
                        transition_map[from_id][to_id] = []
                    transition_map[from_id][to_id].append(symbol)

        for from_id, to_state_n_values in transition_map.items():
            for to_state, values in to_state_n_values.items():
                self.json_automata['transitions'].append({
                    "from": from_id,
                    "to": to_state.id,
                    "values": values
                })
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
                return {"processing":False, "accepted": True, "curr_state": curr_state_id}
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
            result = determinized_automaton.step_forward(state_id,step,word)
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
            define final_ids
        """
        for state_id, state in new_automata.states.items():
            name_compound = "{"
            states_ids = FiniteAutomata.to_closure_ids(state.name)

            for id_string in states_ids:
                if(int(id_string) in automaton.final_ids and not(state_id in new_automata.final_ids)):
                    new_automata.final_ids.append(state_id)
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

    """ returns the union between two or more automata """
    def unify(*automata_in, rename=True):
        automata = [copy.deepcopy(automaton) for automaton in automata_in]
        new_automaton = FiniteAutomata()

        new_automaton.initial_id = 0
        initial_state = State(0, "q0")
        new_automaton.states[0] = initial_state

        state_count = 0
        for automaton in automata:
            initial_state.add_transition("&", automaton.states[automaton.initial_id])
            for state_id, state in automaton.states.items():
                state_count += 1
                state.id = state_count
                new_automaton.states[state_count] = state
                if state_id in automaton.final_ids:
                    new_automaton.final_ids.append(state_count)
        if rename:
            new_automaton.rename_states()
        return new_automaton

    """
        adds missing transitions to a dead state, if there's any
    """
    def complete_states(self, alphabet=None):
        if alphabet is None:
            alphabet = self.alphabet()
        dead_state = None
        states = list(self.states.values())
        for symbol in alphabet:
            for from_state in states:
                if not from_state.has_transition_by_symbol(symbol):
                    if dead_state is None:
                        dead_state = self.add_state("dead")
                    self.add_transition(symbol, from_state, dead_state)
        if dead_state is not None:
            for symbol in alphabet:
                self.add_transition(symbol, dead_state, dead_state)

    """
        returns the complement of a given automaton
        if the automaton is non-deterministic, it is first determinized
    """
    def complement(automaton, alphabet=None):
        if (not automaton.is_deterministic()):
            new_automaton = FiniteAutomata.determinize(automaton)
        else:
            new_automaton = copy.deepcopy(automaton)
        new_automaton.complete_states(alphabet)
        state_ids = list(new_automaton.states.keys())
        new_final_ids = [item for item in state_ids if item not in new_automaton.final_ids]
        new_automaton.final_ids = new_final_ids
        return new_automaton

    """
        returns the intersection of two given automata
        uses de morgan
    """
    def intersect(automaton_1, automaton_2):
        alphabet_1 = automaton_1.alphabet()
        alphabet_2 = automaton_2.alphabet()
        alphabet = list(set(alphabet_1 + alphabet_2) - set(['&']))
        complement_1 = FiniteAutomata.complement(automaton_1, alphabet)
        complement_2 = FiniteAutomata.complement(automaton_2, alphabet)
        unification_of_complements = FiniteAutomata.unify(complement_1, complement_2)
        intesection = FiniteAutomata.complement(unification_of_complements)
        intesection.rename_states()
        return intesection

    """
        returns a minimized automaton
    """
    def minimize(automaton_in):
        automaton = copy.deepcopy(automaton_in)
        if (not automaton.is_deterministic()):
            automaton = FiniteAutomata.determinize(automaton)
        automaton.remove_unreachable_states()
        automaton.remove_dead_states()
        minimized_automaton = FiniteAutomata()

        equivalence_classes = automaton.get_equivalence_classes()
        equivalence_classes = tuple(equivalence_classes)

        mapping = {}
        for class_id, class_set in enumerate(equivalence_classes):
            mapping.update({state_id : class_id for state_id in class_set})
            name = ", ".join(map(lambda x: f"q{x}", class_set))
            name = "{" + name + "}"
            state = minimized_automaton.add_state(name)
            if automaton.initial_id in class_set:
                minimized_automaton.set_initial_state(state)
            if len(class_set.intersection(set(automaton.final_ids))) > 0:
                minimized_automaton.add_final_state(state)
        for from_class_id, from_class_set in enumerate(equivalence_classes):
            from_state_id = tuple(from_class_set)[0]
            from_state = automaton.states[from_state_id]
            from_class = minimized_automaton.states[from_class_id]
            for symbol in from_state.transition:
                if len(from_state.transition[symbol]) == 0:
                    continue
                to_state = from_state.transition[symbol][0]
                to_class_id = mapping[to_state.id]
                to_class = minimized_automaton.states[to_class_id]
                minimized_automaton.add_transition(symbol, from_class, to_class)
        minimized_automaton.rename_states()
        return minimized_automaton

    """
        removes unreachable states from the automaton
    """
    def remove_unreachable_states(self):
        reachable_states = set([self.initial_id])
        remaining_states = set([self.initial_id])

        while len(remaining_states) > 0:
            temp = set()
            for state_id in remaining_states:
                from_state = self.states[state_id]
                for to_states in from_state.transition.values():
                    for to_state in to_states:
                        temp.add(to_state.id)
            remaining_states = temp - reachable_states
            reachable_states = reachable_states.union(remaining_states)

        unreachable_state = set(self.states.keys()) - reachable_states
        for unreachable_state_id in unreachable_state:
            self.states.pop(unreachable_state_id, None)
        self.final_ids = [item for item in self.final_ids if item in reachable_states]

    """
        removes dead states from the automaton
    """
    def remove_dead_states(self):
        alive_states = set(self.final_ids)
        remaining_states = set(self.final_ids)

        while len(remaining_states) > 0:
            temp = set()
            for from_state in self.states.values():
                for to_state_id in remaining_states:
                    if from_state.has_transition_to_state(to_state_id):
                        temp.add(from_state.id)
                        break
            remaining_states = temp - alive_states
            alive_states = alive_states.union(remaining_states)

        dead_states = (set(self.states.keys()) - set([self.initial_id])) - alive_states
        for dead_state_id in dead_states:
            self.states.pop(dead_state_id, None)

        for state in self.states.values():
            for dead_state_id in dead_states:
                state.remove_transitions_to(dead_state_id)
        self.final_ids = [item for item in self.final_ids if item in alive_states]

    """
        removes equivalent states from the automaton
        adapted from Hopcroft's algorithm: https://en.wikipedia.org/wiki/DFA_minimization
    """
    def get_equivalence_classes(self):
        alphabet = self.alphabet()
        final_states = frozenset(self.final_ids)
        non_final_states = frozenset(self.states.keys()) - final_states
        P = set([final_states, non_final_states])
        W = set([final_states, non_final_states])
        while len(W) > 0:
            A = W.pop()
            for symbol in alphabet:
                X = set()
                for from_state in self.states.values():
                    for to_state_id in A:
                        if from_state.has_transition_to_state_by_symbol(to_state_id, symbol):
                            X.add(from_state.id)
                            break
                PP = set()
                for Y in P:
                    intersection = Y.intersection(X)
                    difference = Y - X
                    if len(intersection) == 0 or len(difference) == 0:
                        PP.add(Y)
                        continue
                    PP.add(intersection)
                    PP.add(difference)
                    if Y in W:
                        W.remove(Y)
                        W.add(intersection)
                        W.add(difference)
                    else:
                        if len(intersection) <= len(difference):
                            W.add(intersection)
                        else:
                            W.add(difference)
                P = PP
        if frozenset() in P:
            P.remove(frozenset())
        return P

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
        state_id = max(list(self.states.keys()) + [-1]) + 1
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
