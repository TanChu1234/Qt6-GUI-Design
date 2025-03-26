import ultralytics
from ultralytics import YOLO
import numpy as np
import torch

ultralytics.checks()
model = YOLO("src\model\yolov8s.pt")
dummy_frame = np.zeros((1,3, 640, 640), dtype=np.uint8)
dummy_frame = torch.from_numpy(dummy_frame).float().to("cuda")/255
_ = model(dummy_frame)