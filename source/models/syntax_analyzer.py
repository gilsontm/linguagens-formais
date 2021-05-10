import copy
from utils import messages
from models.grammar import Grammar
from exceptions.invalid_usage import InvalidUsage


class SyntaxAnalyzer:

    """
    Implementa um Analisador sintático preditivo LL(1).
    """

    def __init__(self):
        self.grammar = None
        self.table = None

    @staticmethod
    def from_file(file_path):
        analyser = SyntaxAnalyzer()
        analyser.grammar = Grammar()
        analyser.grammar.from_file(file_path)
        analyser.build_table()
        return analyser

    def build_table(self):
        if self.grammar is None:
            raise InvalidUsage(messages.INVALID_GRAMMAR)
        if not self.grammar.is_valid():
            raise InvalidUsage(messages.INVALID_GRAMMAR)

        # TODO: fatorar e remover recursão à esquerda

        variables = list(self.grammar.get_variables())
        terminals = list(self.grammar.get_terminals()) + ["$"]

        table = {v: {t : None for t in terminals} for v in variables}

        first_table = self.grammar.get_first_table()
        follow_table = self.grammar.get_follow_table()

        for head in self.grammar.dictionary:
            for derivation in self.grammar.dictionary[head]:
                first = self.grammar.get_first(derivation, first_table=first_table)
                for terminal in first:
                    if terminal == "&":
                        continue
                    if table[head][terminal] is None:
                        table[head][terminal] = derivation
                    else:
                        raise InvalidUsage(messages.GRAMMAR_CONFLICT)
                if "&" in first:
                    follow = follow_table[head]
                    for terminal in follow:
                        if table[head][terminal] is None:
                            table[head][terminal] = derivation
                        else:
                            raise InvalidUsage(messages.GRAMMAR_CONFLICT)
        self.table = table

    def is_valid(self):
        if self.grammar is None:
            return False
        if self.table is None:
            return False
        return self.grammar.is_valid()

    def run_analysis(self, sentence):
        stacktrace = []

        stack = ["$", "S"]
        entry = sentence + "$"
        accepted = False

        variables = self.grammar.get_variables()

        while entry and stack:
            history = {"stack" : stack, "entry" : entry}
            stacktrace.append(copy.deepcopy(history))
            symbol = stack.pop()
            if symbol in variables:
                if symbol in self.table and entry[0] in self.table[symbol]:
                    derivation = self.table[symbol][entry[0]]
                    if derivation is None:
                        accepted = False
                        break
                    if derivation == "&":
                        continue
                    derivation = list(derivation)
                    derivation.reverse()
                    stack += derivation
                else:
                    accepted = False
                    break
            elif symbol == entry[0]:
                if symbol == "$":
                    accepted = True
                    break
                else:
                    entry = entry[1:]
            else:
                accepted = False
                break
        return stacktrace, accepted
