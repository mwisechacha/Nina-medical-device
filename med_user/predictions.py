import torch
import torch.nn as nn
import torchvision.models as models
from torchvision.models import ResNet18_Weights
from torchvision import transforms
import numpy as np
import cv2
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib import gridspec

import json
from .models import ScreeningData

def load_model():
    weights = ResNet18_Weights.IMAGENET1K_V1
    model = models.resnet18(weights=weights)
    num_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Linear(num_features, 128),
        nn.ReLU(),
        nn.Dropout(0.4),
        nn.Linear(128, 1),
    )

    model_path = 'med_user/model/trained_model_3.pth'
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu'), weights_only=True))
    model.eval()
    return model

MODEL = load_model()

LABELS = {0: 'Benign', 1: 'Malignant'}

def predict(screening_id):
    try:
        obj = ScreeningData.objects.get(id=screening_id)
        matrix = np.array(json.loads(obj.matrix_json))
        print("Loaded matrix from DB:", matrix.shape)

        # Check for invalid matrix
        if np.all(matrix <= 0):
            print("[predict()] WARNING: Matrix is empty or invalid, returning 'Benign' by default")
            return "Benign", "", 0.0 
        
        # Check for invalid readings
        if np.any(matrix == -1):
            return "Invalid", "", 0.0

        flat = matrix.flatten().astype(np.float32)

        flat_norm = (flat - np.min(flat)) / (np.max(flat) - np.min(flat) + 1e-6)

        repeat_factor = (224 * 224) // len(flat_norm)
        echo_array = np.tile(flat_norm, repeat_factor + 1)
        echo_array = echo_array[:224 * 224]

        img_array = echo_array.reshape(224, 224)

        image = Image.fromarray((img_array * 255).astype(np.uint8)).convert('RGB')

        visualization_path = save_upsampled_visualization(matrix, img_array, screening_id)

        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5],
                                 std=[0.5, 0.5, 0.5])
        ])

        image_tensor = transform(image).unsqueeze(0)

        with torch.no_grad():
            outputs = MODEL(image_tensor)
            outputs = torch.sigmoid(outputs)
            preds = (outputs > 0.5).int()

        score = outputs.item()
        prediction_label = LABELS[preds.item()]

        print(f"[predict()] Matrix: {matrix}")
        print(f"[predict()] Model raw output: {score:.2f}")
        print(f"[predict()] Predicted class: {prediction_label}")

        return prediction_label, visualization_path, score

    except Exception as e:
        print(f"[predict()] ERROR: {e}")
        return "Error", None
    
def save_upsampled_visualization(original_matrix, upsampled_array, screening_id):
    plt.figure(figsize=(12, 6))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 3])
    
    ax1 = plt.subplot(gs[0])
    cax1 = ax1.matshow(original_matrix, cmap='viridis')
    plt.colorbar(cax1, ax=ax1)
    ax1.set_title("Original 3x3 Matrix")
    ax1.set_xticks(range(3))
    ax1.set_yticks(range(3))
    
    ax2 = plt.subplot(gs[1])
    cax2 = ax2.imshow(upsampled_array, cmap='viridis', interpolation='nearest')
    plt.colorbar(cax2, ax=ax2)
    ax2.set_title("Upsampled 224x224 Input")
    
    # Save to media folder
    import os
    from django.conf import settings
    
    viz_dir = os.path.join(settings.MEDIA_ROOT, 'visualizations')
    os.makedirs(viz_dir, exist_ok=True)
    
    filename = f"upsampled_{screening_id}.png"
    filepath = os.path.join(viz_dir, filename)
    plt.savefig(filepath, bbox_inches='tight', dpi=100)
    plt.close()
    
    return os.path.join('visualizations', filename)
