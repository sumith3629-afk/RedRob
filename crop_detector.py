import io
import time
import numpy as np
from PIL import Image

class MobileNetV2Classifier:
    """
    Simulates a MobileNetV2 convolutional neural network inference pipeline
    for edge crop disease classification. Uses pure NumPy for tensor operations
    and channel preprocessing.
    """
    def __init__(self):
        print("[TF-CORE] Initializing MobileNetV2 classifier model...")
        print("[TF-CORE] Loading pre-trained ImageNet + PlantVillage weights into memory...")
        time.sleep(0.3)
        print("[TF-CORE] MobileNetV2 model backbone successfully compiled.")

    def preprocess_input(self, image: Image.Image) -> np.ndarray:
        """
        Executes standard MobileNetV2 input channel transformations:
        1. Resize input to (224, 224)
        2. Convert to float32 NumPy array
        3. Normalize pixel values from [0, 255] to [-1.0, 1.0] range: (x / 127.5) - 1.0
        4. Add batch dimension: (1, 224, 224, 3)
        """
        print(f"[TF-CORE] Preprocessing raw image. Size: {image.size}, Format: {image.format}, Mode: {image.mode}")
        
        # 1. Resize
        resized_img = image.resize((224, 224))
        print(f"[TF-CORE] Resized spatial dimensions: {resized_img.size}")

        # 2. Convert to NumPy
        img_array = np.array(resized_img, dtype=np.float32)
        print(f"[TF-CORE] Cast image to tensor with shape: {img_array.shape} and dtype: {img_array.dtype}")

        # Handle grayscale or RGBA by keeping only RGB (3 channels)
        if len(img_array.shape) == 2:  # Grayscale
            img_array = np.stack([img_array] * 3, axis=-1)
            print(f"[TF-CORE] Stacked grayscale channels. New shape: {img_array.shape}")
        elif img_array.shape[2] == 4:  # RGBA
            img_array = img_array[:, :, :3]
            print(f"[TF-CORE] Discarded alpha channel. New shape: {img_array.shape}")

        # 3. Channel Normalization
        normalized_tensor = (img_array / 127.5) - 1.0
        print(f"[TF-CORE] Preprocessed channel values. Min: {normalized_tensor.min():.4f}, Max: {normalized_tensor.max():.4f}")

        # 4. Expand Batch Dimension
        batch_tensor = np.expand_dims(normalized_tensor, axis=0)
        print(f"[TF-CORE] Completed input tensor assembly. Final Batch Shape: {batch_tensor.shape}")

        return batch_tensor

    def predict(self, image_bytes: bytes) -> dict:
        """
        Runs the full simulated TensorFlow Keras inference pipeline on raw image bytes.
        """
        print("[TF-CORE] --- Starting Inference Pipeline ---")
        try:
            image = Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            print(f"[TF-CORE] [ERROR] Failed to load image bytes: {e}")
            return {
                "status": "error",
                "message": f"Invalid image file: {e}"
            }

        # Run preprocessing
        _ = self.preprocess_input(image)

        # Simulate forward pass propagation latency through the inverted residual blocks
        print("[TF-CORE] Forward propagating through 15 Inverted Residual Blocks (Depthwise & Pointwise Conv)...")
        time.sleep(0.4)
        print("[TF-CORE] Executing GlobalAveragePooling2D operation...")
        time.sleep(0.1)
        print("[TF-CORE] Forwarding output through final Dense layer (Softmax activation)...")
        time.sleep(0.1)

        # Deterministic output payload per specifications
        payload = {
            "status": "success",
            "detected_class": "Tomato__Target_Spot",
            "confidence_score": 0.946,
            "crop_type": "Tomato",
            "severity": "High"
        }
        
        print(f"[TF-CORE] Classifier Output: {payload}")
        print("[TF-CORE] --- Inference Pipeline Completed ---")
        return payload
