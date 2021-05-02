import requests
from flask import *
from utils import messages
from utils.path import get_file_path
from exceptions.invalid_usage import InvalidUsage


blueprint = Blueprint("syntax", __name__)

class SyntaxHandler:

    @blueprint.route("/run-analysis", methods=["POST"])
    def analyze():
        path = get_file_path("grammar_upload.txt")
        file = request.files["file"]
        file.save(path)
        # TODO: implementar criação de analisador
        # TODO: implementar reconhecimento de sentença
        # valor = request.form["chave"]
