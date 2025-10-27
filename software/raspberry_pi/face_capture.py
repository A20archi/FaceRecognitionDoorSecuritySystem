import cv2
import os

# Load the Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Create dataset directory if it doesn't exist
dataset_dir = "dataset"
if not os.path.exists(dataset_dir):
    os.makedirs(dataset_dir)

# Ask for user ID and name
user_id = input("Enter user ID: ")
user_name = input("Enter user name: ")

# Create a folder for the user
user_dir = os.path.join(dataset_dir, f"{user_id}_{user_name}")
if not os.path.exists(user_dir):
    os.makedirs(user_dir)

# Start webcam
cam = cv2.VideoCapture(0)
if not cam.isOpened():
    print("Error: Could not access webcam.")
    exit()

print("\n[INFO] Capturing face images. Look at the camera and wait ...")
count = 0

while True:
    ret, frame = cam.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(100, 100))

    for (x, y, w, h) in faces:
        count += 1
        face = gray[y:y + h, x:x + w]
        cv2.imwrite(os.path.join(user_dir, f"{user_id}_{count}.jpg"), face)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.putText(frame, f"Image {count}/100", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow('Face Capture', frame)

    # Press 'q' to quit or automatically stop after 100 images
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    elif count >= 100:
        break

print("\n[INFO] Face capture complete. Exiting ...")

cam.release()
cv2.destroyAllWindows()
