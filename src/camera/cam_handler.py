import cv2
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage, QPixmap

class CameraThread(QThread):
    frame_signal = Signal(QPixmap)  # Signal to send frames
    log_signal = Signal(str)  # Signal for log messages

    def __init__(self, ip_address, port="", username="", password="", camera_name="", protocol="rtsp"):
        super().__init__()
        self.ip_address = ip_address
        self.port = port
        self.username = username
        self.password = password
        self.camera_name = camera_name
        self.protocol = protocol.lower()
        self.running = True  # Control flag

    
    def run(self):
        """Capture video from the IP camera and handle sudden disconnections."""
        # Build URL with authentication if provided
        if self.protocol == "rtsp":
            url = f"rtsp://"
            if self.username and self.password:
                url += f"{self.username}:{self.password}@"
            url += f"{self.ip_address}:{self.port}/stream1"
        else:  # http
            url = f"http://"
            if self.username and self.password:
                url += f"{self.username}:{self.password}@"
            url += f"{self.ip_address}:{self.port}/video"
        
        self.log_signal.emit(f"🔄 Connecting to {self.protocol}://{self.ip_address}:{self.port}")
        
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        # cap.set(cv2.CAP_PROP_FPS, 10)  # Try lowering FPS
        if not cap.isOpened():
            self.log_signal.emit(f"❌ Failed to open camera {self.camera_name or self.ip_address}. Exiting.")
            return  # Exit the thread immediately

        self.log_signal.emit(f"✅ Camera {self.camera_name or self.ip_address} started streaming.")

        # Add counter for consecutive frame failures
        frame_failure_count = 0
        max_failures = 3  # Number of consecutive failures before giving up
        
        while self.running:
            ret, frame = cap.read()
            if not ret:
                frame_failure_count += 1
                self.log_signal.emit(f"⚠️ Frame read failed ({frame_failure_count}/{max_failures})")
                
                # If we've had too many consecutive failures, stop the thread
                if frame_failure_count >= max_failures:
                    self.log_signal.emit(f"❌ Lost connection to {self.camera_name or self.ip_address}. Stopping thread.")
                    break
                    
                # Short sleep to avoid tight loop when camera is having issues
                self.msleep(100)
                continue
            
            # Reset failure counter on successful frame
            frame_failure_count = 0
            
            # Convert frame to QPixmap
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_img)

            self.frame_signal.emit(pixmap)  # Send frame to UI

        # Clean up
        cap.release()
        self.log_signal.emit(f"🛑 Camera {self.camera_name or self.ip_address} stopped.")
        
        # Signal camera stopped to main thread
        self.running = False

    def stop(self):
        """Stop the camera thread safely and exit immediately."""
        self.running = False
        self.quit()  # Request thread to exit immediately
        self.wait()  # Wait for thread to finish