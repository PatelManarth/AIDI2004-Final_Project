import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@patch('main.model.predict')
def test_detect_endpoint(mock_predict):
    # Mock the detection results
    mock_predict.return_value = [
        MagicMock(boxes=[
            MagicMock(xyxy=[[10, 20, 30, 40]], conf=0.9, cls=1)  # xyxy should be a list of lists
        ])
    ]

    image_path = "tests/test_image.jpg"
    assert os.path.exists(image_path), "Test image file does not exist"

    with open(image_path, "rb") as img:
        response = client.post("/detect", files={"file": img})

    assert response.status_code == 200

