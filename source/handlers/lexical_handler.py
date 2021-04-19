import requests
from flask import *
from utils import messages
from utils.path import get_file_path
from exceptions.invalid_usage import InvalidUsage
from models.lexical_analyzer import LexicalAnalyzer


blueprint = Blueprint("lexical", __name__)

class LexicalHandler:

    @blueprint.route("/create-analyzer", methods=["POST"])
    def build_analyzer():
        path = get_file_path("analyzer.txt")
        analyzer = LexicalAnalyzer.from_json(request.get_json())
        analyzer.to_file(path)
        return send_file(path, mimetype="text/plain")

    @blueprint.route("/run-analysis", methods=["POST"])
    def analyze():
        path = get_file_path("analyzer_upload.txt")
        file = request.files["file"]
        file.save(path)
        analyzer = LexicalAnalyzer.from_file(path)
        if not analyzer.valid():
            raise InvalidUsage(message.INVALID_AUTOMATA)
        tokens = analyzer.run_analysis(request.form["code"])
        return {"tokens" : tokens}
