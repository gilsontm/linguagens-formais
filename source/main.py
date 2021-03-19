from flask import *
from handlers.regex_handler import  blueprint as regex_blueprint
from handlers.grammar_handler import  blueprint as grammar_blueprint
from handlers.automata_handler import  blueprint as automata_blueprint


app = Flask(__name__)
app.register_blueprint(regex_blueprint, url_prefix="/regex")
app.register_blueprint(grammar_blueprint, url_prefix="/grammar")
app.register_blueprint(automata_blueprint, url_prefix="/automata")

@app.route("/")
def main():
    return render_template("base.html")
