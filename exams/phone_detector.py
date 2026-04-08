from ultralytics import YOLO

model = YOLO("yolov8n.pt")

def detect_phone(frame):

    results = model(frame, conf=0.4)

    for r in results:

        for box in r.boxes:

            cls = int(box.cls[0])
            label = model.names[cls]

            if label == "cell phone":
                return True

    return False