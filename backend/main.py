from fastapi import FastAPI, File, UploadFile, HTTPException
import numpy as np
import cv2
from ultralytics import YOLO
import logging

# Initialize FastAPI app and YOLOv8 model
app = FastAPI()
model = YOLO('best.pt')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    try:
        # Read and decode the image file
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Could not decode image")

        # Run object detection
        results = model.predict(source=image,conf=0.75)

        # Initialize detections list
        detections = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                confidence = box.conf
                label = box.cls

                detections.append({
                    "xmin": int(x1),
                    "ymin": int(y1),
                    "xmax": int(x2),
                    "ymax": int(y2),
                    "name": model.names[int(label)],
                    "confidence": float(confidence),
                })

        return {"detections": detections}

    except ValueError as e:
        logger.error(f"Image decoding failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Image decoding failed: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")