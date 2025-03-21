from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QPixmap, QImage
from ultralytics import YOLO
import cv2
import numpy as np
import time
import os

class YoloDetectionThread(QThread):
    """Thread for processing images with YOLOv8 without blocking the UI."""
    
    # Define signals
    result_signal = Signal(str, QPixmap, list)  # camera_name, result_pixmap, detections
    log_signal = Signal(str)  # For logging messages
    
    def __init__(self, camera_name, camera_thread, model_path="yolov8s.pt"):
        """Initialize the detection thread."""
        super().__init__()
        self.camera_name = camera_name
        self.camera_thread = camera_thread
        
        # Directory for saving results
        self.results_dir = "outputs/detections"
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Path to YOLOv8 model and class names
        print("Khởi tạo model YOLO... (có thể mất vài giây)")
        self.model = YOLO(model_path)
        self.model.overrides['conf'] = 0.8
        self.model.overrides['iou'] = 0.5
        self.model.overrides['agnostic_nms'] = True
        self.model.overrides['max_det'] = 1
        dummy_frame = np.zeros((640, 640, 3), dtype=np.uint8)
        _ = self.model(dummy_frame)

    
    def run(self):
        """Process the current frame with YOLOv8."""
        try:
            # Get a copy of the last frame from the camera thread
            self.n  .mutex.lock()
            if self.camera_thread.last_frame is None:
                self.camera_thread.mutex.unlock()
                self.log_signal.emit("❌ No frame available for AI processing")
                self.result_signal.emit(self.camera_name, None, [])
                return
                
            frame = self.camera_thread.last_frame.copy()
            self.camera_thread.mutex.unlock()
            
            # Check if the model file exists
            if not os.path.exists(self.model_path):
                self.log_signal.emit(f"❌ YOLOv8 model not found at {self.model_path}")
                self.result_signal.emit(self.camera_name, None, [])
                return
                
            # Load the YOLO model
            self.log_signal.emit("🔄 Loading YOLOv8 model...")
            net = cv2.dnn.readNetFromONNX(self.model_path)
            
            # Process the image
            detections = self._detect_objects(frame, net)
            
            # Draw bounding boxes and labels
            result_frame = self._draw_detections(frame, detections)
            
            # Save the result
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{self.results_dir}/{self.camera_name}_detection_{timestamp}.jpg"
            cv2.imwrite(filename, result_frame)
            
            # Convert to QPixmap for display
            rgb_frame = cv2.cvtColor(result_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            
            # Extract detection info (class, confidence)
            detection_info = []
            for detection in detections:
                x, y, w, h, confidence, class_id = detection
                class_id = int(class_id)
                class_name = self.classes[class_id] if class_id < len(self.classes) else f"class_{class_id}"
                detection_info.append((class_name, confidence))
            
            # Emit result signal with the processed image and detections
            self.result_signal.emit(self.camera_name, pixmap, detection_info)
            self.log_signal.emit(f"✅ YOLOv8 detection completed and saved: {filename}")
            
        except Exception as e:
            self.log_signal.emit(f"❌ Error in AI detection: {str(e)}")
            self.result_signal.emit(self.camera_name, None, [])
    
    def _detect_objects(self, frame, net):
        """Detect objects in the image using YOLOv8."""
        # Get image dimensions
        height, width = frame.shape[:2]
        
        # Create a blob from the image
        blob = cv2.dnn.blobFromImage(
            frame, 
            1/255.0,  # Normalize pixel values
            (640, 640),  # YOLOv8 input size
            swapRB=True,  # BGR to RGB
            crop=False
        )
        
        # Set the input
        net.setInput(blob)
        
        # Get network output
        outputs = net.forward()
        
        # Process the outputs
        detections = []
        outputs = outputs[0]
        
        # YOLOv8 output format: [x, y, w, h, conf, class_id1, class_id2, ...]
        rows = outputs.shape[0]
        
        # The predictions matrix has 4 corner values, 1 confidence value, and 80 class scores
        for i in range(rows):
            confidence = outputs[i, 4]
            
            # Get the scores (class probabilities)
            scores = outputs[i, 5:]
            
            # Find the class ID with maximum score
            class_id = np.argmax(scores)
            max_score = scores[class_id]
            
            # Multiply class score with objectness confidence
            confidence *= max_score
            
            # Filter out weak predictions
            if confidence > 0.25:  # Confidence threshold
                # Scale bounding box coordinates to the original image
                x, y, w, h = outputs[i, 0:4] * np.array([width, height, width, height])
                x = x - (w / 2)
                y = y - (h / 2)
                
                detections.append([x, y, w, h, confidence, class_id])
        
        # Apply non-maximum suppression
        indices = cv2.dnn.NMSBoxes(
            [det[0:4] for det in detections],
            [det[4] for det in detections],
            0.25,  # Confidence threshold
            0.45   # NMS threshold
        )
        
        return [detections[i] for i in indices]
    
    def _draw_detections(self, frame, detections):
        """Draw bounding boxes and labels on the image."""
        result = frame.copy()
        
        for detection in detections:
            x, y, w, h, confidence, class_id = detection
            
            # Convert to integers
            x, y, w, h = int(x), int(y), int(w), int(h)
            class_id = int(class_id)
            
            # Get class name
            class_name = self.classes[class_id] if class_id < len(self.classes) else f"class_{class_id}"
            
            # Generate a random color for this class
            color = (
                hash(class_name) % 255,
                (hash(class_name) * 137) % 255,
                (hash(class_name) * 269) % 255
            )
            
            # Draw bounding box
            cv2.rectangle(result, (x, y), (x + w, y + h), color, 2)
            
            # Create label
            label = f"{class_name}: {confidence:.2f}"
            
            # Draw label background
            text_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(
                result,
                (x, y - text_size[1] - 5),
                (x + text_size[0], y),
                color,
                -1
            )
            
            # Draw text
            cv2.putText(
                result,
                label,
                (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2
            )
        
        return result