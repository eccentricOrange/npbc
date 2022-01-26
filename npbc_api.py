from npbc_core import NPBC_core
from flask import Flask, request, jsonify, abort
from waitress import serve

app = Flask(__name__)

BASE_NAME = "/npbc/api"
HOSTNAME = "127.0.0.1"
PORT = 8083

@app.route(f"{BASE_NAME}/getpapers", methods=["GET"])
def get_papers():
    core = NPBC_core()
    all_papers = core.get_all_papers()
    del core
    return jsonify(all_papers), 200

@app.route(f"{BASE_NAME}/getpaper/<paper_key>", methods=["GET"])
def get_paper(paper_key):
    core = NPBC_core()
    all_papers = core.get_all_papers()
    del core

    if paper_key in all_papers:
        return jsonify(all_papers[paper_key]), 200

    abort(406)

@app.route(f"{BASE_NAME}/getudlstrings", methods=["GET"])
def get_undelivered_strings():
    core = NPBC_core()
    undelivered_strings = core.get_undelivered_strings()
    del core

    return jsonify(undelivered_strings), 200

@app.route(f"{BASE_NAME}/getudlstring/<int:year>/<int:month>", methods=["GET"])
def get_undelivered_string(year, month):
    core = NPBC_core()
    core.year = year
    core.month = month
    undelivered_strings = core.get_undelivered_strings()
    del core

    return jsonify(undelivered_strings), 200

@app.route(f"{BASE_NAME}/getudldates/<int:year>/<int:month>", methods=["GET"])
def get_undelivered_dates(year, month):
    core = NPBC_core()
    core.month = month
    core.year = year
    undelivered_dates = core.get_undelivered_dates()
    del core
    
    return jsonify(undelivered_dates), 200

@app.route(f"{BASE_NAME}/addudl/<int:year>/<int:month>", methods=["POST"])
def add_undelivered_string(year, month):
    if not request.json:
        abort(400)

    core = NPBC_core()
    core.month = month
    core.year = year

    for paper_key, string in request.json.items():
        if paper_key in core.get_all_papers():
            core.add_undelivered_string(paper_key, string)
    
    del core

    return jsonify({"status": "success"}), 201
    
@app.route(f"{BASE_NAME}/deludl/<int:year>/<int:month>", methods=["POST"])
def delete_undelivered_string(year, month):
    if not request.json:
        abort(400)
    
    core = NPBC_core()
    core.month = month
    core.year = year

    for paper_key in request.json.items():
        if paper_key in core.get_all_papers():
            core.delete_undelivered_string(paper_key)

    del core

    return jsonify({"status": "success"}), 201

@app.route(f"{BASE_NAME}/calculate/<int:year>/<int:month>/<int:save>", methods=["GET"])
def calculate(year, month, save):
    core = NPBC_core()
    core.month = month
    core.year = year

    core.get_number_of_weekdays()
    core.get_undelivered_strings()
    core.calculate_all_papers()

    if bool(save):
        core.save_results()

    totals = core.totals
    del core

    return jsonify(totals), 201

def main():
    core = NPBC_core()
    core.define_schema()
    del core

    print(f"http://{HOSTNAME}:{PORT}{BASE_NAME}")
    serve(app, host=HOSTNAME, port=PORT)

if __name__ == "__main__":
    main()
