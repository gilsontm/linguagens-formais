import requests
from flask import *
from utils.path import get_file_path
from models.finite_automata import FiniteAutomata


blueprint = Blueprint("automata", __name__)

class AutomataHandler:

    @blueprint.route("/import", methods=["POST"])
    def import_automata():
        path = get_file_path("automata_upload.txt")
        file = request.files["file"]
        file.save(path)
        automata = FiniteAutomata()
        automata.from_file(path)
        json = automata.to_json()
        return json

    @blueprint.route("/unify", methods=["POST"])
    def unify_automata():
        automata_1 = FiniteAutomata()
        automata_2 = FiniteAutomata()

        automata_1.from_json(request.get_json()['automata_1'])
        automata_2.from_json(request.get_json()['automata_2'])

        unified_automata = FiniteAutomata.unify(automata_1, automata_2)
        json = unified_automata.to_json()
        return json

    @blueprint.route("/intersect", methods=["POST"])
    def intersect_automata():
        automata_1 = FiniteAutomata()
        automata_2 = FiniteAutomata()

        automata_1.from_json(request.get_json()['automata_1'])
        automata_2.from_json(request.get_json()['automata_2'])

        intersected_automata = FiniteAutomata.intersect(automata_1, automata_2)
        json = intersected_automata.to_json()
        print(json)
        return json

    @blueprint.route("/export", methods=["POST"])
    def export_automata():
        path = get_file_path("automata.txt")
        automata = FiniteAutomata()
        automata.from_json(request.get_json())
        automata.to_file(path)
        return send_file(path, mimetype="text/plain")

    @blueprint.route("/determinize", methods=["POST"])
    def determinize_automata():
        automata = FiniteAutomata()
        automata.from_json(request.get_json()['automata'])
        determinized_automata = FiniteAutomata.determinize(automata)
        json = determinized_automata.to_json()
        return json

    @blueprint.route("/minimize", methods=["POST"])
    def minimize_automata():
        automata = FiniteAutomata()
        automata.from_json(request.get_json()['automata'])
        valid, minimized_automata = FiniteAutomata.minimize(automata)
        if valid:
            json = minimized_automata.to_json()
            return json
        return None

    @blueprint.route("/step", methods=["POST"])
    def step_automata():
        json = request.get_json()
        automata = FiniteAutomata()
        automata.from_json(json['automata'])
        return (automata.step_forward(json['configuration']['curr_state'],json['configuration']['curr_step'],json['word']))

    @blueprint.route("/fastrun", methods=["POST"])
    def fast_run_automata():
        json = request.get_json()
        automata = FiniteAutomata()
        automata.from_json(json['automata'])
        return (automata.fast_run(json['word']))
