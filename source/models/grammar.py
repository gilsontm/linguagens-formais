class Grammar:

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
        self.dictionary[key].append(value)

    """
    Returns whether a grammar is valid.
    An invalid grammar is one that:
        - has a variable but no derivations.
        - has a variable that does not appear in the head of any derivation.
    """
    def is_valid(self):
        # Checks whether a key has no derivation.
        for k, v in self.dictionary.items():
            if not v:
                return False

        # Checks whether a variable appears in at least one derivation head.
        variables = self.get_variables()
        for variable in variables:
            for key in self.dictionary:
                if variable in key:
                    break
            else:
                return False

        return True

    """
    Returns true if a grammar is regular, false otherwise
    """
    def is_regular(self):
        for k, v in self.dictionary.items():
            for derivation in v:
                if len(k) != 1:
                    return False
                if not k.isupper():
                    return False
                if len(derivation) > 2:
                    return False
                if derivation[0].isupper():
                    return False
                if len(derivation) == 2 and derivation[1].islower():
                    return False
        return True

    def remove_left_recursion(self):
        # TODO: implementar remoção de recursão à esquerda
        pass

    def factor(self):
        # TODO: implementar fatoração
        pass

    """
    Returns the FIRST set of a sequence of characteres
    """
    def get_first(self, sequence):
        pass

    """
    Returns the FOLLOW set of a sequence of characteres
    """
    def get_follow(self, sequence):
        pass