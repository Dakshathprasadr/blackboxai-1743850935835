import cv2
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image
import io

# Load or create placeholder model
try:
    from models.injury_classifier import create_placeholder_model
    model = create_placeholder_model()
    print("Using placeholder model - replace with trained model for production")
    
    CLASS_NAMES = ['cut', 'burn', 'bruise', 'rash']
    SEVERITY_THRESHOLDS = {
        'cut': {'low': 0.1, 'medium': 0.5, 'high': 0.8},
        'burn': {'low': 0.2, 'medium': 0.6, 'high': 0.9},
        'bruise': {'low': 0.1, 'medium': 0.4, 'high': 0.7},
        'rash': {'low': 0.1, 'medium': 0.3, 'high': 0.6}
    }

    FIRST_AID_ADVICE = {
        'cut': {
            'low': "Clean with water and apply bandage",
            'medium': "Clean with antiseptic and apply pressure",
            'high': "Seek medical attention for deep cuts"
        },
        'burn': {
            'low': "Cool with running water for 10 minutes",
            'medium': "Apply burn cream and cover loosely",
            'high': "Seek immediate medical attention"
        },
        'bruise': {
            'low': "Apply ice pack for 15 minutes",
            'medium': "Elevate and rest the area",
            'high': "Consult doctor if severe swelling occurs"
        },
        'rash': {
            'low': "Apply mild moisturizer",
            'medium': "Use hydrocortisone cream",
            'high': "See dermatologist for persistent rash"
        }
    }
except ImportError:
    raise RuntimeError("Could not initialize image processing model")

def process_image(image_file):
    # Read and preprocess image
    img = Image.open(io.BytesIO(image_file.read()))
    img = img.convert('RGB')
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    # Make prediction
    predictions = model.predict(img_array)
    predicted_class = CLASS_NAMES[np.argmax(predictions)]
    confidence = np.max(predictions)
    
    # Determine severity
    thresholds = SEVERITY_THRESHOLDS[predicted_class]
    if confidence < thresholds['low']:
        severity = 'low'
    elif confidence < thresholds['medium']:
        severity = 'medium'
    else:
        severity = 'high'
    
    # Get first aid advice
    advice = FIRST_AID_ADVICE[predicted_class][severity]
    
    return {
        'injury_type': predicted_class,
        'confidence': float(confidence),
        'severity': severity,
        'first_aid': advice
    }