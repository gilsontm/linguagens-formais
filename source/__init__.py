import os
from flask import *

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('base.html', title="Página inicial")

@app.route('/hello')
def hello():
    return render_template('hello.html', title="Outra página")
