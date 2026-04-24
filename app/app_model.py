import os
import numpy as np
from PIL import Image

# Force NVIDIA High-Performance mode
os.environ['__NV_PRIME_RENDER_OFFLOAD'] = '1'
os.environ['__GLX_VENDOR_LIBRARY_NAME'] = 'nvidia'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf

class SkinModel:
    def __init__(self, model_filename="skin_model_v2.h5"):
        # Get the absolute path of the directory Skinalyse1
        # This file is in Skinalyse1/app/app_model.py
        current_file_path = os.path.abspath(__file__) 
        app_dir = os.path.dirname(current_file_path)
        self.root_dir = os.path.dirname(app_dir) 
        
        self.model_path = os.path.join(self.root_dir, model_filename)
        
        self.model = None
        self.classes = [
            "Actinic keratoses", "Basal cell carcinoma", 
            "Benign keratosis-like lesions", "Dermatofibroma", 
            "Melanocytic nevi", "Melanoma", "Vascular lesions"
        ]
        
        self._setup_hardware()

    def _setup_hardware(self):
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            try:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                print(f"[SUCCESS] RTX 3050 Initialized.")
            except RuntimeError as e:
                print(f"[ERROR] GPU Config: {e}")
        else:
            print("[WARNING] Running on CPU.")

    def load_model(self):
        if not os.path.exists(self.model_path):
            print(f"[CRITICAL] Model NOT FOUND at: {self.model_path}")
            return False, f"File missing at {self.model_path}"
        
        try:
            # Using compile=False for faster loading and fewer errors
            self.model = tf.keras.models.load_model(self.model_path, compile=False)
            print(f"[SUCCESS] Model loaded from {self.model_path}")
            return True, "Model Loaded"
        except Exception as e:
            print(f"[ERROR] TF Load Failure: {e}")
            return False, str(e)

    def predict(self, image_path):
        if self.model is None:
            # This is what's hitting your PDF
            return "Error", "Model not loaded in memory"

        try:
            img = Image.open(image_path).convert('RGB')
            img = img.resize((224, 224))
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            predictions = self.model.predict(img_array, verbose=0)
            idx = np.argmax(predictions[0])
            conf = float(predictions[0][idx]) * 100
            
            return self.classes[idx], f"{conf:.2f}%"
        except Exception as e:
            return "Inference Error", str(e)