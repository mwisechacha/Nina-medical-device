from django.shortcuts import render, redirect
from django.http import JsonResponse
import numpy as np
import json
from django.views.decorators.csrf import csrf_exempt

from .models import ScreeningData
from .predictions import predict

waiting_screening_id = None

def request_demo(request):
    pass

def home(request):
    return render(request, 'med_user/home.html')

def try_it_out(request):
    global waiting_screening_id
    return render(request, 'med_user/wait_for_data.html', {
        'screening_id': waiting_screening_id or 0
    })

# check if data ready
def check_data_ready(request):
    global waiting_screening_id
    if waiting_screening_id:
        return JsonResponse({'ready': True, 'screening_id': waiting_screening_id})
    else:
        return JsonResponse({'ready': False})

# data recieved
def show_data_received(request, screening_id):
    return render(request, 'med_user/data_received.html', {
        'screening_id': screening_id
    })

# Receive data from ESP32
@csrf_exempt
def receive_screening_data(request):
    global waiting_screening_id

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            matrix = np.array(data.get('matrix', []))

            if matrix.size == 0:
                return JsonResponse({'error': "No matrix provided"}, status=400)

            obj = ScreeningData.objects.create(
                matrix_json = json.dumps(matrix.tolist())
            )
            print(f"Received matrix: {matrix}")

            waiting_screening_id = obj.id

            # ESP32 gets JSON response (you can also send 200 OK)
            return JsonResponse({'status': 'ok', 'screening_id': obj.id})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
def get_rule_based_diagnosis(matrix):
    invalid_count = sum(1 for row in matrix for value in row if value == -1)
    
    if invalid_count > 0:
        return {
            'risk_level': 'invalid',
            'label': 'Invalid Scan',
            'recommendation': 'Please try scanning again following the instructions manual',
            'invalid_zones': invalid_count
        }

    normal_count = 0
    benign_count = 0
    suspicious_count = 0
    
    for row in matrix:
        for value in row:
            if value <= 30:
                normal_count += 1
            elif value <= 60:
                benign_count += 1
            else:
                suspicious_count += 1
    
    if suspicious_count >= 3 or (matrix[1][1] > 60 and suspicious_count >= 2):
        return {
            'risk_level': 'high',
            'label': 'High risk - tumor likely',
            'recommendation': 'Urgent professional evaluation recommended'
        }
    elif benign_count >= 2:
        return {
            'risk_level': 'medium',
            'label': 'Possible benign - monitor',
            'recommendation': 'Suggest follow-up scan'
        }
    else:
        return {
            'risk_level': 'low',
            'label': 'Normal',
            'recommendation': 'No immediate action needed'
        }

# Show tumor data heatmap
def show_tumor_data(request, screening_id):
    obj = ScreeningData.objects.get(id=screening_id)
    matrix = json.loads(obj.matrix_json)
    
    # Calculate rule-based diagnosis and counts
    rule_based_diagnosis = get_rule_based_diagnosis(matrix)
    
    # Calculate counts for display
    normal_count = sum(1 for row in matrix for value in row if value <= 30)
    benign_count = sum(1 for row in matrix for value in row if 30 < value <= 60)
    suspicious_count = sum(1 for row in matrix for value in row if value > 60)
    invalid_count = sum(1 for row in matrix for value in row if value == -1)
    
    return render(request, 'med_user/rule_based_result.html', {
        'screening_id': screening_id,
        'sensor_data': matrix,
        'rule_based_diagnosis': rule_based_diagnosis,
        'normal_count': normal_count,
        'benign_count': benign_count,
        'suspicious_count': suspicious_count,
        'center_zone_value': matrix[1][1]
    })

# second wait
def model_wait(request):
    global waiting_screening_id

    if waiting_screening_id is None:
        return redirect('try_it_out')

    return render(request, 'med_user/wait_for_prediction.html', {
        'screening_id': waiting_screening_id
    })

# Run diagnosis
def predict_diagnosis(request, screening_id):
    obj = ScreeningData.objects.get(id=screening_id)

    prediction_label, visualization_path, score  = predict(screening_id)

    if visualization_path:
        obj.visualization = visualization_path

    score = float(score * 100) 

    # Save diagnosis
    obj.diagnosis = prediction_label
    obj.score = round(score, 2)
    obj.save()

    return redirect('prediction_result', screening_id=screening_id)

# Show result
def prediction_result(request, screening_id):
    obj = ScreeningData.objects.get(id=screening_id)
    return render(request, 'med_user/prediction_result.html', {
        'screening_id': screening_id,
        'diagnosis': obj.diagnosis,
        'score': obj.score,
        'sensor_data': obj.get_matrix().reshape(3, 3),
        'visualization_url': obj.visualization.url if obj.visualization else None
    })

