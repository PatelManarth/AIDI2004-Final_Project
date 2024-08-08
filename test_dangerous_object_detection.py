import pytest
import subprocess
import os
import time
import requests
from ultralytics import YOLO
import random
from pathlib import Path

# Path configuration
BACKEND_DIR = os.path.abspath("backend")
FRONTEND_DIR = os.path.abspath("frontend")
DATASET_DIR = os.path.abspath("datasets/test/images")
YOLO_MODEL_PATH = "best.pt"

@pytest.fixture(scope="session", autouse=True)
def start_backend_and_frontend():
    # Start FastAPI backend
    backend_process = subprocess.Popen(
        ["uvicorn", "main:app", "--reload"],
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(5)  # Give some time to start

    # Start Streamlit frontend
    frontend_process = subprocess.Popen(
        ["streamlit", "run", "app.py"],
        cwd=FRONTEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(5)  # Give some time to start

    yield

    # Terminate the processes after tests
    backend_process.terminate()
    frontend_process.terminate() 

def test_yolo_model_on_random_images():
    # Load the model
    model = YOLO(YOLO_MODEL_PATH)

    # Get all image paths
    image_paths = list(Path(DATASET_DIR).glob("*.jpg"))
    assert len(image_paths) > 0, "No images found in test directory"

    # Run the test 5 times with random images
    for _ in range(5):
        random_image = random.choice(image_paths)
        results = model.predict(source=str(random_image), conf=0.8)
        assert results is not None, f"Detection failed on image: {random_image}"

if __name__ == "__main__":
    pytest.main([__file__])
