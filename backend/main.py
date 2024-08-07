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

    detections = []
    for result in results:
        for box in result.boxes:
            detections.append({
                "xmin": box.xmin.item(),
                "ymin": box.ymin.item(),
                "xmax": box.xmax.item(),
                "ymax": box.ymax.item(),
                "confidence": box.confidence.item(),
                "class": box.cls.item(),
                "name": result.names[int(box.cls.item())]
            })

    return {"detections": detections}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
