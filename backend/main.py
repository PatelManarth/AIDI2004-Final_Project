# backend/main.py
from fastapi import FastAPI, File, UploadFile
import cv2
import numpy as np
from ultralytics import YOLO

app = FastAPI()

model = YOLO("yolov8n.pt")

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    results = model(img)
    return {"detections": results.pandas().xyxy[0].to_dict(orient="records")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
