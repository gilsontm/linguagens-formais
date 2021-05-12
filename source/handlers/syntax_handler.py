import requests
from flask import *
from utils import messages
from utils.path import get_file_path
from exceptions.invalid_usage import InvalidUsage
from models.syntax_analyzer import SyntaxAnalyzer


blueprint = Blueprint("syntax", __name__)

class SyntaxHandler:

    @blueprint.route("/run-analysis", methods=["POST"])
    def analyze():
        path = get_file_path("grammar_upload.txt")
        file = request.files["file"]
        file.save(path)
        sentence = request.form["sentence"]
        # Criação de analisador
        analyzer = SyntaxAnalyzer.from_file(path)
        # Reconhecimento de sentença
        stacktrace, accepted = analyzer.run_analysis(sentence)
        result = {
            "stacktrace": stacktrace,
            "accepted": accepted,
            "variables": list(analyzer.grammar.get_variables()),
            "terminals": list(analyzer.grammar.get_terminals()) + ["$"],
            "table": analyzer.table,
        }
        return result

