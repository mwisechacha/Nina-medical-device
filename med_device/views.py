from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
import numpy as np
import os

def home(request):
    return render(request, 'home.html')
# Example: Load your AI model here (replace with your actual model loading code)
# from tensorflow.keras.models import load_model
# model = load_model(os.path.join(settings.BASE_DIR, 'model.h5'))

def predict_tumor_type(signal):
    # Dummy prediction logic, replace with your model's prediction
    # prediction = model.predict(signal.reshape(1, -1))
    # For demonstration, let's just return the mean frequency as "prediction"
    return float(np.mean(signal))

def tumor_prediction_view(request):
    prediction = None
    if request.method == 'POST':
        # Load the latest ultrasonic signal (ensure the path is correct)
        npy_path = os.path.join(os.path.dirname(__file__), 'ultrasonic_signal.npy')
        if os.path.exists(npy_path):
            signal = np.load(npy_path)
            prediction = predict_tumor_type(signal)
        else:
            prediction = "No signal data found. Please upload or collect data first."
    return render(request, 'prediction_result.html', {'prediction': prediction})