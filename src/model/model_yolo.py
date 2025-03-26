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
        # Move model to GPU
        self.model.to("cuda")
        # self.model.overrides['conf'] = 0.5  # Confidence threshold
        # self.model.overrides['iou'] = 0.5   # IoU threshold
        # self.model.overrides['agnostic_nms'] = True  # Class-agnostic NMS
        self.model.overrides['max_det'] = 1  # Maximum number of detections
        
        # Warm up the model with a dummy frame
        self._warmup_model()
        print(f"✅ YOLODetector initialized with model: {model_path}")
    
    def _warmup_model(self):
        """Warm up the model with a dummy frame to reduce initial inference time."""
        # dummy_frame = np.zeros((1, 3, 640, 640), dtype=np.uint8)
        # dummy_frame = torch.from_numpy(dummy_frame).float().to("cuda")/255
        dummy_frame = np.zeros((640, 640, 3), dtype=np.uint8)
        _ = self.model(dummy_frame)
    
    def detect(self, frame, save_path=None):
        # image_tensor = self.preprocess_image(frame)
        # Run inference
        results = self.model(frame)
        
        # Create annotated image
        annotated_frame = frame.copy()
        
        # Draw bounding boxes and labels
        self._draw_boxes_and_labels(results, annotated_frame)
        
        # Count detected items
        detected_items, person_count = self._count_detected_items(results)
        
        # Create detection summary
        detection_summary = self._create_detection_summary(detected_items)
        
        # Save the annotated image if path is provided
        if save_path and annotated_frame is not None:
            # Make sure the directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            cv2.imwrite(save_path, annotated_frame)
        
        return annotated_frame, detection_summary, person_count

    def _draw_boxes_and_labels(self, results, annotated_frame):
        """Draw bounding boxes and labels on the annotated frame."""
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Extract confidence
                conf = float(box.conf[0])
                
                # Only process detections with confidence > threshold
                if conf > 0.6 and box.cls[0] == 0:
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

    def _count_detected_items(self, results):
        """Count detected items and persons."""
        detected_items = {}
        person_count = 0  # Total person count
        
        for r in results:
            for box in r.boxes:
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = r.names[cls]
                
                # Count all persons with confidence > 0.6
                if conf > 0.6 and cls == 0 and class_name == "person":
                    person_count += 1
                    if class_name in detected_items:
                        detected_items[class_name] += 1
                    else:
                        detected_items[class_name] = 1
        return detected_items, person_count

    def _create_detection_summary(self, detected_items):
        """Create a summary of detected items."""
        if detected_items:
            return ", ".join([f"{count} {item}" for item, count in detected_items.items()])
        return ""