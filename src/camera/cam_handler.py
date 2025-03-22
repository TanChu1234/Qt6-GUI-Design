from PySide6.QtCore import QThread, Signal, QMutex, QWaitCondition
from PySide6.QtGui import QPixmap, QImage
# from model.model_yolo import YOLOWorker
import cv2
import time
import os

class CameraThread(QThread):
    """Thread class for handling camera streaming and operations."""
    
    # Define signals
    frame_signal = Signal(QPixmap, str)  # For UI updates (pixmap, camera_name)
    log_signal = Signal(str)  # For logging messages
    connection_status_signal = Signal(str, str)  # (status, camera_name)
    trigger_completed_signal = Signal(str, str)  # (result, camera_name)
    
    
    def __init__(self, ip, port, username, password, camera_name, protocol):
        """Initialize the camera thread with connection details."""
        super().__init__()
        # Connection parameters
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.camera_name = camera_name
        self.protocol = protocol
        
        # State variables
        self.active = False  # Controls thread main loop
        self.triggered = False  # Flag for trigger operations
        self.trigger_action = None  # What action to perform when triggered
        
        # Thread synchronization
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        # Initialize YOLO worker thread
        # self.yolo_worker = YOLOWorker()
        # self.yolo_worker.resultReady.connect(self.update_image)
        # self.yolo_worker.start()
        # Frame buffer
        self.last_frame = None
        
        # Output configuration
        self.save_path = "captures"  # Default path for saved images
        self.result_path = "outputs/detections"
        # Create the save directory if it doesn't exist
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        
    def run(self):
        """Main thread execution method."""
        self.active = True
        
        # Build camera URL based on protocol
        url = self._build_camera_url()
        
        # Log that we're connecting
        self.log_signal.emit(f"🔌 Connecting to {self.camera_name} at {self.ip}...")
        self.connection_status_signal.emit("connecting", self.camera_name)
        
        # Initialize capture object
        cap = cv2.VideoCapture()
        
        # Set buffer size to reduce latency
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Attempt to connect to camera with timeout
        if not self._connect_with_timeout(cap, url, timeout=2):
            self.log_signal.emit(f"❌ Failed to connect to {self.camera_name} (Timeout)")
            self.connection_status_signal.emit("disconnected", self.camera_name)
            self.active = False
            cap.release()
            return
            
        self.log_signal.emit(f"✅ Connected to {self.camera_name}")
        self.connection_status_signal.emit("connected", self.camera_name)     
        
        # Main frame capture loop
        try:
            self._process_frames(cap)
        except Exception as e:
            self.log_signal.emit(f"❌ Error in {self.camera_name}: {str(e)}")
        finally:
            # Ensure proper cleanup
            cap.release()
    
    def _build_camera_url(self):
        """Build the camera URL string based on protocol."""
        if self.protocol == "RTSP":
            # More generic RTSP URL format
            return f"rtsp://{self.username}:{self.password}@{self.ip}:{self.port}/stream1"
        elif self.protocol == "HTTP":
            return f"http://{self.username}:{self.password}@{self.ip}:{self.port}/video"
        else:
            # Try to use as local camera index
            try:
                return int(self.ip)  # Local camera
            except ValueError:
                # Default to generic URL format
                return f"{self.protocol}://{self.username}:{self.password}@{self.ip}:{self.port}"
    
    def _connect_with_timeout(self, cap, url, timeout=None):
        """
        Attempt to connect to the camera without a strict timeout
        
        Args:
            cap (cv2.VideoCapture): Video capture object
            url (str): Camera URL or source
            timeout (optional): Ignored, kept for compatibility
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Open the camera source
            cap.open(url)
            
            # Check if the capture is opened successfully
            if not cap.isOpened():
                self.log_signal.emit(f"❌ Failed to open camera {self.camera_name}")
                return False
            
            # Attempt to read a frame to verify connection
            ret, frame = cap.read()
            
            if not ret or frame is None:
                self.log_signal.emit(f"⚠️ Cannot read frame from {self.camera_name}")
                return False
            
            return True
        
        except Exception as e:
            # Log any connection errors
            self.log_signal.emit(f"❌ Connection error for {self.camera_name}: {str(e)}")
            return False
            
    def _process_frames(self, cap):
        """Process frames from the camera in a loop."""
        
        while self.active:
            ret, frame = self._read_frame_with_retries(cap)
            if not ret:
                break

            rgb_frame = self._convert_frame_to_rgb(frame)
            self._handle_frame(rgb_frame, frame)
            self._emit_frame_signal(rgb_frame)
            
            time.sleep(0.03)  # ~30 fps max
            
            if not self._should_continue():
                break

    def _read_frame_with_retries(self, cap):
        """Read frame with retries if initial read fails."""
        ret, frame = cap.read()
        if not ret:
            retries = 3
            while retries > 0 and self.active:
                time.sleep(0.1)
                ret, frame = cap.read()
                if ret:
                    break
                retries -= 1
            
            if not ret:
                self.log_signal.emit(f"🚫 Lost connection to {self.camera_name}")
                self.connection_status_signal.emit("disconnected", self.camera_name)
        return ret, frame

    def _convert_frame_to_rgb(self, frame):
        """Convert BGR frame to RGB format."""
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def _handle_frame(self, rgb_frame, frame):
        """Handle frame processing and triggering."""
        self.mutex.lock()
        self.last_frame = frame.copy()
        
        if self.triggered:
            self._process_trigger(self.trigger_action)
            self.triggered = False
            
        self.mutex.unlock()

    def _emit_frame_signal(self, rgb_frame):
        """Convert frame to QPixmap and emit frame signal."""
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.frame_signal.emit(pixmap, self.camera_name)

    def _should_continue(self):
        """Check if the thread should continue running."""
        self.mutex.lock()
        should_continue = self.active
        self.mutex.unlock()
        return should_continue
    
    def stop(self):
        """Stop the camera thread safely."""
        self.mutex.lock()
        self.active = False
        self.mutex.unlock()
        self.condition.wakeAll()
    
    def trigger(self, action):
        """
        Trigger the camera to perform an action on the next frame.
        
        Args:
            action (str, optional): The action to perform (e.g., "capture"). Defaults to "capture".
            use_ai (bool, optional): Whether to trigger AI processing. Defaults to False.
        
        Returns:
            bool: True if trigger was successful, False otherwise.
        """
        if not self.active:
            self.log_signal.emit(f"⚠️ Cannot trigger {self.camera_name}: Camera not active")
            self.trigger_completed_signal.emit("error", self.camera_name)
            return False
        
        self.mutex.lock()

        self.triggered = True
        self.trigger_action = action
        self.mutex.unlock()
        return True
    
      
    def _process_trigger(self, trigger_action):
        """Process the triggered action on the current frame."""
        # Save the current frame to file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{self.result_path}/{self.camera_name}_{timestamp}.jpg"
        
        if self.last_frame is not None:
            try:   
                if trigger_action == "ai_detect":
                    print(type(self.last_frame))
                    cv2.line(self.last_frame,(0,0),(511,511),(255,0,0),5)
                    cv2.imwrite(filename, self.last_frame)
                    self.log_signal.emit(f"📸 Captured image from {self.camera_name}: {filename}")
                    self.trigger_completed_signal.emit(filename, self.camera_name)
                elif trigger_action == "capture":
                    cv2.imwrite(filename, self.last_frame)
                    self.log_signal.emit(f"📸 Captured image from {self.camera_name}: {filename}")
                    self.trigger_completed_signal.emit(filename, self.camera_name)
            except Exception as e:
                self.log_signal.emit(f"❌ Error: {str(e)}")
                self.trigger_completed_signal.emit("error", self.camera_name)
        else:
            self.log_signal.emit("❌ No frame available to capture")
            self.trigger_completed_signal.emit("error", self.camera_name)
        
    
        