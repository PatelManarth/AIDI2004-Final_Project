import streamlit as st
import cv2
import requests
import numpy as np
from PIL import Image
from fpdf import FPDF
import datetime
import time
import os

# Set the title of the Streamlit app
st.title("Dangerous Object Detection")

# Input fields and controls in Streamlit
event_name = st.text_input("Enter Event Name")
start_detection = st.button('Start Detection', key='start_button')

FRAME_WINDOW = st.image([])  # To display the video frames
results = []
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Global variable to track the state of detection
detection_running = False

def detect_objects(frame):
    try:
        _, img_encoded = cv2.imencode('.jpg', frame)
        response = requests.post(
            "http://localhost:8000/detect",
            files={"file": ("frame.jpg", img_encoded.tobytes(), "image/jpeg")}
        )

        if response.status_code != 200:
            st.error(f"API Error: {response.status_code} - {response.json().get('detail', 'No details available')}")
            return []

        return response.json().get('detections', [])

    except requests.exceptions.ConnectionError as e:
        st.error("Failed to connect to the backend. Please ensure it is running.")
        return []

    except requests.exceptions.Timeout as e:
        st.error("Request to the backend timed out. Please try again.")
        return []

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while making the request: {str(e)}")
        return []

    except ValueError as e:
        st.error(f"Failed to decode JSON response: {str(e)}")
        return []

def save_pdf():
    try:
        for result in results:
            frame = result["frame"]
            detection = result["detection"]
            label = detection['name']
            confidence = detection['confidence']
            timestamp = result["timestamp"]

            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Detection: {label} with confidence {confidence:.2f} at {timestamp}", ln=True)

            img = Image.fromarray(frame)
            img_path = f"temp_{int(time.time())}.png"
            img.save(img_path)
            pdf.image(img_path, x=10, y=None, w=100)
            os.remove(img_path)  # Clean up the temporary image file

        results.clear()

    except Exception as e:
        st.error(f"Failed to save PDF: {str(e)}")

def finalize_pdf():
    try:
        # Create the "SAVED PDF" folder if it doesn't exist
        save_folder = os.path.join(os.getcwd(), "../SAVED-PDFs")
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        # Save the PDF with the current date, time, and event name
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_file_name = f"{now}_{event_name}.pdf"
        pdf_file_path = os.path.join(save_folder, pdf_file_name)
        pdf.output(pdf_file_path)

        st.success(f"Results saved to {pdf_file_path}")

    except Exception as e:
        st.error(f"Failed to save final PDF: {str(e)}")

# Start the detection process when the button is clicked
if start_detection:
    detection_running = True
    cap = cv2.VideoCapture(0)
    stop_detection=st.button("Stop Detection", key='stop_button')
    if not cap.isOpened():
        st.error("Failed to open camera. Please check if the camera is connected properly.")
    else:
        frame_count = 0
        
        while detection_running:
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to read from camera.")
                break

            detections = detect_objects(frame)
            for detection in detections:
                x1, y1, x2, y2 = int(detection['xmin']), int(detection['ymin']), int(detection['xmax']), int(detection['ymax'])
                label = detection['name']
                confidence = detection['confidence']

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} {confidence:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                results.append({
                    "frame": cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                    "detection": detection,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

            FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            frame_count += 1

            if frame_count >= 1:  # Save PDF after every frame
                save_pdf()
                frame_count = 0  # Reset frame count and continue detection

            # Stop detection if the "Stop Detection" button is clicked
            if stop_detection:
                detection_running = False
                save_pdf()
                break

        cap.release()
        finalize_pdf()  # Save the final PDF when detection loop is stopped
