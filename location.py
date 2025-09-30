from flask import Flask, request, jsonify
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import os
import json

app = Flask(__name__)
JSON_FILE = '/tmp/locations.json'  # Serverless environment uses /tmp

@app.route('/location', methods=['POST'])
def location():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if request.headers.getlist("X-Forwarded-For"):
        user_ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        user_ip = request.remote_addr

    user_agent = request.headers.get('User-Agent', 'N/A')

    if not latitude or not longitude:
        return jsonify({"status": "error", "message": "Latitude and Longitude are required."}), 400

    geolocator = Nominatim(user_agent="geo_learning")

    try:
        loc = geolocator.reverse((latitude, longitude), language='en', exactly_one=True)
        if loc:
            address = loc.raw.get('address', {})
            city = address.get('city', address.get('town', address.get('village', 'N/A')))
            state = address.get('state', 'N/A')
            country = address.get('country', 'N/A')
            full_address = loc.address

            geocoded_lat = loc.latitude
            geocoded_lon = loc.longitude
            original_coords = (latitude, longitude)
            geocoded_coords = (geocoded_lat, geocoded_lon)
            distance = geodesic(original_coords, geocoded_coords).kilometers
        else:
            city = state = country = full_address = distance = "N/A"

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    location_data = {
        "latitude": latitude,
        "longitude": longitude,
        "full_address": full_address,
        "city": city,
        "state": state,
        "country": country,
        "accuracy": distance,
        "user_ip": user_ip,
        "browser": user_agent
    }

    # Serverless: store in /tmp
    all_locations = []
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, 'r') as f:
                all_locations = json.load(f)
        except json.JSONDecodeError:
            all_locations = []

    all_locations.append(location_data)

    with open(JSON_FILE, 'w') as f:
        json.dump(all_locations, f, indent=4)

    return jsonify({"status": "success", "data": location_data})


# For Vercel Serverless
def handler(request, context):
    return app(request.environ, context)
