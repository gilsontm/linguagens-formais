import os
from flask import *

from models.regex import Regex
from models.grammar import Grammar
from models.finite_automata import FiniteAutomata

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

@app.route("/automata/export", methods=["POST"])
def export_automata():
    path = get_file_path("automata.txt")
    automata = FiniteAutomata()
    automata.from_json(request.get_json())
    automata.to_file(path)
    automata.determinization()
    return send_file(path, mimetype="text/plain")

@app.route("/automata/step", methods=["POST"])
def step_automata():
    json = request.get_json()
    automata = FiniteAutomata()
    automata.from_json(json['automata'])
    automata.set_word(json['word'])
    automata.set_step(json['configuration']['curr_step'])
    automata.set_state(json['configuration']['curr_state'])
    return (automata.step_forward())


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
