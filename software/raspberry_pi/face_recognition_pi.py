# software/raspberry_pi/face_recognition_pi.py
import cv2
import os
import time
import threading
import numpy as np
import tkinter as tk
from tkinter import ttk

# --------------------------
# Paths (robust, relative)
# --------------------------
base_dir = os.path.dirname(os.path.abspath(__file__))
dataset_dir = os.path.join(base_dir, "dataset")
trainer_file = os.path.join(base_dir, "trainer", "lbph_trainer.yml")
cascade_file = os.path.join(base_dir, "haarcascade_frontalface_default.xml")

# --------------------------
# Config
# --------------------------
CONFIDENCE_THRESHOLD = 60.0   # lower = stricter (0 = perfect match)
UNLOCK_COOLDOWN = 5.0         # seconds between unlocks
UNLOCK_DISPLAY_SECONDS = 3.0  # popup duration

# --------------------------
# Helper: Build names map from dataset folders
# dataset folders expected: 1_Saptarshi, 2_Avika, ...
# --------------------------
def build_names_map(dataset_path):
    names_map = {}
    if not os.path.exists(dataset_path):
        return names_map
    for folder in os.listdir(dataset_path):
        folder_path = os.path.join(dataset_path, folder)
        if not os.path.isdir(folder_path):
            continue
        # Expect format "ID_Name" or "ID"
        parts = folder.split('_', 1)
        id_part = parts[0]
        try:
            uid = int(id_part)
        except ValueError:
            continue
        display_name = parts[1] if len(parts) > 1 else f"User{uid}"
        names_map[uid] = display_name
    return names_map

# --------------------------
# Helper: transient unlock popup using Tkinter
# --------------------------
def show_unlock_popup(name, duration=UNLOCK_DISPLAY_SECONDS):
    # run in separate thread because Tk mainloop is blocking
    def _popup():
        root = tk.Tk()
        root.title("Door Status")
        root.geometry("300x150")
        root.resizable(False, False)
        # center window on screen
        root.eval('tk::PlaceWindow . center')

        frm = ttk.Frame(root, padding=12)
        frm.pack(fill="both", expand=True)

        lbl_title = ttk.Label(frm, text="ACCESS GRANTED", font=("Helvetica", 14, "bold"), foreground="green")
        lbl_title.pack(pady=(6, 6))

        lbl_user = ttk.Label(frm, text=f"{name}", font=("Helvetica", 12))
        lbl_user.pack(pady=(0, 8))

        lbl_info = ttk.Label(frm, text="Door Unlocked", font=("Helvetica", 11))
        lbl_info.pack()

        # keep popup for duration then destroy
        root.after(int(duration * 1000), root.destroy)
        root.mainloop()

    t = threading.Thread(target=_popup, daemon=True)
    t.start()

# --------------------------
# Validate files
# --------------------------
if not os.path.exists(cascade_file):
    raise FileNotFoundError(f"Haar cascade not found: {cascade_file}")

if not os.path.exists(trainer_file):
    raise FileNotFoundError(f"Trained model not found: {trainer_file}\nRun the trainer script first.")

# --------------------------
# Load cascade and recognizer
# --------------------------
face_cascade = cv2.CascadeClassifier(cascade_file)
if face_cascade.empty():
    raise RuntimeError(f"Failed to load Haar cascade from {cascade_file}")

recognizer = cv2.face.LBPHFaceRecognizer_create()
# recognizer.read returns nothing but raises if file unreadable
recognizer.read(trainer_file)

# Build names map
names = build_names_map(dataset_dir)
if not names:
    # fallback names if dataset folder absent or poorly named
    names = {1: "User1"}

print("[INFO] Names mapping:", names)
print("[INFO] Starting face recognition. Press ESC to quit.")

# --------------------------
# Start webcam
# --------------------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Cannot open webcam (index 0).")

# set smaller resolution for speed (optional)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

last_unlock_time = 0.0

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Frame not received from camera, retrying...")
            time.sleep(0.1)
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(60, 60)
        )

        # default overlay text
        overlay_text = ""

        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]

            # predict
            try:
                id_pred, confidence = recognizer.predict(face_roi)
            except Exception as e:
                # in rare cases recognizer.predict may fail
                print("[ERROR] recognizer.predict failed:", e)
                continue

            confidence_pct = round(100 - confidence)
            if confidence < CONFIDENCE_THRESHOLD:
                name = names.get(id_pred, f"User{id_pred}")
                overlay_text = f"ACCESS GRANTED: {name} ({confidence_pct}%)"
                color = (0, 220, 0)

                now = time.time()
                if now - last_unlock_time >= UNLOCK_COOLDOWN:
                    last_unlock_time = now
                    print(f"[ACCESS GRANTED] {name} recognized ({confidence_pct}%) - unlocking")
                    # simulate unlock popup
                    show_unlock_popup(name, duration=UNLOCK_DISPLAY_SECONDS)
                else:
                    print(f"[INFO] Recognized {name} but in cooldown ({round(now - last_unlock_time,1)}s)")

            else:
                name = "Unknown"
                overlay_text = f"ACCESS DENIED: {name} ({confidence_pct}%)"
                color = (0, 0, 255)
                print(f"[ACCESS DENIED] ID={id_pred} conf={confidence_pct}%")

            # draw rectangle and text
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, overlay_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # show overall instruction text
        cv2.putText(frame, "Press ESC to exit", (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        cv2.imshow("Face Recognition Door Lock (Simulation)", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Exited cleanly.")
