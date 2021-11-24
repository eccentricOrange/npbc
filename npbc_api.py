from npbc_core import NPBC_core, CONFIG_FILEPATH
from flask import Flask, request, jsonify, abort

app = Flask(__name__)
BASE_NAME = "/npbc/api"

core = NPBC_core()
core.load_files()

@app.route(f"{BASE_NAME}/getpapers", methods=["GET"])
def get_papers():
    return jsonify(core.papers), 200

@app.route(f"{BASE_NAME}/getpaper/<paper_key>", methods=["GET"])
def get_paper(paper_key):
    if paper_key in core.papers:
        return jsonify(core.papers[paper_key]), 200

    abort(406)

@app.route(f"{BASE_NAME}/getudlstrings", methods=["GET"])
def get_undelivered_strings():
    return jsonify(core.undelivered_strings), 200

@app.route(f"{BASE_NAME}/getudlstring/<int:year>/<int:month>", methods=["GET"])
def get_undelivered_string(year, month):
    if f"{month}/{year}" in core.undelivered_strings:
        return jsonify(core.undelivered_strings[f"{month}/{year}"]), 200

    abort(406)

@app.route(f"{BASE_NAME}/getudldates/<int:year>/<int:month>", methods=["GET"])
def get_undelivered_dates(year, month):
    core.month = month
    core.year = year
    core.prepare_dated_data()
    core.undelivered_strings_to_dates()

    return jsonify(core.undelivered_dates), 200

@app.route(f"{BASE_NAME}/addudl/<int:year>/<int:month>", methods=["POST"])
def add_undelivered_string(year, month):
    if not request.json:
        abort(400)

    core.month = month
    core.year = year
    core.prepare_dated_data()

    for paper_key, string in request.json.items():
        if paper_key in core.papers:
            core.undelivered_strings[f"{month}/{year}"][paper_key].append(string)

    core.addudl()

    return jsonify({"status": "success"}), 201

@app.route(f"{BASE_NAME}/deludl/<int:year>/<int:month>", methods=["POST"])
def delete_undelivered_string(year, month):
    core.month = month
    core.year = year
    core.prepare_dated_data()
    core.deludl()
    return jsonify({"status": "success"}), 201

@app.route(f"{BASE_NAME}/editconfig", methods=["POST"])
def edit_config():
    if not request.json:
        abort(400)

    if core.edit_config_file(request.json):
        return jsonify({"status": "success"}), 200
    
    else:
        abort(406)

@app.route(f"{BASE_NAME}/calculate/<int:year>/<int:month>/<int:save>", methods=["GET"])
def calculate(year, month, save):
    core.month = month
    core.year = year
    core.prepare_dated_data()
    core.undelivered_strings_to_dates()
    core.calculate_all_papers()
    core.format()


    if bool(save):
        core.save_results()

    return jsonify({"status": "success"}), 200

def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()