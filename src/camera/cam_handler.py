from PySide6.QtCore import QThread, Signal, QMutex, QWaitCondition, QObject
from PySide6.QtGui import QPixmap, QImage
import cv2
import time
import os

class CameraThread(QThread):
    """Thread class for handling camera streaming and operations."""
    
    # Define signals
    frame_signal = Signal(QPixmap, str)  # For UI updates (pixmap, camera_name)
    log_signal = Signal(str)  # For logging messages
    person_count = Signal(int)  # For reporting person counts
    connection_status_signal = Signal(str, str)  # (status, camera_name)
    trigger_completed_signal = Signal(str, str)  # (result, camera_name)
    
    def __init__(self, ip, port, username, password, camera_name, protocol, yolo_detector=None):
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

        # Frame buffer
        self.last_frame = None
        
        # Output configuration
        self.save_path = "outputs/captures"  # Default path for saved images
        self.result_path = "outputs/detections"
        # Create the save directory if it doesn't exist
        for path in [self.save_path, self.result_path]:
            if not os.path.exists(path):
                os.makedirs(path)
            
        # Store the YOLO detector instance
        self.yolo_detector = yolo_detector
        
    def run(self):
        """Main thread execution method."""
        self.active = True
        self.last_frame = None  # Clear any previous frame
        
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
        if not self._connect_with_timeout(cap, url):
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
            try:
                cap.release()
                self.log_signal.emit(f"📤 Released camera resources for {self.camera_name}")
            except Exception as e:
                self.log_signal.emit(f"⚠️ Error releasing camera resources: {str(e)}")
                
            # Make sure we're marked as disconnected
            self.connection_status_signal.emit("disconnected", self.camera_name)
    
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
    
    def _connect_with_timeout(self, cap, url):
      
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
        
        try:
            while self.active:
                # Check for stop condition more frequently
                if not self._should_continue():
                    break
                    
                ret, frame = self._read_frame_with_retries(cap)
                if not ret:
                    break

                rgb_frame = self._convert_frame_to_rgb(frame)
                self._handle_frame(rgb_frame, frame)
                self._emit_frame_signal(rgb_frame)
                
                # Shorter sleep time to check active flag more often
                time.sleep(0.01)  
        except Exception as e:
            self.log_signal.emit(f"❌ Error in frame processing: {str(e)}")
        finally:
            # Force release resources
            self.last_frame = None
            # Try to encourage garbage collection
            import gc
            gc.collect()
  
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
        """Handle frame processing and triggering with proper lock handling."""
        try:
            self.mutex.lock()
            # Only make a copy if needed for a trigger, otherwise just reference
            if self.triggered:
                self.last_frame = frame.copy()
                self._process_trigger(self.trigger_action)
                self.triggered = False
            else:
                # Just keep a reference without copying if not triggering
                self.last_frame = frame
        finally:
            self.mutex.unlock()  # Always ensure mutex is unlocked

    def _emit_frame_signal(self, rgb_frame):
        """Convert frame to QPixmap and emit frame signal."""
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.frame_signal.emit(pixmap, self.camera_name)

    def _should_continue(self):
        """Check if the thread should continue running."""
        try:
            self.mutex.lock()
            should_continue = self.active
            return should_continue
        finally:
            self.mutex.unlock()  # Always ensure mutex is unlocked
    
    def stop(self):
        """Stop the camera thread safely."""
        try:
            self.mutex.lock()
            self.active = False
            self.triggered = False  # Reset trigger state
            self.trigger_action = None  # Clear any pending trigger actions
        finally:
            self.mutex.unlock()  # Always ensure mutex is unlocked
            
        # Wake any waiting threads
        self.condition.wakeAll()
        
        # Remove frame buffer to free memory
        self.last_frame = None
    
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
        
        if self.last_frame is not None:
            try:   
                if trigger_action == "ai" and self.yolo_detector is not None:
                    filename = f"{self.result_path}/{self.camera_name}_{timestamp}.jpg"
                    
                    # Run inference - now only returns person_count
                    _, detection_summary, person_count = self.yolo_detector.detect(
                        self.last_frame, 
                        filename
                    )
                    
                    # Emit the person count signal
                    self.person_count.emit(person_count)
                    
                    # Log detection results
                    if detection_summary:
                        self.log_signal.emit(f"🤖 AI detection found: {detection_summary} in {self.camera_name}")
                    else:
                        self.log_signal.emit(f"🤖 No objects detected with confidence > 0.6 in {self.camera_name}")
                    
                    # Log the person count value
                    self.log_signal.emit(f"🔍 Person count for {self.camera_name}: {person_count}")
                    
                    self.log_signal.emit(f"🤖 Detection results saved to: {filename}")
                    
                    # Include the person count in the trigger_completed_signal
                    # Format: "filename|person_count"
                    self.trigger_completed_signal.emit(f"{filename}|{person_count}", self.camera_name)
                
                elif trigger_action == "capture":
                    filename = f"{self.save_path}/{self.camera_name}_{timestamp}.jpg"
                    cv2.imwrite(filename, self.last_frame)
                    self.log_signal.emit(f"📸 Captured image from {self.camera_name}: {filename}")
                    
                    # For regular captures, emit 0 for person_count
                    self.person_count.emit(0)
                    
                    # Include count=0 for regular captures
                    self.trigger_completed_signal.emit(f"{filename}|0", self.camera_name)
                    
            except Exception as e:
                self.log_signal.emit(f"❌ Error: {str(e)}")
                # For errors, emit 0 for person_count
                self.person_count.emit(0)
                self.trigger_completed_signal.emit("error", self.camera_name)
        else:
            self.log_signal.emit("❌ No frame available to capture")
            # For errors, emit 0 for person_count
            self.person_count.emit(0)
            self.trigger_completed_signal.emit("error", self.camera_name)
                  
class CameraStopWorker(QObject):
    """Worker class to stop cameras in a separate thread."""
    progress_signal = Signal(int, str)  # (progress value, camera name)
    finished_signal = Signal(list, list)  # (stopped_cameras, failed_cameras)

    def __init__(self, camera_threads, stop_camera_method):
        super().__init__()
        self.camera_threads = camera_threads
        self.stop_camera_method = stop_camera_method  # Pass stop_camera function

    def run(self):
        """Stops cameras in a background thread."""
        connected_cameras = [name for name, thread in self.camera_threads.items() if thread.isRunning()]
        # total_cameras = len(connected_cameras)

        stopped_cameras = []
        failed_cameras = []

        for i, camera_name in enumerate(connected_cameras):
            success = self.stop_camera_method(camera_name)
            if success:
                stopped_cameras.append(camera_name)
            else:
                failed_cameras.append(camera_name)

            # Emit progress update
            self.progress_signal.emit(i + 1, camera_name)

        # Emit finished signal
        self.finished_signal.emit(stopped_cameras, failed_cameras)