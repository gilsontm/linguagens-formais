class Grammar:

    def __init__(self):
        self.dictionary = {}

    def from_file(self, file_path):
        with open(file_path) as f:
            for line in f:
                s = line.strip()
                s = s.replace(" ", "")
                split = s.split("->")
                key = split[0]
                value = split[1].split("|")

                self.dictionary[key] = value

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

    def from_json(self, json):
        self.dictionary = json

    def to_json(self):
        return self.dictionary

    def get_dictionary(self):
        return self.dictionary

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

    def get_derivations(self, key):
        return self.dictionary[key]

    def add_key(self, key, values):
        self.dictionary[key] = values
