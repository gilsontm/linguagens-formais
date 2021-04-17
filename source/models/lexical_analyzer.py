from models.regex import Regex
from models.finite_automata import FiniteAutomata
from models.regex_interface import RegularExpressionInterface


class LexicalAnalyzer:

    def __init__(self):
        self.automaton = None

    @staticmethod
    def from_file(file_path):
        analyser = LexicalAnalyzer()
        analyser.automaton = FiniteAutomata()
        analyser.automaton.from_file(file_path)
        return analyser

    @staticmethod
    def from_json(json):
        dependencies = json["dependencies"]
        expressions = json["expressions"]

        # Gera um autômato para cada expressão
        automata = []
        for pair in expressions:
            key = tuple(pair.keys())[-1]
            expression = dependencies.copy()
            expression.append(pair)
            expression = {"expressions" : expression}
            regex = Regex.from_json(expression)
            absolute_regex = regex.unify_expressions(unify_on_this=key)
            automaton = RegularExpressionInterface().build_dfa(absolute_regex)
            # Os estados finais de cada autômato recebem
            # o nome da classe léxica que eles reconhecem
            for state_id in automaton.final_ids:
                automaton.states[state_id].name = key
            automata.append(automaton)

        analyser = LexicalAnalyzer()
        # Faz a união dos autômatos gerados
        automaton = FiniteAutomata.unify(*automata, rename=False)
        # Renomeia os estados que não são finais para "q", pois não são importantes
        for state_id, state in automaton.states.items():
            if not (state_id in automaton.final_ids):
                state.name = "q"
        # Determiniza o autômato resultante da união
        automaton = FiniteAutomata.determinize(automaton)
        analyser.automaton = automaton
        return analyser

    def to_file(self, file_path):
        if self.automaton is None:
            return False
        return self.automaton.to_file(file_path)
