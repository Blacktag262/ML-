CREDENCE AI — Credit Risk Predictor

Files:
- app.py
- templates/index.html
- static/style.css
- static/script.js
- credit_risk_model.pkl (copy your existing file here)
- model_features.pkl (copy your existing file here)

Run on Windows:
1. Open CMD in this folder.
2. Install dependencies:
   py -3.12 -m pip install Flask pandas scikit-learn joblib
3. Start the app:
   py -3.12 app.py
4. Open http://127.0.0.1:5000 in your browser.

Notes:
- This demo expects the two PKL files beside app.py.
- The saved model's exact feature names/order must match the form's feature engineering. If you see an error about missing features, share the exact error so the backend can be aligned to the model.
- For an actual public deployment, use a compatible Python/scikit-learn version and add production settings. Do not use this demo as the sole basis for real credit decisions.
