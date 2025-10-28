from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import traceback

app = Flask(__name__)
CORS(app)

# --- Load model and training columns ---
try:
    model = joblib.load("flight_delay_model.pkl")
    training_columns = joblib.load("training_columns.pkl")  # Columns used during training
except Exception as e:
    model = None
    training_columns = None
    print("❌ Failed to load model or columns:", e)

# List of valid options for fallback
valid_airlines = ["CO", "US", "AA", "AS", "DL", "B6", "HA", "OO", "9E", "OH",
                  "EV", "XE", "YV", "UA", "MQ", "FL", "F9", "WN", "OTHER"]
valid_airports = ["JFK", "LAX", "ORD", "ATL", "SFO", "MIA", "SEA", "DFW",
                  "DEN", "BOS", "OTHER"]

def make_input_df(data):
    """
    Convert input JSON to DataFrame compatible with trained model.
    Unknown airlines/airports mapped to 'OTHER'.
    Missing columns added as zeros to match training.
    """
    airline = data.get('carrier', 'OTHER')
    origin = data.get('origin', 'OTHER')
    dest = data.get('dest', 'OTHER')
    day = int(data.get('dayOfWeek', 1))
    dep_hour = int(data.get('depHour', 10))
    length = int(data.get('length', 120))

    # Map unknown airlines/airports to 'OTHER'
    if airline not in valid_airlines:
        airline = 'OTHER'
    if origin not in valid_airports:
        origin = 'OTHER'
    if dest not in valid_airports:
        dest = 'OTHER'

    # Build DataFrame
    row = {
        "Airline": airline,
        "AirportFrom": origin,
        "AirportTo": dest,
        "DayOfWeek": day,
        "Time": dep_hour * 100,
        "Length": length
    }

    df_input = pd.DataFrame([row])

    # Add missing columns from training (e.g., from one-hot encoding)
    for col in training_columns:
        if col not in df_input.columns:
            df_input[col] = 0

    # Reorder columns to match training
    df_input = df_input[training_columns]

    return df_input

@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    try:
        data = request.get_json()
        X = make_input_df(data)

        # Make prediction
        pred = model.predict(X)[0]

        # Return ONLY status (no likelihood)
        result = {
            "status": "DELAYED" if int(pred) == 1 else "ON TIME"
        }

        return jsonify(result)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5000)
