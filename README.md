
---

# 🔒 Face Recognition-Based Smart Door Lock System

A smart and secure door lock system using **ESP32-CAM** and **Raspberry Pi Zero 2 W**, powered by **OpenCV (Haar Cascade + LBPH)** for real-time face recognition. The system identifies authorized users and automatically unlocks a **solenoid lock**, providing seamless, contactless access control.

---

## 🧠 Project Overview

This project combines **embedded AI** and **IoT** to create a compact, intelligent door locking system.

* The **ESP32-CAM** captures live video and streams it to the **Raspberry Pi Zero 2 W**.
* The **Raspberry Pi** performs **face detection** using Haar Cascades and **recognition** using LBPH.
* On successful recognition, it sends an **unlock signal** to the ESP32 via serial.
* The **ESP32-CAM** then triggers a **relay** that powers the **solenoid lock** for a few seconds.

Power is supplied by **two 18650 Li-ion batteries** (7.4V total) through an **LM2596 buck converter**, maintaining a stable 5V output for all modules.

---

## ⚙️ Hardware Components

| Component                    | Quantity | Description                          |
| ---------------------------- | -------- | ------------------------------------ |
| Raspberry Pi Zero 2 W        | 1        | Main controller for face recognition |
| ESP32-CAM (OV2640)           | 1        | Captures live video feed             |
| Solenoid Lock (5V/12V)       | 1        | Physical locking mechanism           |
| Relay Module (5V, 1-Channel) | 1        | Controls solenoid lock               |
| LM2596 Buck Converter        | 1        | Converts 7.4V → 5V                   |
| 18650 Li-ion Batteries       | 2        | Power source                         |
| Battery Holder (2S)          | 1        | Mounts batteries in series           |
| Jumper Wires, Connectors     | —        | Circuit connections                  |
| Enclosure                    | 1        | Final assembly case                  |

---

## 🧩 Working Principle

1. **Face Detection:** Haar Cascade detects human faces.
2. **Recognition:** LBPH compares faces with the trained model.
3. **Communication:** If a match is found, Pi sends `'U'` to ESP32 via serial.
4. **Unlocking:** ESP32 activates relay → solenoid unlocks → door opens briefly.
5. **Locking:** After 3 seconds, ESP32 deactivates relay, re-locking the door.

---

## 🗂️ Project Folder Structure

```
face_lock_system/
│
├── raspberry_pi/
│   ├── haarcascade_frontalface_default.xml
│   ├── dataset/
│   │   └── user1/
│   ├── train.py
│   ├── face_recognition.py
│   └── trainer.yml
│
└── esp32_cam/
    └── door_control.ino
```

---

## 🧰 Software Setup

### 🔹 On Raspberry Pi

1. **Install dependencies:**

   ```bash
   sudo apt update
   sudo apt install python3-opencv python3-serial
   ```

2. **Clone the repository:**

   ```bash
   git clone https://github.com/<your-username>/face_lock_system.git
   cd face_lock_system/raspberry_pi
   ```

3. **Train the face model:**

   ```bash
   python3 train.py
   ```

4. **Run recognition script:**

   ```bash
   python3 face_recognition.py
   ```

---

### 🔹 On ESP32-CAM

1. Open `door_control.ino` in **Arduino IDE**.
2. Select **AI Thinker ESP32-CAM** board.
3. Choose correct COM port & upload via **FTDI programmer (3.3V)**.
4. Connect **GPIO 12 → Relay IN**, and ensure **common ground** with the Pi.

---

## 🖼️ Setup & Upload Images

### 🧩 Step 1: Capture Images for Training

You can use your webcam or the ESP32-CAM stream to collect images.
Run this Python script to save faces:

```python
import cv2, os

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
cam = cv2.VideoCapture(0)
user_id = input("Enter user ID: ")

os.makedirs(f"dataset/user{user_id}", exist_ok=True)
count = 0

while True:
    ret, frame = cam.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        count += 1
        cv2.imwrite(f"dataset/user{user_id}/{count}.jpg", gray[y:y+h, x:x+w])
        cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)
        cv2.imshow('Capturing Faces', frame)
    if cv2.waitKey(1) & 0xFF == ord('q') or count >= 50:
        break

cam.release()
cv2.destroyAllWindows()
```

This saves ~50 images per user in `/dataset/user<ID>/`.

### 🧩 Step 2: Train Your Model

After capturing faces:

```bash
python3 train.py
```

This generates `trainer.yml` — your face recognition model.

### 🧩 Step 3: Test Recognition

Run:

```bash
python3 face_recognition.py
```

If your face matches the trained model, the Pi sends the unlock signal to ESP32.

---

## 🔌 Circuit Overview

* **ESP32 GPIO 12 → Relay IN**
* **Relay COM → Battery +**, **NO → Solenoid +**, **Solenoid – → Battery –**
* **Pi TX → ESP32 RX**, **Pi RX → ESP32 TX**, **GND Common**
* **Battery (7.4V) → LM2596 → 5V Output → Pi, ESP32, Relay**

---

## ✨ Features

* Real-time face recognition using OpenCV
* Offline operation for privacy
* Battery-powered and portable design
* Modular and IoT-ready architecture

---

## 🚀 Future Improvements

* Add deep-learning-based recognition (FaceNet or Dlib)
* Mobile app integration for remote access
* Cloud logging and multi-user management
* Add motion detection or buzzer alarm

---

## 📜 License

This project is released under the **MIT License** — free to use and modiffy.

---

