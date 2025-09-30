from flask import Flask, jsonify
import os, json

app = Flask(__name__)
JSON_FILE = '/tmp/locations.json'

@app.route('/locations', methods=['GET'])
def get_locations():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r') as f:
            all_locations = json.load(f)
        return jsonify({"status": "success", "data": all_locations})
    else:
        return jsonify({"status": "error", "message": "No locations found."})

def handler(request, context):
    return app(request.environ, context)
