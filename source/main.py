from flask import *
from handlers.regex_handler import blueprint as regex_blueprint
from handlers.grammar_handler import blueprint as grammar_blueprint
from handlers.lexical_handler import blueprint as lexical_blueprint
from handlers.automata_handler import blueprint as automata_blueprint
from exceptions.invalid_usage import InvalidUsage

app = Flask(__name__)
app.register_blueprint(regex_blueprint, url_prefix="/regex")
app.register_blueprint(grammar_blueprint, url_prefix="/grammar")
app.register_blueprint(lexical_blueprint, url_prefix="/lexical")
app.register_blueprint(automata_blueprint, url_prefix="/automata")

@app.route("/")
def main():
    return render_template("base.html")

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response