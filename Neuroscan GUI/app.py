# app.py
import os
import uuid
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from preprocess import preprocess_scan
from model import load_model, predict_from_tensor
from werkzeug.utils import secure_filename

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__, static_folder="static", static_url_path="/")
CORS(app)

# Load a model (placeholder — replace with real model path)
MODEL = load_model(model_path=None)  # if None returns a dummy model


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/predict", methods=["POST"])
def predict():
    """
    Expects multipart/form-data:
     - file: uploaded scan (dcm, nii, png, jpg)
     - scanner_type: one of ["MRI","fMRI","PET","CT"]
     - optional metadata JSON in form field "meta"
    """
    if 'file' not in request.files:
        return jsonify({"error": "no file uploaded"}), 400
    f = request.files['file']
    scanner = request.form.get("scanner_type", "MRI")
    meta_json = request.form.get("meta", "{}")
    meta = json.loads(meta_json)

    filename = secure_filename(f.filename)
    unique = f"{uuid.uuid4().hex}_{filename}"
    path = os.path.join(UPLOAD_DIR, unique)
    f.save(path)

    try:
        tensor, info = preprocess_scan(path, scanner_type=scanner, meta=meta)
    except Exception as e:
        return jsonify({"error": f"preprocess failed: {str(e)}"}), 500

    # Predict (returns dict)
    try:
        result = predict_from_tensor(
            MODEL, tensor, scanner_type=scanner, info=info)
    except Exception as e:
        return jsonify({"error": f"prediction failed: {str(e)}"}), 500

    # Combine with meta quiz if provided
    return jsonify({"filename": filename, "scanner": scanner, "prediction": result})


@app.route("/quiz", methods=["POST"])
def quiz():
    """
    Accepts JSON like:
    {
      "age": 72,
      "hypertension": true,
      "diabetes": false,
      "tbi_history": false,
      "family_history_alz": true,
      ...
    }
    Returns a simple risk score (demo).
    """
    try:
        q = request.get_json()
    except:
        return jsonify({"error": "invalid json"}), 400

    # Simple weighted scoring (toy example — replace with validated risk model)
    score = 0.0
    age = q.get("age", 0)
    score += max(0, (age-60)) * 0.1  # older -> more points
    score += 2 if q.get("hypertension") else 0
    score += 2 if q.get("diabetes") else 0
    score += 3 if q.get("tbi_history") else 0
    score += 3 if q.get("family_history_alz") else 0
    score += 1 if q.get("hearing_loss") else 0

    category = "low"
    if score > 8:
        category = "high"
    elif score > 4:
        category = "moderate"

    return jsonify({"score": score, "category": category})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
