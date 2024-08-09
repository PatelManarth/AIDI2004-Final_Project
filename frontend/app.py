import streamlit as st
import requests
import datetime
import time
import os
from PIL import Image
from fpdf import FPDF
import numpy as np
import cv2
import base64

# Set the title of the Streamlit app
st.title("Dangerous Object Detection")

# Input fields and controls in Streamlit
event_name = st.text_input("Enter Event Name")
start_detection = st.button('Start Detection')
stop_detection = st.button('Stop Detection')

# Manage session state for detection
if "detection_running" not in st.session_state:
    st.session_state.detection_running = False
if "results" not in st.session_state:
    st.session_state.results = []

FRAME_WINDOW = st.image([])  # To display the video frames

def detect_objects(frame):
    try:
        _, img_encoded = cv2.imencode('.jpg', frame)
        response = requests.post(
            "http://127.0.0.1:8000/detect",
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
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)

        for result in st.session_state.results:
            frame = result["frame"]
            detection = result.get("detection", {})
            label = detection.get('name', 'Unknown')
            confidence = detection.get('confidence', 0.0)
            timestamp = result.get("timestamp", 'Unknown time')

            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Detection: {label} with confidence {confidence:.2f} at {timestamp}", ln=True)

            img = Image.fromarray(frame)
            img_path = f"temp_{int(time.time())}.png"
            img.save(img_path)
            pdf.image(img_path, x=10, y=None, w=100)
            os.remove(img_path)  # Clean up the temporary image file

        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Get the absolute path to the 'saved-pdf' directory
        save_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'saved-pdf'))
        
        # Ensure the directory exists
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Create the full path for the PDF file
        save_path = os.path.join(save_dir, f"{now}_{event_name}.pdf")
        pdf.output(save_path)
       
        st.success(f"Results saved to {save_path}")

    except Exception as e:
        st.error(f"Failed to save PDF: {str(e)}")


# HTML and JavaScript to access the camera
st.markdown("""
    <video id="video" width="640" height="480" autoplay></video>
    <canvas id="canvas" width="640" height="480" style="display:none;"></canvas>
    <script>
        var video = document.getElementById('video');
        var canvas = document.getElementById('canvas');
        var context = canvas.getContext('2d');

        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function(stream) {
                video.srcObject = stream;
                video.play();
            });

        function captureFrame() {
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            var dataURL = canvas.toDataURL('image/jpeg');
            return dataURL;
        }

        function sendFrame() {
            var frame = captureFrame();
            Streamlit.setComponentValue(frame);
        }

        var intervalId;
        Streamlit.events.startDetection = function() {
            intervalId = setInterval(sendFrame, 500);  // Capture and send frames every 500ms
        };

        Streamlit.events.stopDetection = function() {
            clearInterval(intervalId);
        };
    </script>
""", unsafe_allow_html=True)

# Start detection process
if start_detection and not st.session_state.detection_running:
    st.session_state.detection_running = True
    st.session_state.results = []

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        st.error("Failed to open camera. Please check if the camera is connected properly.")
    else:
        while st.session_state.detection_running:
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to read from camera.")
                break

            # Detect objects in the frame
            detections = detect_objects(frame)

            # Draw bounding boxes and labels on the frame
            for detection in detections:
                x1, y1, x2, y2 = int(detection['xmin']), int(detection['ymin']), int(detection['xmax']), int(detection['ymax'])
                label = detection['name']
                confidence = detection['confidence']

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} {confidence:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                st.session_state.results.append({
                    "frame": cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                    "detection": detection,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

            # Update the frame in Streamlit
            FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Release the camera after detection stops
        cap.release()
        save_pdf()

    if stop_detection:
        st.session_state.detection_running = False
        st.session_state.results.append({"frame": np.zeros((100, 100, 3), dtype=np.uint8), "detection": {}, "timestamp": "Detection Stopped"})
        save_pdf()
        st.stop()

if stop_detection and st.session_state.detection_running:
    st.session_state.detection_running = False
    save_pdf()
    st.stop()
