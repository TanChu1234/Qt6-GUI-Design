from PySide6.QtCore import QThread, Signal, QMutex, QWaitCondition
from PySide6.QtGui import QPixmap, QImage
import cv2
import time

class CameraThread(QThread):
    frame_signal = Signal(QPixmap, str)
    log_signal = Signal(str)
    connection_status_signal = Signal(str, str)  # New signal: status, camera_name
    
    def __init__(self, ip, port, username, password, camera_name, protocol):
        super().__init__()
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.camera_name = camera_name
        self.protocol = protocol
        self.active = False
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        
    def run(self):
        self.active = True
        
        # Build camera URL based on protocol
        if self.protocol == "RTSP":
            url = f"rtsp://{self.username}:{self.password}@{self.ip}:{self.port}/Streaming/Channels/101"
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
        
        # Attempt to connect to camera
        cap = cv2.VideoCapture(url)
        
        if not cap.isOpened():
            self.log_signal.emit(f"❌ Failed to connect to {self.camera_name}")
            self.connection_status_signal.emit("disconnected", self.camera_name)
            self.active = False
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
            
            # Convert to QImage
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Convert to pixmap and emit signal
            pixmap = QPixmap.fromImage(qt_image)
            self.frame_signal.emit(pixmap, self.camera_name)
            
            # Prevent high CPU usage
            # time.sleep(0.033)  # Approx 30 fps
            
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