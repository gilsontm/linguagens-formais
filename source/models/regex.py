class Regex:

    def __init__(self, expressions):
        self.expressions = expressions
        self.dependencies = {}
        self.depends_on = {}
        self.depended_by = {}

    @staticmethod
    def from_json(json):
        json_expressions = json["expressions"]
        expressions = {}
        for pair in json_expressions:
            expressions = dict(expressions, **pair)
        return Regex(expressions)
    
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
            for var in self.expressions:
                f.write(f"{var} <- {self.expressions[var]};\n")

    def __add_depended_by(self, var, depended_by_this):
        if var not in self.depended_by:
            self.depended_by[var] = set()
        self.depended_by[var].add(depended_by_this)

    def __add_depends_on(self, var, depends_on_this):
        if var not in self.depends_on:
            self.depends_on[var] = set()
        self.depends_on[var].add(depends_on_this)

    def __add_dependency(self, var, dependency):
        self.__add_depends_on(var, dependency)
        self.__add_depended_by(dependency, var)

    def __define_dependencies(self):
        # Resetar dependências
        self.depends_on = {var: set() for var in self.expressions}
        self.depended_by = {var: set() for var in self.expressions}

        for var in self.expressions:
            exp = self.expressions[var]
            i = 0
            length = len(exp)
            while i < length:
                ch = exp[i]
                i += 1
                dependency = ""
                while i < length and ch.isupper():
                    dependency += ch
                    ch = exp[i]
                    i += 1
                if len(dependency) != 0:
                    self.__add_dependency(var, dependency)

    def __resolve_dependencies(self, var):
        exp = self.expressions[var]
        begin_separators = [' ', '(', '+', '.']
        end_separators = [' ', ')', '+', '.', '*', '?']

        # Precisa ter certeza que nada além desta variável seja
        # substituído. AMOR não deve editar a variável AMORA
        for depended_by_this in self.depended_by[var]:
            depended_by_exp = self.expressions[depended_by_this]
            depended_by_exp = ' ' + depended_by_exp + ' '
            for bs in begin_separators:
                for es in end_separators:
                    depended_by_exp = depended_by_exp.replace(bs + var + es, bs + '(' + exp + ')' + es)
            self.expressions[depended_by_this] = depended_by_exp[1:-1:]

    def __dependencies(self, var):
        if var not in self.depends_on:
            self.depends_on[var] = set()
        return self.depends_on[var]

    OPEN = 0
    CLOSED = 1
    NOT_VISITED = 2

    def __topologic_order_iteration(self, vertice, color, stack):
        color[vertice] = Regex.OPEN
        for key in self.__dependencies(vertice):
            if color[key] == Regex.NOT_VISITED:
                stack = self.__topologic_order_iteration(key, visited, stack)
            elif color[key] == Regex.OPEN:
                return None
            pass
        stack.append(vertice)
        color[vertice] = Regex.CLOSED
        return stack

    def __topological_order(self):
        color = {var: Regex.NOT_VISITED for var in self.expressions}

        stack = []

        for key in self.expressions:
            if color[key] == Regex.NOT_VISITED:
                stack = self.__topologic_order_iteration(key, color, stack)

        if stack != None:
            return stack[::-1]
        return None

    def unify_expressions(self, unify_on_this=None):
        self.__define_dependencies()
        order = self.__topological_order()
        if unify_on_this is None:
            unify_on_this = order[-1]
        for var in order:
            self.__resolve_dependencies(var)
        return self.expressions[unify_on_this]
