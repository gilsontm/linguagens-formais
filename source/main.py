import os
from flask import *
from models.grammar import Grammar

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
    # path = save_file("upload.txt")
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

@app.route("/expression/import", methods=["POST"])
def import_expression():
    # path = save_file("upload.txt")
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
