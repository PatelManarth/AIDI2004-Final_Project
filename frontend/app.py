# frontend/app.py
import streamlit as st
import cv2
import requests
import numpy as np
from PIL import Image

st.title("Dangerous Object Detection")

run = st.checkbox('Run')
FRAME_WINDOW = st.image([])

def detect_objects(frame):
    _, img_encoded = cv2.imencode('.jpg', frame)
    response = requests.post("http://localhost:8000/detect", files={"file": ("frame.jpg", img_encoded.tobytes(), "image/jpeg")})
    return response.json().get('detections', [])

cap = cv2.VideoCapture(0)

while run:
    ret, frame = cap.read()
    if not ret:
        break

    detections = detect_objects(frame)

    for detection in detections:
        x1, y1, x2, y2 = int(detection['xmin']), int(detection['ymin']), int(detection['xmax']), int(detection['ymax'])
        label = detection['name']
        confidence = detection['confidence']
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"{label} {confidence:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

cap.release()