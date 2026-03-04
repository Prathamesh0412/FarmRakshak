# FarmRakshak - AI Crop Lodging Detection

Multilingual (English/Hindi/Marathi) Streamlit app using EfficientNet-B0.

## Classes
- Healthy (0%) | Mild (15%) | Moderate (35%) | Severe (65%+)

## Run Locally
  pip install -r requirements.txt
  streamlit run app.py

## Train (Google Colab Free GPU)
  Runtime > T4 GPU > python model/train.py

## Deploy Free
  HuggingFace Spaces or Streamlit Community Cloud

## Dataset
  data/train/{healthy,mild,moderate,severe}/
  Kaggle PlantVillage, Roboflow (free), USDA NASS