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
        variables = list()
        for key in self.dictionary:
            keys = list(filter(lambda k: k.isupper(), key))
            for x in keys:
                variables.append(x)

            for string in self.dictionary[key]:
                values = list(filter(lambda v: v.isupper(), string))
                for x in values:
                    variables.append(x)

        return list(set(variables))

    """
    Returns all terminals in the grammar (lower case letters)
    """
    def get_terminals(self):
        terminals = list()
        for key in self.dictionary:
            keys = list(filter(lambda k: k.islower(), key))
            for x in keys:
                terminals.append(x)

            for string in self.dictionary[key]:
                values = list(filter(lambda v: v.islower(), string))
                for x in values:
                    terminals.append(x)

        return list(set(terminals))

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
    Returns if a grammar is valid. An invalid grammar is one that
    has a variable but no derivations.
    """
    def is_valid(self):
        for k, v in self.dictionary.items():
            if not v:
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

    def find_free_symbol(self):
        symbol = ord('A')
        while chr(symbol) in self.dictionary:
            symbol = symbol + 1
        return chr(symbol)

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
                            self.add_derivation(Ai, beta + alfa)
                        print(self.to_json())
            """
                Elimine as recursões diretas das produções de P_ com lado esquerdo Ai
            """
            c1 = []
            c2 = []
            Ai_ = self.find_free_symbol()
            for derivation in self.get_derivations(Ai):
                if derivation and derivation[0] == Ai:
                    c2.append(derivation[1::] + Ai_)
                elif derivation:
                    c1.append(derivation + Ai_)
            # Adiciona-se epsilon
            c2.append("")
            if not c1:
                c1.append(Ai_)
            self.add_key(Ai, c1)
            self.add_key(Ai_, c2)