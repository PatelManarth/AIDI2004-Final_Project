import streamlit as st
import requests
import numpy as np
from PIL import Image
from fpdf import FPDF
import datetime
import time
import base64
import cv2

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
            "http://20.220.16.247/detection/",
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

        save_path = f"{pdf_save_path}/{now}_{event_name}.pdf"
        pdf.output(save_path)
       
        st.success(f"Results saved to {save_path}")

    except Exception as e:
        st.error(f"Failed to save PDF: {str(e)}")

# Embedding the HTML for local camera access
st.markdown(
    """
    <div>
        <video id="video" width="640" height="480" autoplay></video>
        <script>
        async function captureFrame() {
            const video = document.getElementById('video');
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const context = canvas.getContext('2d');
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            return canvas.toDataURL('image/jpeg');
        }
        
        navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
            const video = document.getElementById('video');
            video.srcObject = stream;
            video.play();

            const captureButton = document.getElementById('captureButton');
            captureButton.onclick = async () => {
                const frame = await captureFrame();
                window.streamlitSendFrame(frame);
            };
        });
        </script>
    </div>
    """, unsafe_allow_html=True
)

# Capture frame button
st.markdown('<button id="captureButton">Capture Frame</button>', unsafe_allow_html=True)

def handle_frame(frame_base64):
    frame_data = base64.b64decode(frame_base64.split(",")[1])
    nparr = np.frombuffer(frame_data, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    detections = detect_objects(frame)
    
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

    FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

# Bind Streamlit callback for frame capture
st.streamlitSendFrame = handle_frame

if stop_detection and st.session_state.detection_running:
    st.session_state.detection_running = False
    save_pdf()
