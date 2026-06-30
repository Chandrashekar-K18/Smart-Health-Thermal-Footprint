import os
import cv2
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle

DATASET = "datasets"

X = []
Y = []

classes = ["Healthy", "Diabetic"]

print("Starting robust feature extraction...")

for label, name in enumerate(classes):
    path = os.path.join(DATASET, name)
    if not os.path.exists(path):
        continue
        
    for file in os.listdir(path):
        img_path = os.path.join(path, file)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            continue

        # 1. Standardize image dimensions
        img = cv2.resize(img, (60, 60))
        
        # 2. Segment the footprint vertically into 3 physiological zones (20 pixels each)
        toe_zone = img[0:20, :]
        mid_zone = img[20:40, :]
        heel_zone = img[40:60, :]
        
        # 3. Compute invariant numeric features instead of raw pixels
        features = [
            np.mean(img),        # Global average intensity
            np.max(img),         # Peak hotspot temperature
            np.mean(toe_zone),   # Forefoot metabolic rate
            np.max(toe_zone),    # Toe local peak
            np.mean(mid_zone),   # Plantar arch metabolic rate
            np.max(mid_zone),    # Arch local peak
            np.mean(heel_zone),  # Heel metabolic rate
            np.max(heel_zone),   # Heel local peak
            np.std(img)          # Thermal variation index
        ]
        
        X.append(features)
        Y.append(label)

X = np.array(X)
Y = np.array(Y)

print(f"Extraction complete. Training dataset shape: {X.shape}")
print("Training started...")

# Hyperparameters set to prevent overfitting
model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
model.fit(X, Y)

# Ensure directory exists and save the trained intelligence
os.makedirs("model", exist_ok=True)
pickle.dump(model, open("model/thermal_model.pkl", "wb"))

print("SUCCESS: Model trained and saved to model/thermal_model.pkl")