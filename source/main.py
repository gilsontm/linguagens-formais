import os
from flask import *

from models.regex import Regex
from models.grammar import Grammar
from models.finite_automata import FiniteAutomata
from models.regular_expression_interface import RegularExpressionInterface
import requests

app = Flask(__name__)
app.config["FILES_FOLDER"] = os.path.join(os.path.dirname(__file__), "files")

def get_file_path(filename):
    path = os.path.join(app.config["FILES_FOLDER"], filename)
    return path

@app.route("/")
def main():
    return render_template("base.html")

@app.route("/automata/import", methods=["POST"])
def import_automata():
    path = get_file_path("automata_upload.txt")
    file = request.files["file"]
    file.save(path)
    automata = FiniteAutomata()
    automata.from_file(path)
    json = automata.to_json()
    return json

@app.route("/automata/unify", methods=["POST"])
def unify_automata():
    automata_1 = FiniteAutomata()
    automata_2 = FiniteAutomata()

    automata_1.from_json(request.get_json()['automata_1'])
    automata_2.from_json(request.get_json()['automata_2'])

    unified_automata = FiniteAutomata.unify(automata_1, automata_2)
    json = unified_automata.to_json()
    return json

@app.route("/automata/intersect", methods=["POST"])
def intersect_automata():
    automata_1 = FiniteAutomata()
    automata_2 = FiniteAutomata()

    automata_1.from_json(request.get_json()['automata_1'])
    automata_2.from_json(request.get_json()['automata_2'])

    intersected_automata = FiniteAutomata.intersect(automata_1, automata_2)
    json = intersected_automata.to_json()
    print(json)
    return json

@app.route("/automata/export", methods=["POST"])
def export_automata():
    path = get_file_path("automata.txt")
    automata = FiniteAutomata()
    automata.from_json(request.get_json())
    automata.to_file(path)
    return send_file(path, mimetype="text/plain")

@app.route("/automata/determinize", methods=["POST"])
def determinize_automata():
    automata = FiniteAutomata()
    automata.from_json(request.get_json()['automata'])
    determinized_automata = FiniteAutomata.determinize(automata)
    json = determinized_automata.to_json()
    return json

@app.route("/automata/step", methods=["POST"])
def step_automata():
    json = request.get_json()
    automata = FiniteAutomata()
    automata.from_json(json['automata'])
    return (automata.step_forward(json['configuration']['curr_state'],json['configuration']['curr_step'],json['word']))

@app.route("/automata/fastrun", methods=["POST"])
def fast_run_automata():
    json = request.get_json()
    automata = FiniteAutomata()
    automata.from_json(json['automata'])
    return (automata.fast_run(json['word']))


@app.route("/grammar/import", methods=["POST"])
def import_grammar():
    path = get_file_path("grammar_upload.txt")
    file = request.files["file"]
    file.save(path)
    grammar = Grammar()
    grammar.from_file(path)
    json = grammar.to_json()
    return json

@app.route("/grammar/export", methods=["POST"])
def export_grammar():
    path = get_file_path("grammar.txt")
    grammar = Grammar()
    grammar.from_json(request.get_json())
    grammar.to_file(path)
    return send_file(path, mimetype="text/plain")

@app.route("/regex/import", methods=["POST"])
def import_regex():
    path = get_file_path("regex_upload.txt")
    file = request.files["file"]
    file.save(path)
    regex = Regex.from_file(path)
    json = regex.to_json()
    return json

@app.route("/regex/export", methods=["POST"])
def export_regex():
    path = get_file_path("regex.txt")
    regex = Regex.from_json(request.get_json())
    regex.to_file(path)
    return send_file(path, mimetype="text/plain")

@app.route("/regex/convert_dfa", methods=["POST"])
def convert_regex_to_dfa():
    regex = Regex.from_json(request.get_json())
    absolute_exp = regex.unify_expressions()
    regex_interface = RegularExpressionInterface()
    dfa = regex_interface.build_dfa(absolute_exp)
    dfa_json = dfa.to_json()
    return json
