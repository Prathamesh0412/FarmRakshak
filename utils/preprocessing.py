"""
preprocessing.py
----------------
Handles all image preprocessing for FarmRakshak model inference.
Includes resizing, normalization, and optional augmentation.
"""

from PIL import Image
import torch
from torchvision import transforms
import numpy as np


# ── Constants ──────────────────────────────────────────────────────────────────
IMAGE_SIZE = 224  # EfficientNet-B0 / MobileNetV2 input size

# ImageNet normalization constants (used for pretrained model fine-tuning)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]


# ── Inference Transform (no augmentation) ─────────────────────────────────────
def get_inference_transform() -> transforms.Compose:
    """
    Returns the deterministic transform pipeline used during inference.
    Order: Resize → CenterCrop → ToTensor → Normalize
    """
    return transforms.Compose([
        transforms.Resize((IMAGE_SIZE + 32, IMAGE_SIZE + 32)),  # Slightly larger for crop
        transforms.CenterCrop(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


# ── Training Transform (with augmentation) ────────────────────────────────────
def get_training_transform() -> transforms.Compose:
    """
    Returns augmented transform pipeline used during training.
    Augmentations: random flip, rotation, brightness/contrast jitter.
    Helps model generalize across different field conditions, lighting, etc.
    """
    return transforms.Compose([
        transforms.Resize((IMAGE_SIZE + 32, IMAGE_SIZE + 32)),
        transforms.RandomCrop(IMAGE_SIZE),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.2),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(
            brightness=0.3,
            contrast=0.3,
            saturation=0.2,
            hue=0.05
        ),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


# ── Preprocessing Entry Point ──────────────────────────────────────────────────
def preprocess_image(pil_image: Image.Image) -> torch.Tensor:
    """
    Converts a PIL image to a normalized model-ready tensor.

    Args:
        pil_image: PIL.Image loaded from file or BytesIO

    Returns:
        torch.Tensor of shape [1, 3, 224, 224] (batch dimension added)
    """
    # Ensure RGB (handles grayscale or RGBA uploads)
    if pil_image.mode != "RGB":
        pil_image = pil_image.convert("RGB")

    transform = get_inference_transform()
    tensor = transform(pil_image)           # Shape: [3, 224, 224]
    tensor = tensor.unsqueeze(0)            # Shape: [1, 3, 224, 224]
    return tensor


# ── Denormalize (for Grad-CAM visualization) ───────────────────────────────────
def denormalize(tensor: torch.Tensor) -> np.ndarray:
    """
    Reverses ImageNet normalization for display/visualization.

    Args:
        tensor: Normalized tensor of shape [1, 3, H, W] or [3, H, W]

    Returns:
        NumPy array of shape [H, W, 3] with pixel values in [0, 255]
    """
    if tensor.dim() == 4:
        tensor = tensor.squeeze(0)  # Remove batch dim

    mean = torch.tensor(IMAGENET_MEAN).view(3, 1, 1)
    std  = torch.tensor(IMAGENET_STD).view(3, 1, 1)
    img  = tensor * std + mean          # Reverse normalization
    img  = img.clamp(0, 1)             # Clip to valid range
    img  = img.permute(1, 2, 0)        # CHW → HWC
    img  = (img.numpy() * 255).astype(np.uint8)
    return img
