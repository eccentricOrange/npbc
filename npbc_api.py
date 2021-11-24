from flask import Flask, jsonify, request, abort
from npbc import NPBC_core

app = Flask(__name__)
base_name = "/npbc/api"

core = NPBC_core()
core.load_files()

@app.route(f"{base_name}/addpaper", methods=["POST"])
def add_paper():
    if (not request.json) or ('paper_key' not in request.json):
        abort(400)

    decoded_delivery_data = core.decode_days_and_cost(request.json['days']['sold'], request.json['days']['costs'])

    core.create_new_paper(request.json['paper_key'], request.json['name'], decoded_delivery_data)
    
    return jsonify({'result': True}), 201

@app.route(f"{base_name}/editpaper", methods=["POST"])
def edit_paper():
    if (not request.json) or ('paper_key' not in request.json):
        abort(400)

    decoded_delivery_data = core.decode_days_and_cost(request.json['days']['sold'], request.json['days']['costs'])
    
    core.edit_existing_paper(request.json['paper_key'], request.json['name'], decoded_delivery_data)
    
    return jsonify({'result': True}), 201

@app.route(f"{base_name}/delpaper", methods=["POST"])
def delete_paper():
    if (not request.json) or ('paper_key' not in request.json):
        abort(400)

    core.delete_existing_paper(request.json['paper_key'])
    
    return jsonify({'result': True}), 201

def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()