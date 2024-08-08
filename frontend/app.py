import streamlit as st
import cv2
import requests
import numpy as np
from PIL import Image
from fpdf import FPDF
import datetime

# Set the title of the Streamlit app
st.title("Dangerous Object Detection")

# Input fields and controls in Streamlit
event_name = st.text_input("Enter Event Name")
run = st.checkbox('Run')
FRAME_WINDOW = st.image([])  # To display the video frames

def detect_objects(frame):
    try:
        # Encode the image frame as a JPEG
        _, img_encoded = cv2.imencode('.jpg', frame)

        # Make the POST request to the backend
        response = requests.post(
            "http://localhost:8000/detect",
            files={"file": ("frame.jpg", img_encoded.tobytes(), "image/jpeg")}
        )

        # Debug: Print the raw response text
        print("Response Text:", response.text)

        # Check for response status
        if response.status_code != 200:
            st.error(f"API Error: {response.status_code}")
            return []

        # Parse JSON response
        return response.json().get('detections', [])

    except requests.exceptions.RequestException as e:
        st.error(f"Request Exception: {str(e)}")
        return []

    except ValueError as e:
        st.error(f"JSON Decode Error: {str(e)}")
        return []

# Open a connection to the default camera
cap = cv2.VideoCapture(0)
results = []

while run:
    ret, frame = cap.read()  # Capture a frame from the camera
    if not ret:
        st.error("Failed to read from camera.")
        break

    # Detect objects in the current frame
    detections = detect_objects(frame)

    # Process each detection
    for detection in detections:
        x1, y1, x2, y2 = int(detection['xmin']), int(detection['ymin']), int(detection['xmax']), int(detection['ymax'])
        label = detection['name']
        confidence = detection['confidence']

        # Draw a rectangle and label on the frame
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"{label} {confidence:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Save the detection result for later use
        results.append({
            "frame": cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
            "detection": detection
        })

    # Display the current frame in Streamlit
    FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

# Release the camera when done
cap.release()

# Save results to PDF when the button is clicked
if st.button("Save Results to PDF"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Add detection results to the PDF
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
