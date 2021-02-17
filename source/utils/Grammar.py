import json

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
        f = open("file_path", "w")

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


    def from_json(self, filepath):
        self.dictionary = json.loads(filepath)


    def to_json(self):
        return json.dumps(self.dictionary, indent=2)


    def get_dictionary(self):
        return self.dictionary


    def get_variables(self):
        variables = list()
        for key in self.dictionary:
            variables_head = list(filter(lambda x: x.isupper(), key))
            for x in variables_head:
                variables.append(x)

            for string in self.dictionary[key]:
                variables_body = list(filter(lambda x: x.isupper(), string))
                for x in variables_body:
                    variables.append(x)

        return list(set(variables))


    def get_terminals(self):
        variables = list()
        for key in self.dictionary:
            variables_head = list(filter(lambda x: x.islower(), key))
            for x in variables_head:
                variables.append(x)

            for string in self.dictionary[key]:
                variables_body = list(filter(lambda x: x.islower(), string))
                for x in variables_body:
                    variables.append(x)

        return list(set(variables))
