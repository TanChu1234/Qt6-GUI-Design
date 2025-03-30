from ultralytics import YOLO
import numpy as np
import cv2
import os

class YOLODetector:
    """Class for handling YOLO model   operations and detections with ROI support."""
    
    def __init__(self, model_path="src/model/yolov8s.pt", rois=None):
        """Initialize the YOLO detector with model and configuration.
        
        Args:
            model_path (str): Path to the YOLO model file
            rois (list): List of ROIs in format [(x1,y1,x2,y2), ...] where
                        (x1,y1) is top-left and (x2,y2) is bottom-right
        """
        # Make sure the model file exists
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
            
        # Load and configure the model
        self.model = YOLO(model_path)
        # Move model to GPU
        self.model.to("cuda")
        self.model.overrides['max_det'] = 100  # Maximum number of detections
        
        # Store ROIs
        self.rois = rois if rois is not None else []
        
        # Warm up the model with a dummy frame
        self._warmup_model()
        print(f"✅ YOLODetector initialized with model: {model_path}")
    
    def _warmup_model(self):
        """Warm up the model with a dummy frame to reduce initial inference time."""
        dummy_frame = np.zeros((640, 640, 3), dtype=np.uint8)
        _ = self.model(dummy_frame)
    
    def detect(self, frame, save_path=None):
        """Run detection on a frame and check ROIs.
        
        Returns:
            tuple: (annotated_frame, detection_summary, person_count, roi_status)
                   roi_status is a list of booleans indicating person presence in each ROI
        """
        
        
        # Run inference
        results = self.model(frame)
        
        # Create annotated image
        annotated_frame = frame.copy()
        if not self.rois:
            h, w = frame.shape[:2]
            self.rois = [(0, 0, w, h)]
        
        # Draw ROIs first (so detections appear on top)
        self._draw_rois(annotated_frame)
        
        # Draw bounding boxes and labels
        boxes = self._draw_boxes_and_labels(results, annotated_frame)
        
        # Count detected items
        detected_items, person_count = self._count_detected_items(results)
        
        # Create detection summary
        detection_summary = self._create_detection_summary(detected_items)
        
        # Check which ROIs have persons
        roi_status = self._check_rois(boxes)
        
        # Save the annotated image if path is provided
        if save_path and annotated_frame is not None:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            cv2.imwrite(save_path, annotated_frame)
        
        return annotated_frame, detection_summary, person_count, roi_status

    def _draw_rois(self, frame):
        """Draw ROIs on the frame."""
        for i, roi in enumerate(self.rois):
            x1, y1, x2, y2 = roi
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            # Put ROI number
            cv2.putText(frame, f"ROI {i+1}", (x1, y1-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    def _draw_boxes_and_labels(self, results, annotated_frame):
        """Draw bounding boxes and labels on the annotated frame.
        
        Returns:
            list: List of person bounding boxes in format [(x1,y1,x2,y2), ...]
        """
        person_boxes = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Extract confidence
                conf = float(box.conf[0])
                
                # Only process detections with confidence > threshold and are persons
                if conf > 0.6 and box.cls[0] == 0:
                    # Extract coordinates
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    person_boxes.append((x1, y1, x2, y2))
                    
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
        return person_boxes

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

    def _check_rois(self, boxes):
        """Check which ROIs contain persons.
        
        Args:
            boxes (list): List of person bounding boxes in format [(x1,y1,x2,y2), ...]
            
        Returns:
            list: Boolean list indicating if each ROI contains at least one person
        """
        roi_status = [False] * len(self.rois)
        
        for i, roi in enumerate(self.rois):
            roi_x1, roi_y1, roi_x2, roi_y2 = roi
            for box in boxes:
                box_x1, box_y1, box_x2, box_y2 = box
                
                # Check if box center is within ROI
                box_center_x = (box_x1 + box_x2) // 2
                box_center_y = (box_y1 + box_y2) // 2
                
                if (roi_x1 <= box_center_x <= roi_x2 and 
                    roi_y1 <= box_center_y <= roi_y2):
                    roi_status[i] = True
                    break  # No need to check other boxes for this ROI
        
        return roi_status