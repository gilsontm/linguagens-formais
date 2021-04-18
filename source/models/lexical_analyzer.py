from models.regex import Regex
from models.finite_automata import FiniteAutomata
from models.regex_interface import RegularExpressionInterface


class LexicalAnalyzer:

    def __init__(self):
        self.automaton = None
        self.lexemes = None
        self.tokens = {}

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
    
    def run_analysis(self, code):
        lexemes = code.split()
        while lexemes:
            token = self.next_token(lexemes)
            if token["name"]:
                self.__add_token(token)
    
    def next_token(self, lexemes):
        # Os lexemas sao lidos do ultimo ao primeiro
        lexem = lexemes.pop()
        
        step = 0
        state_id = self.automaton.initial_id
        result = {}

        # Alimenta o automato com a palavra e retorna o resultado
        # TODO substituir por fast run? Vale a pena chamar o determinize() toda vez?
        while (len(lexem) >= step):
            result = self.automaton.step_forward(state_id,step,lexem)
            if not result["processing"]:
               break

            step += 1
            state_id = result["next_states"][0]
        
        # Palavras nao aceitas retornam um token com valores vazios
        if not result["accepted"]:
            return {"name":"", "value":""}
        else:
            state_id = result["curr_state"]
            name = self.automaton.states[state_id].get_name()
            name = name.replace("{", "")
            name = name.replace("}", "")
            return {"name": name, "value": lexem}
        
    def __add_token(self, token):
        token_name = token["name"]
        token_value = token["value"]

        if token_name not in self.tokens:
            self.tokens[token_name] = [token_value]
        else:
            self.tokens[token_name].append(token_value)