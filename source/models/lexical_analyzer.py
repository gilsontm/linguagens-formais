from models.regex import Regex
from models.finite_automata import FiniteAutomata
from models.regex_interface import RegularExpressionInterface


class LexicalAnalyzer:

    def __init__(self):
        self.automaton = None
        self.lexemes = None
        self.tokens = []

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

        # Renomeia os estados
        #    - estados de aceitação recebem o nome da primeira classe que representam (maior prioridade)
        #    - estados de não aceitação recebem o nome "q"
        for state_id, state in automaton.states.items():
            name = "q"
            if state_id in automaton.final_ids:
                tokens = analyser.__format_state_name(state.name).split(",")
                for token in tokens:
                    if token != "q":
                        name = token
                        break
            state.name = name
        analyser.automaton = automaton
        return analyser

    def to_file(self, file_path):
        if self.automaton is None:
            return False
        return self.automaton.to_file(file_path)

    def valid(self):
        if self.automaton is None:
            return False
        return self.automaton.valid()

    def run_analysis(self, code):
        lexemes = code.split()
        lexemes.reverse()
        while lexemes:
            token = self.next_token(lexemes)
            if token is not None:
                self.tokens.append(token)
        return self.tokens

    def next_token(self, lexemes):
        lexeme = lexemes.pop()

        step = 0
        state_id = self.automaton.initial_id
        result = {}

        last_accepted_step = 0
        last_accepted_id = -1

        # Alimenta o automato com a palavra e retorna o resultado
        while (len(lexeme) >= step):
            result = self.automaton.step_forward(state_id, step, lexeme)

            # Guardamos o ultimo estado aceito e o passo
            if state_id in self.automaton.final_ids:
                last_accepted_step = step
                last_accepted_id = state_id

            if not result["processing"]:
                break

            step += 1
            state_id = result["next_states"][0]

        # Em algum momento tivemos um token formado
        if not result["accepted"] and last_accepted_step > 0:
            # Separamos a sub-string aceita do resto
            accepted = lexeme[:last_accepted_step]
            remaining = lexeme[last_accepted_step:]

            # O que sobrou precisa ser reavaliado
            lexemes.append(remaining)
            name = self.automaton.states[last_accepted_id].get_name()
            name = self.__format_state_name(name)
            return {"token" : name, "lexeme" : accepted}

        # Finalizamos com um token
        if result["accepted"]:
            state_id = result["curr_state"]
            name = self.automaton.states[state_id].get_name()
            name = self.__format_state_name(name)
            return {"token" : name, "lexeme" : lexeme}

        # Nenhum token foi formado
        return None

    def __format_state_name(self, name):
        name = name.replace("{", "")
        name = name.replace("}", "")
        name = name.replace(">", "")
        name = name.replace("<", "")
        return name
