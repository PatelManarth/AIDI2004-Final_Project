# backend/main.py
from fastapi import FastAPI, File, UploadFile
import cv2
import numpy as np
import uvicorn
from ultralytics import YOLO

app = FastAPI()

model = YOLO("yolov8n.pt")

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    results = model(img)
    
    # Converting results to pandas DataFrame
    results_df = results.pandas().xyxy[0] if hasattr(results, 'pandas') else None
    if results_df is None:
        return {"error": "Failed to process results"}
    
    detections = results_df.to_dict(orient="records")
    return {"detections": detections}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
