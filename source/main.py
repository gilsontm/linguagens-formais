import os
from flask import *

from models import regex
from models.grammar import Grammar
from models.finite_automata import FiniteAutomata

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
    return send_file(path, mimetype="text/plain")

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
    path = get_file_path("regex_upload.xml")
    file = request.files["file"]
    file.save(path)
    expression = regex.from_file(path)
    json = expression.to_json()
    return json

@app.route("/regex/export", methods=["POST"])
def export_regex():
    path = get_file_path("regex.xml")
    expression = regex.from_json(request.get_json())
    expression.to_file(path)
    return send_file(path, mimetype="application/xml")
