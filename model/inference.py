"""
inference.py
------------
Loads the trained FarmRakshak model and runs inference on a PIL image.
Also includes optional Grad-CAM visualization for explainability.
"""

import os, sys, json, torch, torch.nn as nn, numpy as np
from PIL import Image
from torchvision import models
from typing import Optional, Tuple, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.preprocessing import preprocess_image, denormalize
from utils.severity import get_severity_score

DEFAULT_CLASS_NAMES = ["healthy", "mild", "moderate", "severe"]
MODEL_PATH  = os.path.join(os.path.dirname(__file__), "model.pth")
METADATA_PATH = os.path.join(os.path.dirname(__file__), "model_metadata.json")
DEVICE      = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class ModelNotReadyError(RuntimeError):
    """Raised when the trained model artifacts are missing or invalid."""


def build_model(num_classes=4):
    """Builds EfficientNet-B0 with custom head for crop lodging classification."""
    model = models.efficientnet_b0(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3, inplace=True),
        nn.Linear(in_features, 512),
        nn.ReLU(inplace=True),
        nn.Dropout(p=0.2),
        nn.Linear(512, num_classes),
    )
    return model


_model_cache = None
_class_names_cache = None

def load_model():
    """Loads trained model from disk with singleton caching."""
    global _model_cache, _class_names_cache
    if _model_cache is not None:
        return _model_cache, _class_names_cache
    if not os.path.exists(MODEL_PATH):
        raise ModelNotReadyError(
            f"Trained model not found at {MODEL_PATH}. Train the model first using model/train.py."
        )

    class_names = DEFAULT_CLASS_NAMES
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        meta_class_names = metadata.get("class_names")
        if meta_class_names:
            class_names = meta_class_names
    if len(class_names) < 2:
        raise ModelNotReadyError(
            f"Invalid class_names in metadata: {class_names}. Need at least 2 classes."
        )

    model = build_model(len(class_names))
    state_dict = torch.load(MODEL_PATH, map_location=DEVICE)
    model.load_state_dict(state_dict)
    print(f"[FarmRakshak] Model loaded from {MODEL_PATH}")
    model.to(DEVICE)
    model.eval()
    _model_cache = model
    _class_names_cache = class_names
    return model, class_names


class GradCAM:
    """Gradient-weighted Class Activation Mapping for explainability."""
    def __init__(self, model):
        self.model = model
        self.gradients = None
        self.activations = None
        target_layer = self.model.features[-1]
        target_layer.register_forward_hook(lambda m, i, o: setattr(self, "activations", o.detach()))
        target_layer.register_full_backward_hook(lambda m, gi, go: setattr(self, "gradients", go[0].detach()))

    def generate(self, input_tensor, class_idx):
        self.model.zero_grad()
        output = self.model(input_tensor)
        one_hot = torch.zeros_like(output)
        one_hot[0, class_idx] = 1.0
        output.backward(gradient=one_hot)
        weights = self.gradients.mean(dim=[2, 3], keepdim=True)
        cam = (weights * self.activations).sum(dim=1, keepdim=True)
        cam = torch.relu(cam).squeeze()
        cam = cam - cam.min()
        if cam.max() > 0:
            cam = cam / cam.max()
        return cam.cpu().numpy()


def overlay_heatmap(original_image, cam, alpha=0.45):
    """Overlays Grad-CAM heatmap on the original image."""
    import cv2
    import matplotlib.cm as cm
    img_rgb = np.array(original_image.convert("RGB").resize((224, 224)))
    cam_resized = cv2.resize(cam, (224, 224))
    colormap = cm.get_cmap("jet")
    heatmap = (colormap(cam_resized)[:, :, :3] * 255).astype(np.uint8)
    blended = (alpha * heatmap + (1 - alpha) * img_rgb).astype(np.uint8)
    return blended


def predict(pil_image, generate_gradcam=True):
    """Full inference pipeline: preprocess, predict, postprocess."""
    model, class_names = load_model()
    input_tensor = preprocess_image(pil_image).to(DEVICE)
    with torch.set_grad_enabled(generate_gradcam):
        logits = model(input_tensor)
    probs = torch.softmax(logits, dim=1).squeeze(0)
    probs_list = probs.tolist()
    class_probs = {name: round(probs_list[i] * 100, 1)
                   for i, name in enumerate(class_names)}
    top_idx = probs.argmax().item()
    predicted_class = class_names[top_idx]
    confidence = probs_list[top_idx]
    severity_pct = get_severity_score(predicted_class, confidence)
    result = {
        "predicted_class": predicted_class,
        "confidence":      round(confidence * 100, 1),
        "severity_pct":    round(severity_pct, 1),
        "class_probs":     class_probs,
        "gradcam_overlay": None,
    }
    if generate_gradcam:
        try:
            class_idx = class_names.index(predicted_class)
            gcam = GradCAM(model)
            cam = gcam.generate(input_tensor, class_idx)
            result["gradcam_overlay"] = overlay_heatmap(pil_image, cam)
        except Exception as e:
            print(f"[GradCAM] Could not generate heatmap: {e}")
    return result
