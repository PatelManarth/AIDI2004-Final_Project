import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend')))

import pytest
from unittest.mock import patch, MagicMock
import numpy as np
from app import detect_objects

@patch('app.requests.post')
@patch('app.cv2.imencode')
def test_detect_objects(mock_imencode, mock_post):
    # Mock image encoding
    mock_imencode.return_value = (True, MagicMock(tobytes=MagicMock(return_value=b'fake_image_data')))
    
    # Mock backend response
    mock_post.return_value = MagicMock(
        status_code=200,
        json=MagicMock(return_value={
            'detections': [
                {"xmin": 10, "ymin": 20, "xmax": 30, "ymax": 40, "name": "person", "confidence": 0.95}
            ]
        })
    )
    
    # Create a fake frame
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    detections = detect_objects(frame)
    
    assert len(detections) == 1
    assert detections[0]["name"] == "person"
    assert detections[0]["confidence"] == 0.95
