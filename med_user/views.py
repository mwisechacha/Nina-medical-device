from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
import numpy as np
import time
import os
import json
from django.views.decorators.csrf import csrf_exempt
from .models import ScreeningData

waiting_screening_id = None

def home(request):
    return render(request, 'med_user/home.html')

def try_it_out(request):
    global waiting_screening_id

    return render(request, 'med_user/wait_for_data.html', {
        'screening_id': waiting_screening_id or 0
    })
    
def request_demo(request):
    pass

# receive data from esp32
@csrf_exempt
def receive_screening_data(request):
    global waiting_screening_id

    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            matrix = np.array(data.get('matrix', []))

            if matrix.size == 0:
                return render(request, 'med_user/home.html', {"error": "No matrix provided"})

            from .models import ScreeningData
            obj = ScreeningData.objects.create(
                matrix_json = json.dumps(matrix.tolist())
            )

            waiting_screening_id = obj.id

            return render(request, 'med_user/tumor_data.html', {
                'screening_id': obj.id,
                'sensor_data': matrix.reshape(3, 3)
            })

        except Exception as e:
            return render(request, 'med_user/home.html', {"error": str(e)})

    else:
        return render(request, 'med_user/home.html')
    
# second delay page
def model_wait(request):
    global waiting_screening_id

    if waiting_screening_id is None:
        return redirect('try_it_out')

    return render(request, 'med_user/wait_for_prediction.html', {
        'screening_id': waiting_screening_id
    })

# feed the data to the model and predict diagnosis
def predict_diagnosis(request, screening_id):
    obj = ScreeningData.objects.get(id=screening_id)

    # Run model (simulate delay)
    matrix = obj.get_matrix()
    mean_val = np.mean(matrix)

    # Save diagnosis
    if mean_val < 5.0:
        diagnosis = "Normal"
    elif mean_val < 10.0:
        diagnosis = "Suspicious - Checkup advised"
    else:
        diagnosis = "High risk - Immediate doctor visit recommended"

    obj.diagnosis = diagnosis
    obj.save()


    return render(request, 'wait_for_prediction.html', {
        'screening_id': screening_id
    })

# Show the prediction result
def prediction_result(request, screening_id):
    obj = ScreeningData.objects.get(id=screening_id)

    if obj.diagnosis is None:
        return redirect('predict_diagnosis', screening_id=screening_id)

    return render(request, 'prediction_result.html', {
        'screening_id': screening_id,
        'diagnosis': obj.diagnosis,
        'sensor_data': obj.get_matrix().reshape(3, 3)
    })