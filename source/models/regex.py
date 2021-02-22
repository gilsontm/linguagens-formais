class Regex:

    def __init__(self, expressions):
        self.expressions = expressions

    @staticmethod
    def from_json(json):
        return Regex(json["expressions"])
    
    @staticmethod
    def from_file(path):
        expressions = []
        with open(path, "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.replace(" ", "")
                line = line.replace("\n", "")
                line = line.replace(";", "")
                elements = line.split("<-")
                if len(elements) != 2:
                    continue
                expressions.append({elements[0] : elements[1]})
        return Regex(expressions)

    def to_json(self):
        return {"expressions": self.expressions}

    def to_file(self, path):
        with open(path, "w") as f:
            for expression in self.expressions:
                for key in expression:
                    f.write(f"{key} <- {expression[key]};\n")
