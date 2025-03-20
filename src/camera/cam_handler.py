from PySide6.QtCore import QThread, Signal, QMutex, QWaitCondition
from PySide6.QtGui import QPixmap, QImage
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
        
        # Frame buffer
        self.last_frame = None
        
        # Output configuration
        self.save_path = "captures"  # Default path for saved images
        
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
    
    def _connect_with_timeout(self, cap, url, timeout=6):
        """Try to connect to the camera with a timeout."""
        start_time = time.time()
        
        # First attempt to open
        cap.open(url)
        
        # Check connection with timeout
        while time.time() - start_time < timeout:
            if cap.isOpened():
                # Test if we can actually get a frame
                ret, _ = cap.read()
                if ret:
                    return True
            
            # Check if we should stop trying
            self.mutex.lock()
            if not self.active:
                self.mutex.unlock()
                return False
            self.mutex.unlock()
            
            # Wait a bit before trying again
            time.sleep(0.1)  # Shorter sleep to be more responsive
            
            # Only try reopening if we're still within timeout
            if time.time() - start_time < timeout - 0.2:
                cap.release()  # Make sure to release before reopening
                cap.open(url)
        
        # If we get here, we've timed out
        cap.release()  # Make sure to release the capture
        return False
            
    def _process_frames(self, cap):
        """Process frames from the camera in a loop."""
        frame_count = 0
        last_log_time = time.time()
        frame_rate = 0
        
        while self.active:
            # Read frame with timeout handling
            ret, frame = cap.read()
            
            if not ret:
                # Try a couple more times before giving up
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
                    break

            # FPS calculation and logging
            frame_count += 1
            current_time = time.time()
            time_diff = current_time - last_log_time
            
            if time_diff >= 5.0:  # Log FPS every 5 seconds
                frame_rate = frame_count / time_diff
                self.log_signal.emit(f"📊 {self.camera_name} FPS: {frame_rate:.1f}")
                frame_count = 0
                last_log_time = current_time

            # Convert to RGB format for display
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Thread-safe operations on shared state
            self.mutex.lock()
            
            # Store the last frame for trigger processing (in BGR format)
            self.last_frame = frame.copy()
            
            # Check if we've been triggered
            if self.triggered:
                self._process_trigger()
                self.triggered = False
                
            # Can release the lock before UI operations
            self.mutex.unlock()
            
            # Convert to QImage - this can be slow so do it outside the lock
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Convert to pixmap and emit signal
            pixmap = QPixmap.fromImage(qt_image)
            self.frame_signal.emit(pixmap, self.camera_name)
            
            # Reduce CPU usage - adjust based on desired frame rate
            time.sleep(0.03)  # ~30 fps max
            
            # Check if we should stop - thread-safe way
            self.mutex.lock()
            should_continue = self.active
            self.mutex.unlock()
            
            if not should_continue:
                break
    
    def stop(self):
        """Stop the camera thread safely."""
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
        return True
        
    def _process_trigger(self):
        """Process the triggered action on the current frame."""
        if self.trigger_action == "capture":
            # Save the current frame to file
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{self.save_path}/{self.camera_name}_{timestamp}.jpg"
            
            if self.last_frame is not None:
                try:
                    cv2.imwrite(filename, self.last_frame)
                    self.log_signal.emit(f"📸 Captured image from {self.camera_name}: {filename}")
                    self.trigger_completed_signal.emit(filename, self.camera_name)
                except Exception as e:
                    self.log_signal.emit(f"❌ Error saving image: {str(e)}")
                    self.trigger_completed_signal.emit("error", self.camera_name)
            else:
                self.log_signal.emit(f"❌ No frame available to capture")
                self.trigger_completed_signal.emit("error", self.camera_name)
        else:
            # Handle other actions here
            self.log_signal.emit(f"⚠️ Unknown action: {self.trigger_action}")
            self.trigger_completed_signal.emit("error", self.camera_name)