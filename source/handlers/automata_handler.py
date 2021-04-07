import requests
from flask import *
from utils import messages
from utils.path import get_file_path
from exceptions.invalid_usage import InvalidUsage
from models.finite_automata import FiniteAutomata
from models.grammar_converter import GrammarConverter


blueprint = Blueprint("automata", __name__)

class AutomataHandler:

    @staticmethod
    def __load_automata(data):
        automata = FiniteAutomata()
        automata.from_json(data)
        if not automata.valid():
            raise InvalidUsage(messages.INVALID_AUTOMATA)
        return automata

    @blueprint.before_request
    def before():
        json = request.get_json()
        if json is not None:
            if "automata" in json:
                g.automata = AutomataHandler.__load_automata(json["automata"])
            if "automata_1" in json:
                g.automata1 = AutomataHandler.__load_automata(json["automata_1"])
            if "automata_2" in json:
                g.automata2 = AutomataHandler.__load_automata(json["automata_2"])
            if "configuration" in json:
                g.configuration = json["configuration"]
            if "word" in json:
                g.word = json["word"]

    @blueprint.route("/import", methods=["POST"])
    def import_automata():
        path = get_file_path("automata_upload.txt")
        file = request.files["file"]
        file.save(path)
        automata = FiniteAutomata()
        automata.from_file(path)
        json = automata.to_json()
        return json

    @blueprint.route("/export", methods=["POST"])
    def export_automata():
        path = get_file_path("automata.txt")
        automata = g.automata
        automata.to_file(path)
        return send_file(path, mimetype="text/plain")

    @blueprint.route("/unify", methods=["POST"])
    def unify_automata():
        automata = FiniteAutomata.unify(g.automata1, g.automata2)
        return automata.to_json()

    @blueprint.route("/intersect", methods=["POST"])
    def intersect_automata():
        automata = FiniteAutomata.intersect(g.automata1, g.automata2)
        return automata.to_json()

    @blueprint.route("/to-grammar", methods=["POST"])
    def export_automata_grammar():
        path = get_file_path("grammar.txt")
        converter = GrammarConverter()
        grammar = converter.automata_to_grammar(g.automata)
        grammar.to_file(path)
        return send_file(path, mimetype="text/plain")

    @blueprint.route("/determinize", methods=["POST"])
    def determinize_automata():
        automata = FiniteAutomata.determinize(g.automata)
        return automata.to_json()

    @blueprint.route("/minimize", methods=["POST"])
    def minimize_automata():
        automata = FiniteAutomata.minimize(g.automata)
        return automata.to_json()

    @blueprint.route("/step", methods=["POST"])
    def step_automata():
        automata = g.automata
        curr_step = g.configuration["curr_step"]
        curr_state = g.configuration["curr_state"]
        result = automata.step_forward(curr_state, curr_step, g.word)
        return result

    @blueprint.route("/fast-run", methods=["POST"])
    def fast_run_automata():
        automata = g.automata
        result = automata.fast_run(g.word)
        return result
