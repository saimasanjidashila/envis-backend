#!/usr/bin/env python3
#!/usr/bin/env python3
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import pandas as pd
import geojson
import xarray as xr
import geojson
app = Flask(__name__)
CORS(app)

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
DATA_DIR = os.path.join(os.getcwd(), "data")
GEOJSON_DIR = os.path.join(os.getcwd(), "geojson")

# Ensure all directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(GEOJSON_DIR, exist_ok=True)

@app.route('/')
def index():
    return "EnVis backend is running!"

@app.route("/upload", methods=["POST"])
def upload_file():
    uploaded_file = request.files.get("file")
    if not uploaded_file:
        return jsonify({"error": "No file uploaded"}), 400

    filename = uploaded_file.filename
    filepath = os.path.join(UPLOAD_DIR, filename)
    uploaded_file.save(filepath)

    try:
        columns = pd.read_csv(filepath, nrows=0).columns.tolist()
        print(f"File '{filename}' uploaded and saved. Columns: {columns}")
        return jsonify({"status": "File uploaded", "columns": columns, "filename": filename})
    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500

@app.route("/sst-preview")
def serve_preview():
    return send_file("data/sst_preview.png", mimetype="image/png")

@app.route("/geojson/<path:filename>")
def serve_geojson(filename):
    return send_from_directory(GEOJSON_DIR, filename)

@app.route("/sst_today_overlay")
def serve_sst_today_overlay():
    return send_file("data/sst_today_overlay.png", mimetype="image/png")

@app.route("/dust-preview")
def serve_dust_preview():
    return send_file("data/ducmass_overlay.png", mimetype="image/png")

@app.route("/sst-details", methods=["GET"])
def sst_details():
    details = {
        "variable_name": "sst",
        "long_name": "Sea Surface Temperature",
        "units": "°C",
        "source": "NOAA OISST V2",
        "institution": "NOAA",
        "date_range": "Real time",
        "shape": [24, 361, 720, 1],
        "dimensions": ["time", "lat", "lon"]
    }
    return jsonify(details)

@app.route("/dust_today_overlay")
def serve_dust_today_overlay():
    return send_file("data/ducmass_overlay.png", mimetype="image/png")

@app.route("/sst-tomorrow-preview")
def serve_sst_tomorrow_preview():
    return send_file("data/predicted_sst_tomorrow.png", mimetype="image/png")

@app.route("/predicted_sst_tomorrow_overlay")
def serve_predicted_sst_tomorrow_overlay():
    return send_file("data/predicted_sst_tomorrow.png", mimetype="image/png")

@app.route("/render", methods=["POST"])
def render_data():
    filename = request.form.get("filename")
    variable = request.form.get("variable")

    if not filename or not variable:
        return jsonify({"error": "Filename and variable required"}), 400

    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 400

    try:
        df = pd.read_csv(filepath)
        df.columns = df.columns.str.lower()
        variable = variable.lower()

        lat_col = next((c for c in ["lat", "latitude"] if c in df.columns), None)
        lon_col = next((c for c in ["lon", "longitude"] if c in df.columns), None)

        if not lat_col or not lon_col:
            return jsonify({"error": "CSV must contain 'lat' and 'lon' columns"}), 400
        if variable not in df.columns:
            return jsonify({"error": f"Column '{variable}' not found. Available: {list(df.columns)}"}), 400

        df = df[[lat_col, lon_col, variable]].dropna()

        MAX_POINTS = 150000
        if len(df) > MAX_POINTS:
            df = df.sample(n=MAX_POINTS, random_state=42)

        if df.empty:
            return jsonify({"error": "No valid data rows"}), 400

        geojson_data = convert_to_geojson(df, lat_col, lon_col)
        out_path = os.path.join(UPLOAD_DIR, "processed.geojson")
        with open(out_path, "w") as f:
            geojson.dump(geojson_data, f)

        print(f"Generated GeoJSON with {len(df)} points.")

        return jsonify({"status": "GeoJSON generated", "path": "/uploads/processed.geojson", "variable": variable})

    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

@app.route("/uploads/<filename>")
def serve_uploaded(filename):
    path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(path):
        return send_file(path)
    else:
        return jsonify({"error": "File not found"}), 404

def convert_to_geojson(df, lat_col, lon_col):
    features = []
    for row in df.itertuples(index=False):
        lat = getattr(row, lat_col)
        lon = getattr(row, lon_col)
        props = row._asdict()
        features.append(geojson.Feature(
            geometry=geojson.Point((float(lon), float(lat))),
            properties=props
        ))
    return geojson.FeatureCollection(features)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
