import tensorflow as tf
import numpy as np
from PIL import Image
import os

class SkinModel:
    def __init__(self, model_path):
        self.model_path = model_path
        self.model = None
        self.classes = [
            "Actinic keratoses", "Basal cell carcinoma", 
            "Benign keratosis-like lesions", "Dermatofibroma", 
            "Melanocytic nevi", "Melanoma", "Vascular lesions"
        ]

    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.model = tf.keras.models.load_model(self.model_path)
                return True, "Model loaded successfully"
            except Exception as e:
                return False, f"Error loading model: {str(e)}"
        return False, "Model file not found"

    def predict(self, image_path):
        if self.model is None:
            return "Analysis Result: Model not loaded. (Simulated: Healthy Skin)"

        try:
            img = Image.open(image_path).resize((224, 224))
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            predictions = self.model.predict(img_array)
            class_idx = np.argmax(predictions[0])
            confidence = predictions[0][class_idx] * 100
            
            disease = self.classes[class_idx] if class_idx < len(self.classes) else "Unknown Condition"
            return f"{disease} (Confidence: {confidence:.2f}%)"
        except Exception as e:
            return f"Prediction Error: {str(e)}"
