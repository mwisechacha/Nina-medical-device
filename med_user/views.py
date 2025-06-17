from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
import numpy as np
import time
import os
import json
from django.views.decorators.csrf import csrf_exempt

waiting_screening_id = None

def home(request):
    return render(request, 'med_user/home.html')

def try_it_out(request):
    global waiting_screening_id
     
    if waiting_screening_id is None:
        return render(request, 'try_it_out.html', {'screening_id': 0})
    else:
        return redirect('predict_diagnosis', screening_id=waiting_screening_id)
    
def request_demo(request):
    pass

@csrf_exempt
def receive_screening_data(request):
    global waiting_screening_id

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sensor_data = np.array(data.get('sensor_data', []))

            from .models import ScreeningData
            obj = ScreeningData.objects.create(
                matrix_json = json.dumps(sensor_data.tolist())
            )

            waiting_screening_id = obj.id

            return render(request, 'tumor_data.html', {'screening_id': obj.id, 'sensor_data': sensor_data.reshape(3, 3)})
        except Exception as e:
                return render(request, 'home.html', {"error": str(e)})
    else:
        return render(request, 'home.html')

def predict_diagnosis(request, screening_id):
    from .models import ScreeningData
    obj = ScreeningData.objects.get(id=screening_id)

    # Run model (simulate delay)
    import time
    import numpy as np

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

    # Show "waiting" page first, then redirect to result page
    return render(request, 'prediction_wait.html', {
        'screening_id': screening_id
    })

def prediction_result(request, screening_id):
    from .models import ScreeningData
    obj = ScreeningData.objects.get(id=screening_id)

    if obj.diagnosis is None:
        return redirect('predict_diagnosis', screening_id=screening_id)

    return render(request, 'prediction_result.html', {
        'screening_id': screening_id,
        'diagnosis': obj.diagnosis,
        'sensor_data': obj.get_matrix().reshape(3, 3)
    })