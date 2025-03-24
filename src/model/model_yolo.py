from ultralytics import YOLO
import numpy as np
import cv2
import os

class YOLODetector:
    """Class for handling YOLO model operations and detections."""
    
    def __init__(self, model_path="src/model/yolov8s.pt"):
        """Initialize the YOLO detector with model and configuration."""
        # Make sure the model file exists
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
            
        # Load and configure the model
        self.model = YOLO(model_path)
        self.model.overrides['conf'] = 0.8  # Confidence threshold
        self.model.overrides['iou'] = 0.5   # IoU threshold
        self.model.overrides['agnostic_nms'] = True  # Class-agnostic NMS
        self.model.overrides['max_det'] = 5  # Maximum number of detections
        
        # Warm up the model with a dummy frame
        self._warmup_model()
        print(f"✅ YOLODetector initialized with model: {model_path}")
    
    def _warmup_model(self):
        """Warm up the model with a dummy frame to reduce initial inference time."""
        dummy_frame = np.zeros((640, 640, 3), dtype=np.uint8)
        _ = self.model(dummy_frame)
    
    def detect(self, frame, save_path=None):
        """
        Perform object detection on a frame.
        
        Args:
            frame: The input frame for detection
            save_path: Optional path to save the annotated image
            
        Returns:
            tuple: (annotated_frame, detection_summary)
        """
        # Run inference
        results = self.model(frame)
        
        # Create annotated image
        annotated_frame = frame.copy()
        
        # Draw bounding boxes and labels
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Extract confidence
                conf = float(box.conf[0])
                
                # Only process detections with confidence > threshold
                if conf > 0.5:
                    # Extract coordinates
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # Extract class
                    cls = int(box.cls[0])
                    class_name = r.names[cls]
                    
                    # Draw rectangle and label
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    # Get image dimensions
                    h, w = annotated_frame.shape[:2]
                    text_x = max(0, min(x1, w-10))  # Keep x within image width
                    text_y = max(20, min(y1-10, h-10))  # Keep y within image height

                    cv2.putText(annotated_frame, f"{class_name} {conf:.2f}", 
                                (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 
                                (0, 255, 0), 2)
                    print("text done")
        # Count detected items with confidence > 0.5
        detected_items = {}
        for r in results:
            for box in r.boxes:
                conf = float(box.conf[0])
                if conf > 0.5:
                    cls = int(box.cls[0])
                    class_name = r.names[cls]
                    if class_name in detected_items:
                        detected_items[class_name] += 1
                    else:
                        detected_items[class_name] = 1
        
        # Create detection summary
        detection_summary = ""
        if detected_items:
            detection_summary = ", ".join([f"{count} {item}" for item, count in detected_items.items()])
        
        # Save the annotated image if path is provided
        if save_path and annotated_frame is not None:
            # Make sure the directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            cv2.imwrite(save_path, annotated_frame)
        
        return annotated_frame, detection_summary