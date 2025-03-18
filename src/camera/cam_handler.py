from PySide6.QtCore import QThread, Signal, QMutex, QWaitCondition
from PySide6.QtGui import QPixmap, QImage
import cv2
import time
import os

class CameraThread(QThread):
    frame_signal = Signal(QPixmap, str)
    log_signal = Signal(str)
    connection_status_signal = Signal(str, str)  # status, camera_name
    trigger_completed_signal = Signal(str, str)  # result, camera_name
    
    def __init__(self, ip, port, username, password, camera_name, protocol):
        super().__init__()
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.camera_name = camera_name
        self.protocol = protocol
        self.active = False
        self.triggered = False
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.last_frame = None
        self.save_path = "captures"  # Default path for saved images
        
        # Create the save directory if it doesn't exist
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        
    def run(self):
        self.active = True
        
        # Build camera URL based on protocol
        if self.protocol == "RTSP":
            url = f"rtsp://{self.username}:{self.password}@{self.ip}:{self.port}/stream1"
        elif self.protocol == "HTTP":
            url = f"http://{self.username}:{self.password}@{self.ip}:{self.port}/video"
        else:  # Default or local camera
            try:
                url = int(self.ip)  # Try to convert to int for local cameras
            except ValueError:
                url = f"{self.protocol}://{self.username}:{self.password}@{self.ip}:{self.port}"
        
        # Log that we're connecting
        self.log_signal.emit(f"🔌 Connecting to {self.camera_name} at {self.ip}...")
        self.connection_status_signal.emit("connecting", self.camera_name)
        
        # Attempt to connect to camera with timeout logic
        cap = cv2.VideoCapture(url)
        start_time = time.time()
        timeout = 5  # Set timeout to 5 seconds

        while time.time() - start_time < timeout:
            if cap.isOpened():
                break
            time.sleep(0.5)  # Avoid busy-waiting

        if not cap.isOpened():
            self.log_signal.emit(f"❌ Failed to connect to {self.camera_name} (Timeout)")
            self.connection_status_signal.emit("disconnected", self.camera_name)
            self.active = False
            cap.release()  # Ensure the resource is released
            return
            
        self.log_signal.emit(f"✅ Connected to {self.camera_name}")
        self.connection_status_signal.emit("connected", self.camera_name)     
        
        # Main loop for capturing frames
        while self.active:
            ret, frame = cap.read()
            if not ret:
                self.log_signal.emit(f"🚫 Lost connection to {self.camera_name}")
                self.connection_status_signal.emit("disconnected", self.camera_name)
                break

            # Convert to RGB format
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Store the last frame for trigger processing
            self.mutex.lock()
            self.last_frame = frame.copy()  # Store BGR format for processing
            
            # Check if we've been triggered
            if self.triggered:
                self.process_trigger()
                self.triggered = False
            self.mutex.unlock()
            
            # Convert to QImage
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Convert to pixmap and emit signal
            pixmap = QPixmap.fromImage(qt_image)
            self.frame_signal.emit(pixmap, self.camera_name)
            
            # Reduce CPU usage
            time.sleep(0.03)  # Approx 30 fps
            
            # Check if we should stop - thread-safe way
            self.mutex.lock()
            if not self.active:
                self.mutex.unlock()
                break
            self.mutex.unlock()
                
        # Cleanup
        cap.release()
        
    def stop(self):
        self.mutex.lock()
        self.active = False
        self.mutex.unlock()
        self.condition.wakeAll()
    
    def trigger(self, action="capture"):
        """Trigger the camera to perform an action on the next frame."""
        if not self.active:
            self.log_signal.emit(f"⚠️ Cannot trigger {self.camera_name}: Camera not active")
            self.trigger_completed_signal.emit("error", self.camera_name)
            return False
            
        self.mutex.lock()
        self.triggered = True
        self.trigger_action = action
        self.mutex.unlock()
        self.log_signal.emit(f"🔔 Triggered {self.camera_name} - Action: {action}")
        return True
    
    def process_trigger(self):
        """Process the trigger action on the current frame."""
        if self.last_frame is None:
            self.log_signal.emit(f"⚠️ Cannot process trigger: No frame available")
            self.trigger_completed_signal.emit("error", self.camera_name)
            return
            
        action = self.trigger_action
        
        if action == "capture":
            # Save the current frame as an image
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"{self.save_path}/{self.camera_name}_{timestamp}.jpg"
            cv2.imwrite(filename, self.last_frame)
            self.log_signal.emit(f"📸 Captured image from {self.camera_name}: {filename}")
            self.trigger_completed_signal.emit(filename, self.camera_name)
            
        elif action == "analyze":
            # Placeholder for running analysis on the frame
            # This could be replaced with actual CV/ML processing
            self.log_signal.emit(f"🔍 Analyzing frame from {self.camera_name}...")
            
            # Simulate analysis (replace with actual analysis code)
            # Example: count objects, detect faces, read text, etc.
            result = f"Analysis complete for {self.camera_name}"
            
            self.log_signal.emit(f"✅ {result}")
            self.trigger_completed_signal.emit(result, self.camera_name)
            
        else:
            self.log_signal.emit(f"⚠️ Unknown trigger action: {action}")
            self.trigger_completed_signal.emit("error", self.camera_name)