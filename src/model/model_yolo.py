from ultralytics import YOLO
import cv2
import numpy as np
import queue
from PySide6.QtCore import QThread, Signal

class YOLOWorker(QThread):
    resultReady = Signal(np.ndarray)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = YOLO("best100.pt")
        self.model.overrides['conf'] = 0.8
        self.model.overrides['iou'] = 0.5
        self.model.overrides['agnostic_nms'] = True
        self.model.overrides['max_det'] = 5
        
        # Warm up the model
        dummy_frame = np.zeros((640, 640, 3), dtype=np.uint8)
        _ = self.model(dummy_frame)
        
        self.frame_queue = queue.Queue(maxsize=1)
        self.running = True
    
    def add_frame(self, frame):
        try:
            # Clear queue before adding new frame
            while not self.frame_queue.empty():
                self.frame_queue.get_nowait()
            
            self.frame_queue.put_nowait(frame)
            return True
        except queue.Full:
            return False
    
    def run(self):
        while self.running:
            try:
                frame = self.frame_queue.get(timeout=1.0)
                results = self.model(frame)
                annotated_frame = self._annotate_frame(frame, results)
                self.resultReady.emit(annotated_frame)
                self.frame_queue.task_done()
            except queue.Empty:
                continue
    
    def _annotate_frame(self, frame, results):
        for det in results:
            for box in det.boxes:
                x, y, w, h = box.xywh[0]
                conf = box.conf[0]
                cls = int(box.cls[0])
                label = f"{det.names[cls]} {conf:.2f}"
                
                cv2.rectangle(frame, 
                            (int(x-w/2), int(y-h/2)), 
                            (int(x+w/2), int(y+h/2)), 
                            (0, 255, 0), 2)
                cv2.putText(frame, label, 
                          (int(x-w/2), int(y-h/2)-10), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, 
                          (0, 255, 0), 2)
        return frame
    
    def stop(self):
        self.running = False
        self.wait()  # Wait until the thread finishes
