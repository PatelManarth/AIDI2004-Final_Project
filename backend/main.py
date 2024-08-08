from fastapi import FastAPI, File, UploadFile, HTTPException
import numpy as np
import cv2
from ultralytics import YOLO

app = FastAPI()

# Load the YOLOv8 model
model = YOLO('yolov8n.pt')  # Ensure you have the correct path to your YOLOv8 model file

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    try:
        # Read the image file
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Ensure the image was correctly decoded
        if image is None:
            raise ValueError("Could not decode image")

        # Run object detection
        results = model.predict(source=image)

        # Initialize detections list
        detections = []

        # Process detection results
        for result in results:
            for box in result.boxes:
                # Extract bounding box coordinates and other details
                x1, y1, x2, y2 = box.xyxy[0]  # Properly unpack coordinates
                confidence = box.conf
                label = box.cls

                detections.append({
                    "xmin": int(x1),
                    "ymin": int(y1),
                    "xmax": int(x2),
                    "ymax": int(y2),
                    "name": model.names[int(label)],  # Get class name from model
                    "confidence": float(confidence),
                })

        # Return JSON response
        return {"detections": detections}

    except Exception as e:
        # Log exception and return a 500 error
        print(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
