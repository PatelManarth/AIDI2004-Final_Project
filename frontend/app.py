import streamlit as st
import cv2
import requests
import numpy as np
from PIL import Image
import time
from fpdf import FPDF
import datetime

st.title("Dangerous Object Detection")

event_name = st.text_input("Enter Event Name")
run = st.checkbox('Run')
FRAME_WINDOW = st.image([])

def detect_objects(frame):
    _, img_encoded = cv2.imencode('.jpg', frame)
    try:
        response = requests.post("http://localhost:8000/detect", files={"file": ("frame.jpg", img_encoded.tobytes(), "image/jpeg")})
        response.raise_for_status()  # Raise an HTTPError for bad responses
        
        st.write("Backend response status:", response.status_code)
        st.write("Backend response content:", response.content)

        detections = response.json().get('detections', [])
        return detections
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return []
    except ValueError:
        st.error("Invalid JSON response")
        return []

cap = cv2.VideoCapture(0)
results = []

while run:
    ret, frame = cap.read()
    if not ret:
        break

    # Capture frame every 5 seconds
    if int(time.time()) % 5 == 0:
        detections = detect_objects(frame)

        for detection in detections:
            x1, y1, x2, y2 = int(detection['xmin']), int(detection['ymin']), int(detection['xmax']), int(detection['ymax'])
            label = detection['name']
            confidence = detection['confidence']
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{label} {confidence:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Save the detection result
            results.append({
                "frame": cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                "detection": detection
            })

    FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

cap.release()

# Save results to PDF
if st.button("Save Results to PDF"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    for result in results:
        frame = result["frame"]
        detection = result["detection"]
        label = detection['name']
        confidence = detection['confidence']

        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Detection: {label} with confidence {confidence:.2f}", ln=True)
        img = Image.fromarray(frame)
        img_path = f"temp_{int(time.time())}.png"
        img.save(img_path)
        pdf.image(img_path, x=10, y=None, w=100)

    # Save the PDF with the current date, time, and event name
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_file_name = f"{now}_{event_name}.pdf"
    pdf.output(pdf_file_name)

    st.success(f"Results saved to {pdf_file_name}")
