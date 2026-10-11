from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "credit_risk_model.pkl")
FEATURES_PATH = os.path.join(BASE_DIR, "model_features.pkl")

app = Flask(__name__)

model = joblib.load(MODEL_PATH)
model_features = joblib.load(FEATURES_PATH)

def build_features(data):
    # Raw inputs expected from the form
    pay_status = [int(data.get(f"PAY_{i}", 0)) for i in range(0, 6)]
    bill_amounts = [float(data.get(f"BILL_AMT{i}", 0)) for i in range(1, 7)]
    pay_amounts = [float(data.get(f"PAY_AMT{i}", 0)) for i in range(1, 7)]

    row = {
        "LIMIT_BAL": float(data.get("LIMIT_BAL", 0)),
        "SEX": int(data.get("SEX", 1)),
        "EDUCATION": int(data.get("EDUCATION", 2)),
        "MARRIAGE": int(data.get("MARRIAGE", 1)),
        "AGE": int(data.get("AGE", 30)),
        "PAY_0": pay_status[0],
        "PAY_2": pay_status[2],
        "PAY_3": pay_status[3],
        "PAY_4": pay_status[4],
        "PAY_5": pay_status[5],
        "PAY_6": int(data.get("PAY_6", 0)),
    }
    # Common credit-card default dataset uses PAY_0, PAY_2...PAY_6.
    # Include all engineered features used by the frontend/model training pipeline.
    row["AVG_PAY_STATUS"] = sum(pay_status) / max(len(pay_status), 1)
    row["MAX_PAY_STATUS"] = max(pay_status) if pay_status else 0
    row["NUM_LATE_MONTHS"] = sum(1 for x in pay_status if x > 0)
    row["AVG_BILL_AMT"] = sum(bill_amounts) / 6
    row["AVG_PAY_AMT"] = sum(pay_amounts) / 6
    total_bill = sum(bill_amounts)
    row["PAYMENT_TO_BILL_RATIO"] = (sum(pay_amounts) / total_bill) if total_bill else 0

    for i in range(1, 7):
        row[f"BILL_AMT{i}"] = bill_amounts[i-1]
        row[f"PAY_AMT{i}"] = pay_amounts[i-1]

    # Model expects the exact feature order saved during training.
    missing = [feature for feature in model_features if feature not in row]
    if missing:
        return None, missing
    input_df = pd.DataFrame([[row[feature] for feature in model_features]], columns=list(model_features))
    return input_df, []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)
        input_df, missing = build_features(data)
        if missing:
            return jsonify({"error": "The model requires features not provided by this form: " + ", ".join(missing)}), 400

        prediction = int(model.predict(input_df)[0])
        probability = None
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(input_df)[0]
            classes = list(getattr(model, "classes_", []))
            probability = float(probabilities[classes.index(1)]) if 1 in classes else float(probabilities[-1])
        else:
            probability = float(prediction)

        risk_score = round(probability * 100, 1)
        risk_level = "Low" if risk_score < 30 else ("Medium" if risk_score < 60 else "High")
        return jsonify({
            "prediction": prediction,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "message": "Likely to repay" if prediction == 0 else "Higher likelihood of default",
        })
    except Exception as exc:
        app.logger.exception("Prediction failed")
        return jsonify({"error": f"Prediction failed: {str(exc)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
