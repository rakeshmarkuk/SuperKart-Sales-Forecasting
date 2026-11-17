# Flask Web API for SuperKart Sales Forecasting
from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np
import io

app = Flask(__name__)

# Load the pre-trained pipeline model
model = joblib.load('superkart_model.joblib')

@app.route('/v1/predict', methods=['POST'])
def predict():
    try:
        # Get JSON data
        data = request.get_json(force=True)
        # Convert to DataFrame matching expected features
        input_df = pd.DataFrame([data])
        # Generate prediction
        prediction = model.predict(input_df)[0]
        return jsonify({'prediction': float(prediction)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/v1/predictbatch', methods=['POST'])
def predict_batch():
    try:
        # Get file from request
        file = request.files['file']
        if not file:
            return jsonify({'error': 'No file provided'}), 400
        
        # Read CSV file
        file_contents = file.stream.read().decode("utf-8")
        input_df = pd.read_csv(io.StringIO(file_contents))
        
        # Generate predictions
        predictions = model.predict(input_df)
        # Map index to prediction values
        predictions_dict = {str(i): float(pred) for i, pred in enumerate(predictions)}
        return jsonify(predictions_dict)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
