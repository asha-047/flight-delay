from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

# Load your trained model (pipeline including encoding)
model = joblib.load(r'D:\Projects\model\flight_delay_model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    if not request.is_json:
        return jsonify({"error": "JSON request expected"}), 400

    data = request.get_json()

    try:
        # Make sure your model expects the features in this order:
        # carrier, origin, dest, dayOfWeek, depHour, length
        features = [
            data['carrier'],
            data['origin'],
            data['dest'],
            float(data['dayOfWeek']),
            float(data['depHour']),
            float(data['length'])
        ]

        # Model predicts delay in minutes
        pred_value = model.predict([features])[0]

        # Define status based on delay threshold (e.g., 15 minutes)
        status = "DELAYED" if pred_value > 15 else "ON TIME"

        response = {
            "status": status,
            "likelihood": min(max(pred_value, 0), 100),
            "detail": f"Predicted delay: {pred_value:.2f} minutes"
        }
        return jsonify(response)

    except KeyError as ke:
        return jsonify({"error": f"Missing field: {ke}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
