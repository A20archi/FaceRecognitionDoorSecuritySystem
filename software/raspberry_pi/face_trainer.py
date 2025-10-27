import cv2
import os
import numpy as np

# Paths
dataset_path = 'software/raspberry_pi/dataset'
trainer_path = 'software/raspberry_pi/trainer'
cascade_path = 'software/raspberry_pi/haarcascade_frontalface_default.xml'

# Load face detector
face_cascade = cv2.CascadeClassifier(cascade_path)
recognizer = cv2.face.LBPHFaceRecognizer_create()

faces = []
ids = []

print("[INFO] Loading dataset...")

# Loop through all subfolders (e.g., 1_Saptarshi, 2_Rahul)
for user_folder in os.listdir(dataset_path):
    folder_path = os.path.join(dataset_path, user_folder)
    if not os.path.isdir(folder_path):
        continue

    # Extract numeric ID (e.g., "1" from "1_Saptarshi")
    try:
        user_id = int(user_folder.split('_')[0])
    except ValueError:
        print(f"[WARNING] Skipping folder {user_folder} — invalid format.")
        continue

    print(f"[INFO] Processing user {user_id}: {user_folder}")

    valid_faces = 0
    for file in os.listdir(folder_path):
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            img_path = os.path.join(folder_path, file)
            gray = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if gray is None:
                continue

            faces_detected = face_cascade.detectMultiScale(gray, 1.1, 5)
            for (x, y, w, h) in faces_detected:
                faces.append(gray[y:y+h, x:x+w])
                ids.append(user_id)
                valid_faces += 1

    print(f"[INFO] User {user_id}: {valid_faces} valid faces added.")

# Check if we have enough data
if len(faces) < 5:
    raise ValueError("[ERROR] Not enough usable face data. Please capture more samples!")

print(f"[INFO] Training model with {len(faces)} face samples...")
recognizer.train(faces, np.array(ids))

# Ensure trainer directory exists
os.makedirs(trainer_path, exist_ok=True)
model_path = os.path.join(trainer_path, 'lbph_trainer.yml')
recognizer.save(model_path)

print(f"[✅ SUCCESS] Training complete! Model saved to: {model_path}")
