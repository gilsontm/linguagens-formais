import requests
from flask import *
from utils import messages
from utils.path import get_file_path
from exceptions.invalid_usage import InvalidUsage


blueprint = Blueprint("lexical", __name__)

class LexicalHandler:

    @blueprint.route("/create-analyzer", methods=["POST"])
    def build_analyzer():
        # TODO: ler regexes e criar analisador léxico
        # TODO: como salvar analisador entre requisições?
        pass

    @blueprint.route("/analyze", methods=["POST"])
    def analyze():
        # TODO: ler pseudocódigo e identificar lexemas
        pass
