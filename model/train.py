"""
train.py
--------
Training script for FarmRakshak EfficientNet-B0 crop lodging classifier.
Run this on Google Colab (free T4 GPU) using the dataset instructions below.

DATASET STRUCTURE expected:
    data/
        train/
            healthy/      (images of healthy crops)
            mild/         (images with mild lodging)
            moderate/     (images with moderate lodging)
            severe/       (images with severe lodging)
        val/
            healthy/
            mild/
            moderate/
            severe/

FREE DATASETS:
    - PlantVillage (Kaggle): plant disease images - use as augmentation base
    - USDA Crop Monitoring: publicly available field images
    - iNaturalist: labeled crop images
    - Custom: photograph your own fields or use Google Images + manual labeling
    - Use Roboflow (free tier) to annotate and export crop images
"""

import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, models
from torchvision.models import EfficientNet_B0_Weights

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.preprocessing import get_training_transform, get_inference_transform

# ── Training Configuration ─────────────────────────────────────────────────────
CONFIG = {
    "data_dir":    "./data",          # Path to your dataset root
    "save_path":   "./model/model.pth",
    "num_classes": 4,
    "batch_size":  32,
    "num_epochs":  25,
    "lr":          1e-4,               # Fine-tuning learning rate
    "backbone_lr": 1e-5,               # Lower LR for pretrained layers
    "weight_decay": 1e-4,
    "patience":    5,                  # Early stopping patience
}

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[FarmRakshak] Using device: {DEVICE}")


def build_efficientnet(num_classes):
    """
    Load pretrained EfficientNet-B0 and replace the classifier head.
    Uses ImageNet pretrained weights for transfer learning.
    """
    model = models.efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1)

    # Freeze early feature layers to preserve low-level features
    for param in list(model.features[:5].parameters()):
        param.requires_grad = False

    # Replace classifier head
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3, inplace=True),
        nn.Linear(in_features, 512),
        nn.ReLU(inplace=True),
        nn.Dropout(p=0.2),
        nn.Linear(512, num_classes),
    )
    return model


def get_dataloaders(data_dir, batch_size):
    """Creates train and validation DataLoaders with appropriate transforms."""
    train_dataset = datasets.ImageFolder(
        root=os.path.join(data_dir, "train"),
        transform=get_training_transform()
    )
    val_dataset = datasets.ImageFolder(
        root=os.path.join(data_dir, "val"),
        transform=get_inference_transform()
    )
    train_loader = DataLoader(train_dataset, batch_size=batch_size,
                              shuffle=True, num_workers=4, pin_memory=True)
    val_loader   = DataLoader(val_dataset, batch_size=batch_size,
                              shuffle=False, num_workers=4, pin_memory=True)
    print(f"[FarmRakshak] Train samples: {len(train_dataset)} | Val samples: {len(val_dataset)}")
    print(f"[FarmRakshak] Classes: {train_dataset.classes}")
    return train_loader, val_loader


def train_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss, correct, total = 0.0, 0, 0
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * images.size(0)
        _, preds = outputs.max(1)
        correct += preds.eq(labels).sum().item()
        total   += labels.size(0)
    return total_loss / total, 100.0 * correct / total


def validate(model, loader, criterion, device):
    model.eval()
    total_loss, correct, total = 0.0, 0, 0
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            total_loss += loss.item() * images.size(0)
            _, preds = outputs.max(1)
            correct += preds.eq(labels).sum().item()
            total   += labels.size(0)
    return total_loss / total, 100.0 * correct / total


def main():
    train_loader, val_loader = get_dataloaders(CONFIG["data_dir"], CONFIG["batch_size"])
    model = build_efficientnet(CONFIG["num_classes"]).to(DEVICE)

    # Differential learning rates: backbone vs head
    backbone_params = list(model.features.parameters())
    head_params     = list(model.classifier.parameters())
    optimizer = optim.AdamW([
        {"params": backbone_params, "lr": CONFIG["backbone_lr"]},
        {"params": head_params,     "lr": CONFIG["lr"]},
    ], weight_decay=CONFIG["weight_decay"])

    # Cosine annealing LR scheduler
    scheduler = optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=CONFIG["num_epochs"], eta_min=1e-6
    )

    # Class-weighted loss to handle potential imbalance
    criterion = nn.CrossEntropyLoss()

    # Training loop with early stopping
    best_val_acc = 0.0
    patience_counter = 0

    for epoch in range(CONFIG["num_epochs"]):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, DEVICE)
        val_loss, val_acc     = validate(model, val_loader, criterion, DEVICE)
        scheduler.step()

        print(f"Epoch [{epoch+1:02d}/{CONFIG[num_epochs]}] "
              f"Train Loss: {train_loss:.4f} Acc: {train_acc:.1f}%  "
              f"Val Loss: {val_loss:.4f} Acc: {val_acc:.1f}%")

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), CONFIG["save_path"])
            print(f"  [Saved] Best model with val_acc={val_acc:.1f}%")
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= CONFIG["patience"]:
                print(f"Early stopping at epoch {epoch+1}")
                break

    print(f"Training complete. Best Val Accuracy: {best_val_acc:.1f}%")
    print(f"Model saved to: {CONFIG[save_path]}")


if __name__ == "__main__":
    main()
