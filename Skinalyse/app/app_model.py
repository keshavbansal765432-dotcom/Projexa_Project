import os
import numpy as np
from PIL import Image

# Force TensorFlow to ignore the Keras import error by trying multiple paths
try:
    import tensorflow as tf
    from tensorflow import keras
except (ImportError, AttributeError):
    try:
        import keras
    except ImportError:
        # Final fallback: if nothing works, we'll try to load via tf.keras.models
        import tensorflow.keras as keras

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
        if not os.path.exists(self.model_path):
            return False, f"Model file not found at: {self.model_path}"
        
        try:
            # First attempt: Standard TF loading
            self.model = tf.keras.models.load_model(self.model_path, compile=False)
            return True, "Model loaded successfully"
        except Exception as e:
            try:
                # Second attempt: Standalone Keras loading
                import keras
                self.model = keras.models.load_model(self.model_path, compile=False)
                return True, "Model loaded via Standalone Keras"
            except:
                return False, f"Keras Import Error: {str(e)}"

    def predict(self, image_path):
        if self.model is None:
            return "Analysis Result: Model not loaded."

        try:
            img = Image.open(image_path).convert('RGB')
            img = img.resize((224, 224))
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            predictions = self.model.predict(img_array)
            class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][class_idx]) * 100
            
            disease = self.classes[class_idx] if class_idx < len(self.classes) else "Unknown"
            return f"{disease} ({confidence:.2f}%)"
        except Exception as e:
            return f"Prediction Error: {str(e)}"