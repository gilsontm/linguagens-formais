import os
from flask import *
from werkzeug.exceptions import HTTPException

import requests

app = Flask(__name__)
from .finiteAutomata import FiniteAutomata
app.config["FILES_FOLDER"] = os.path.join(os.path.dirname(__file__), "files")



@app.route("/")
def main():
    return render_template("base.html")

@app.route("/automata/import", methods=["POST"])
def import_automata():
    raise Exception()
    path = save_file("upload.txt")
    # from_file
    # to_json
    json = {}
    return json

@app.route("/automata/export", methods=["POST"])
def export_automata():
    json = request.get_json()
    # from_json
    # to_file -> path
    path = ""
    return send_file(path, mimetype="text/plain")

@app.route("/automata/step", methods=["POST"])
def step_automata():
    json = request.get_json()
    automata = FiniteAutomata()
    automata.from_json(json['automata'])
    automata.set_word(json['word'])
    automata.set_step(json['step'])
    automata.set_state(json['curr_state'])
    return (automata.step_forward(json['branch_id']))


@app.route("/grammar/import", methods=["POST"])
def import_grammar():
    path = save_file("upload.txt")
    # from_file
    # to_json
    json = {}
    return json

@app.route("/grammar/export", methods=["POST"])
def export_grammar():
    json = request.get_json()
    # from_json
    # to_file -> path
    path = ""
    return send_file(path, mimetype="text/plain")

@app.route("/expression/import", methods=["POST"])
def import_expression():
    path = save_file("upload.txt")
    # from_file
    # to_json
    json = {}
    return json

@app.route("/expression/export", methods=["POST"])
def export_expression():
    json = request.get_json()
    # from_json
    # to_file -> path
    path = ""
    return send_file(path, mimetype="text/plain")

def save_file(filename):
    path = os.path.join(app.config["FILES_FOLDER"], filename)
    file = request.files["file"]
    file.save(path)
    return path
   