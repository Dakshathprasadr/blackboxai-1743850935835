import numpy as np
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense
import os

def create_placeholder_model():
    """Create a simple placeholder model for demonstration"""
    input_layer = Input(shape=(224, 224, 3))
    x = Conv2D(32, (3,3), activation='relu')(input_layer)
    x = MaxPooling2D((2,2))(x)
    x = Conv2D(64, (3,3), activation='relu')(x)
    x = MaxPooling2D((2,2))(x)
    x = Flatten()(x)
    output = Dense(4, activation='softmax')(x)
    
    model = Model(inputs=input_layer, outputs=output)
    model.compile(optimizer='adam', loss='categorical_crossentropy')
    return model

def save_placeholder_model():
    """Save the placeholder model to disk"""
    os.makedirs('models', exist_ok=True)
    model = create_placeholder_model()
    model.save('models/injury_classifier.h5')

if __name__ == '__main__':
    save_placeholder_model()
    print("Placeholder model saved to models/injury_classifier.h5")