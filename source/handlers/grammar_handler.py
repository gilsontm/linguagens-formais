import requests
from flask import *
from utils.path import get_file_path
from models.grammar import Grammar


blueprint = Blueprint("grammar", __name__)

class GrammarHandler:

    @blueprint.route("/import", methods=["POST"])
    def import_grammar():
        path = get_file_path("grammar_upload.txt")
        file = request.files["file"]
        file.save(path)
        grammar = Grammar()
        grammar.from_file(path)
        json = grammar.to_json()
        return json

    @blueprint.route("/export", methods=["POST"])
    def export_grammar():
        path = get_file_path("grammar.txt")
        grammar = Grammar()
        grammar.from_json(request.get_json())
        grammar.to_file(path)
        return send_file(path, mimetype="text/plain")
