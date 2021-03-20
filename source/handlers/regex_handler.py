import requests
from flask import *
from utils.path import get_file_path
from models.regex import Regex


blueprint = Blueprint("regex", __name__)

class RegexHandler:

    @blueprint.route("/import", methods=["POST"])
    def import_regex():
        path = get_file_path("regex_upload.txt")
        file = request.files["file"]
        file.save(path)
        regex = Regex.from_file(path)
        json = regex.to_json()
        return json

    @blueprint.route("/export", methods=["POST"])
    def export_regex():
        path = get_file_path("regex.txt")
        regex = Regex.from_json(request.get_json())
        regex.to_file(path)
        return send_file(path, mimetype="text/plain")

    @blueprint.route("/to_automata", methods=["POST"])
    def convert_regex_to_dfa():
        regex = Regex.from_json(request.get_json())
        absolute_exp = regex.unify_expressions()
        regex_interface = RegularExpressionInterface()
        dfa = regex_interface.build_dfa(absolute_exp)
        path = get_file_path("automata.txt")
        valid = dfa.to_file(path)
        if valid:
            return send_file(path, mimetype="text/plain")
        return None
