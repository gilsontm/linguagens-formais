import copy
import string
from utils import messages
from exceptions.invalid_usage import InvalidUsage


class Grammar:

    # Set of all uppercase letters
    VARIABLES = set(string.ascii_uppercase)

    # Maximum iterations while factoring
    MAX_ITERATIONS = 100

    def __init__(self):
        self.dictionary = {}

    """
    Parses the grammar from the agreed upon structure into a grammar object
    """
    def from_file(self, file_path):
        with open(file_path) as f:
            for line in f:
                s = line.strip()
                s = s.replace(" ", "")
                split = s.split("->")
                key = split[0]
                value = split[1].split("|")

                self.dictionary[key] = value

    """
    Converts the Grammar object into a text file according to the agreed upon structure
    """
    def to_file(self, file_path):
        with open(file_path, "w") as f:
            for key in self.dictionary:
                write_string = key + " -> "
                first = True
                for value in self.dictionary[key]:
                    if first:
                        write_string += value
                        first = False
                    else:
                        write_string += " | " + value
                f.write(write_string + '\n')

    """
    Parses from a json, which is just a dictionary
    """
    def from_json(self, json):
        self.dictionary = json

    """
    A JSON is a dictionary, but this method is here for compatibility reasons
    """
    def to_json(self):
        return self.dictionary

    def get_dictionary(self):
        return self.dictionary

    """
    Returns all variables in the grammar (upper case letters)
    """
    def get_variables(self):
        variables = set()

        for key in self.dictionary:
            keys = set(filter(lambda k: self.__is_variable(k), key))
            variables = variables.union(keys)

            for string in self.dictionary[key]:
                values = set(filter(lambda v: self.__is_variable(v), string))
                variables = variables.union(values)

        return list(variables)

    """
    Returns all terminals in the grammar (lower case letters, digits and other symbols)
    """
    def get_terminals(self):
        terminals = set()

        for key in self.dictionary:
            keys = set(filter(lambda k: self.__is_terminal(k), key))
            terminals = terminals.union(keys)

            for string in self.dictionary[key]:
                values = set(filter(lambda v: self.__is_terminal(v), string))
                terminals = terminals.union(values)

        # Removes epsilon in case it exists
        terminals -= (set(["&"]))

        return list(terminals)

    """
    Returns whether a character is a variable.
    """
    def __is_variable(self, character):
        return character.isupper()

    """
    Returns whether a character is terminal.
    """
    def __is_terminal(self, character):
        if character == "&":
            return False
        return not character.isupper()

    """
    Given a production head, returns all its derivations
    """
    def get_derivations(self, key):
        return self.dictionary[key]

    """
    Adds a new key to the dictionary, which corresponds to a production or a variable
    """
    def add_key(self, key, values):
        self.dictionary[key] = values

    """
    Adds a derivation given the production head
    """
    def add_derivation(self, key, value):
        if key not in self.dictionary:
            self.add_key(key, [value])
        else:
            self.dictionary[key].append(value)

    """
    Returns whether a grammar is valid.
    An invalid grammar is one that:
        - has a head with no derivations.
        - has a derivation with no head.
        - has a variable that does not appear in the head of any derivation.
        - has a head or derivation with the invalid symbol '$'.
        - has a head made of just terminals with no variable.
    """
    def is_valid(self):
        # Checks whether grammar has the initial symbol.
        if "S" not in self.dictionary:
            return False

        # Checks whether a key has no derivation or a derivation has no key.
        for key, value in self.dictionary.items():
            if not key or not value:
                return False

        # Checks whether a key or derivation has the invalid symbol '$'.
        for key, value in self.dictionary.items():
            if "$" in key or "$" in value:
                return False

        # Checks whether a variable appears in at least one derivation head.
        variables = self.get_variables()
        for variable in variables:
            for key in self.dictionary:
                if variable in key:
                    break
            else:
                return False

        # Checks whether a head has only terminals and no variable.
        for key in self.dictionary:
            for symbol in key:
                if self.__is_variable(symbol):
                    break
            else:
                return False
        return True

    def get_length_of_longest_derivation(self):
        return max(map(len, sum(self.dictionary.values(), [])))

    """
    Returns true if a grammar is regular, false otherwise
    """
    def is_regular(self):
        if not self.is_valid():
            return False
        for k, v in self.dictionary.items():
            for derivation in v:
                if len(k) != 1:
                    return False
                if not self.__is_variable(k):
                    return False
                if len(derivation) > 2:
                    return False
                if self.__is_variable(derivation[0]):
                    return False
                if len(derivation) == 2 and self.__is_terminal(derivation[1]):
                    return False
        return True

    def is_context_free(self):
        if not self.is_valid():
            return False
        for head in self.dictionary:
            if len(head) != 1:
                return False
            if not self.__is_variable(head):
                return False
        return True

    def factor(self):
        iterations = 0
        self.remove_left_recursion()
        while not self.is_deterministic() and iterations < Grammar.MAX_ITERATIONS:
            length = self.get_length_of_longest_derivation()
            for _ in range(length):
                self.remove_direct_non_determinism()
            self.remove_indirect_non_determinism()
            iterations += 1
        if iterations >= Grammar.MAX_ITERATIONS:
            raise InvalidUsage(messages.GRAMMAR_UNSUPORTED)
        return iterations

    def remove_direct_non_determinism(self):
        variables = self.get_variables()
        for variable in variables:
            derivations = self.dictionary[variable]
            mapping = {}
            for derivation in derivations:
                head = derivation[0]
                tail = derivation[1:]
                if head not in mapping:
                    mapping[head] = []
                mapping[head].append(self.__concat(tail))
            for head, tails in mapping.items():
                if len(tails) == 1:
                    continue
                for tail in tails:
                    derivations.remove(self.__concat(head, tail))
                new_variable = self.get_new_variable_name()
                derivations.append(self.__concat(head, new_variable))
                self.dictionary[new_variable] = tails

    def remove_indirect_non_determinism(self):
        variables = self.get_variables()
        for variable in variables:
            derivations = copy.deepcopy(self.dictionary[variable])
            for derivation in derivations:
                head = derivation[0]; tail = derivation[1:]
                if self.__is_variable(head):
                    subderivations = copy.deepcopy(self.dictionary[head])
                    self.dictionary[variable].remove(derivation)
                    for subderivation in subderivations:
                        new_derivation = self.__concat(subderivation, tail)
                        if new_derivation not in self.dictionary[variable]:
                            self.dictionary[variable].append(new_derivation)

    """
    Returns a variable name that is unused.
    If there aren't any available, raises InvalidUsage exception.
    """
    def get_new_variable_name(self):
        available = Grammar.VARIABLES - set(self.get_variables())
        if len(available) == 0:
            raise InvalidUsage(messages.GRAMMAR_UNSUPORTED)
        return min(available)

    """
    Returns whether the grammar is deterministic.
    Example of non-deterministic grammar:
        S -> aS | a
    Example of deterministic grammar:
        S -> aB
        B -> S | &
    """
    def is_deterministic(self):
        variables = self.get_variables()
        first_table = self.get_first_table()

        for variable in variables:
            # Calculates the FIRST set of each production under a given head.
            firsts = [self.get_first(string, first_table) - set("&") for string in self.dictionary[variable]]
            # Checks if there are any two derivations B -> alpha and B -> beta,
            # such that (FIRST(alpha) intersect FIRST(beta)) != empty-set.
            # If there are such derivations, then the grammar is non-deterministic.
            for i in range(len(firsts)):
                for j in range(i+1, len(firsts)):
                    if len(firsts[i].intersection(firsts[j])) > 0:
                        return False
        return True

    def __concat(self, alfa, beta=""):
        alfa = alfa if len(alfa) > 0 else "&"
        beta = beta if len(beta) > 0 else "&"
        if alfa == "&":
            return beta
        if beta == "&":
            return alfa
        return alfa + beta

    def remove_left_recursion(self):
        N = self.get_variables()
        for i in range(len(N)):
            Ai = N[i]
            # para j = 1 até i-1
            for j in range(i):
                Aj = N[j]
                derivations = self.get_derivations(Ai)
                for derivation in list(derivations):
                    if derivation and derivation[0] == Aj:
                        # Remova Ai ::= Aj de P
                        derivations.remove(derivation)
                        alfa = derivation[1::]
                        # Se Aj ::= B pertence a P
                        #    P_ = P_ U {Ai ::= BA}
                        for beta in self.get_derivations(Aj):
                            self.add_derivation(Ai, self.__concat(beta, alfa))
            """
                Elimine as recursões diretas das produções de P_ com lado esquerdo Ai
            """
            c1 = []
            c2 = []
            Ai_ = self.get_new_variable_name()
            for derivation in self.get_derivations(Ai):
                if derivation != "&" and derivation[0] == Ai:
                    c2.append(self.__concat(derivation[1::], Ai_))
                elif derivation != "&":
                    c1.append(self.__concat(derivation, Ai_))
            # Adiciona-se epsilon
            c2.append("&")
            if not c1:
                c1.append(Ai_)
            self.add_key(Ai, c1)
            self.add_key(Ai_, c2)

    """
    Returns the FIRST set of a sequence of characteres
    """
    def get_first(self, sequence, first_table=None):
        if first_table is None:
            first_table = self.get_first_table()
        first = set()
        for char in sequence:
            if char == "&":
                continue
            first = first.union(first_table[char] - set("&"))
            if "&" not in first_table[char]:
                break
        else:
            first.add("&")
        return first

    """
    Returns a table of FIRSTS for all symbols.
    """
    def get_first_table(self):
        # Initialize table of FIRSTS
        first_table = dict()
        variables = self.get_variables()
        terminals = self.get_terminals()
        for variable in variables:
            first_table[variable] = set()
        for terminal in terminals:
            first_table[terminal] = set(terminal)

        # Iterate over the table of FIRSTS until no further changes can be made
        previous = None
        while previous != first_table:
            previous = copy.deepcopy(first_table)
            for variable in variables:
                for string in self.dictionary[variable]:
                    if string == "&":
                        first_table[variable].add("&")
                    for char in string:
                        if char == "&":
                            continue
                        if self.__is_terminal(char):
                            first_table[variable].add(char)
                            break
                        else:
                            first_table[variable] = first_table[variable].union(first_table[char] - set("&"))
                            if "&" not in first_table[char]:
                                break
                    else:
                        first_table[variable].add("&")
        return first_table

    """
    Returns a table of FOLLOWS for all variables (not all symbols).
    """
    def get_follow_table(self):
        # Initialize table of FOLLOWS
        follow_table = dict()
        variables = self.get_variables()
        for variable in variables:
            if variable == "S":
                follow_table[variable] = set("$")
            else:
                follow_table[variable] = set()

        # Calculate the table of FIRSTS to speed up the algorithm
        first_table = self.get_first_table()

        # Iterate over the table of FIRSTS until no further changes can be made
        previous = None
        while previous != follow_table:
            previous = copy.deepcopy(follow_table)
            for variable in variables:
                for string in self.dictionary[variable]:
                    for i in range(len(string)):
                        char = string[i]
                        if self.__is_variable(char):
                            beta = string[i+1:]
                            first_beta = self.get_first(beta, first_table=first_table)
                            if len(beta) > 0:
                                follow_table[char] = follow_table[char].union(first_beta - set("&"))
                            if len(beta) == 0 or "&" in first_beta:
                                follow_table[char] = follow_table[char].union(follow_table[variable])
        return follow_table