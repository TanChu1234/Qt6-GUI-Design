from PySide6 import QtCore, QtGui, QtWidgets
import sys
import cv2
import json
import numpy as np
import os
import time
from datetime import datetime

class CameraWorker(QtCore.QObject):
    """Worker that handles camera operations in a separate QThread"""
    status_changed = QtCore.Signal(str, str)
    capture_ready = QtCore.Signal(str, np.ndarray)  # Camera name, image
    
    def __init__(self, camera_config):
        super().__init__()
        self.camera_config = camera_config
        self.camera_name = camera_config["camera_name"]
        
        # Build the camera URL based on configuration
        if camera_config["protocol"] == "HTTP":
            self.camera_stream_link = f"http://{camera_config['ip_address']}:{camera_config['port']}/video"
        else:
            username = camera_config["username"]
            password = camera_config["password"]
            self.camera_stream_link = f"rtsp://{username}:{password}@{camera_config['ip_address']}:{camera_config['port']}/cam/realmonitor?channel=1&subtype=0"
        
        self.capture = None
        self.running = False
        self.online = False
        self.last_reconnect_time = 0
        self.reconnect_timeout = 3  # seconds - faster reconnect
        self.perform_capture = False  # Flag to trigger a capture
        
        print(f'Created camera worker: {self.camera_name} at {self.camera_stream_link}')

    def connect_camera(self):
        """Try to connect to the camera"""
        try:
            self.status_changed.emit("Connecting...", "yellow")
            cap = cv2.VideoCapture(self.camera_stream_link)
            
            # Add timeout for connection
            connection_timeout = time.time() + 3  # 3 seconds timeout - faster connection
            while not cap.isOpened() and time.time() < connection_timeout:
                time.sleep(0.1)
            
            if not cap.isOpened():
                self.status_changed.emit("Failed to Connect", "red")
                return False
                
            # Try to read a test frame
            ret, frame = cap.read()
            if not ret:
                cap.release()
                self.status_changed.emit("Failed to Read Frame", "red")
                return False
                
            self.capture = cap
            self.online = True
            self.status_changed.emit("Ready (Spacebar to Capture)", "green")
            return True
            
        except Exception as e:
            self.status_changed.emit(f"Error: {str(e)[:30]}...", "red")
            print(f"Error connecting to {self.camera_name}: {e}")
            return False

    @QtCore.Slot()
    def start_capture(self):
        """Start the camera capture loop"""
        self.running = True
        
        if not self.connect_camera():
            # Schedule a reconnection attempt
            QtCore.QTimer.singleShot(self.reconnect_timeout * 1000, self.try_reconnect)
        
        # Start the lightweight monitoring loop
        while self.running:
            try:
                if self.capture and self.capture.isOpened() and self.online:
                    if self.perform_capture:
                        # Capture and emit the frame when requested
                        self.status_changed.emit("Capturing...", "orange")
                        
                        # Take multiple frames and use the last one (to ensure fresh frame)
                        for _ in range(3):  # Discard first frames to get a fresh one
                            ret, frame = self.capture.read()
                            time.sleep(0.05)  # Short delay between frames
                            
                        if ret:
                            self.capture_ready.emit(self.camera_name, frame)
                            self.status_changed.emit("Captured ✓", "green")
                        else:
                            self.status_changed.emit("Capture Failed", "red")
                        
                        self.perform_capture = False
                else:
                    # Camera is not ready for capture
                    if not self.online and time.time() - self.last_reconnect_time > self.reconnect_timeout:
                        self.try_reconnect()
                
                # Sleep to prevent CPU overload
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error in camera loop for {self.camera_name}: {e}")
                self.status_changed.emit(f"Error: {str(e)[:30]}...", "red")
                time.sleep(0.5)
                self.try_reconnect()
    
    @QtCore.Slot()
    def trigger_capture(self):
        """Trigger image capture"""
        if self.online and self.capture and self.capture.isOpened():
            self.perform_capture = True
            return True
        else:
            self.status_changed.emit("Cannot Capture - Camera Offline", "red")
            return False
    
    @QtCore.Slot()
    def try_reconnect(self):
        """Attempt to reconnect to the camera"""
        if not self.running:
            return
            
        current_time = time.time()
        if current_time - self.last_reconnect_time > self.reconnect_timeout:
            self.last_reconnect_time = current_time
            self.status_changed.emit("Reconnecting...", "yellow")
            print(f'Attempting to reconnect to {self.camera_name} at {self.camera_stream_link}')
            
            # Close existing capture if any
            if self.capture:
                self.capture.release()
                self.capture = None
            
            # Try to connect
            if not self.connect_camera():
                # Schedule another reconnection attempt
                QtCore.QTimer.singleShot(self.reconnect_timeout * 1000, self.try_reconnect)
    
    @QtCore.Slot()
    def stop(self):
        """Stop the worker"""
        self.running = False
        if self.capture:
            self.capture.release()
            self.capture = None


class CameraStatus(QtWidgets.QWidget):
    """Widget to display camera status"""
    
    def __init__(self, camera_config, parent=None):
        super().__init__(parent)
        
        self.camera_config = camera_config
        self.camera_name = camera_config["camera_name"]
        
        # Create status label
        self.status_label = QtWidgets.QLabel(f"{self.camera_name}: Initializing")
        self.status_label.setStyleSheet("background-color: #333; color: white; padding: 10px; font-size: 14px;")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # Create preview label (for when an image is captured)
        self.preview_label = QtWidgets.QLabel("Preview will appear here after capture")
        self.preview_label.setStyleSheet("background-color: #222; color: #777; padding: 5px;")
        self.preview_label.setAlignment(QtCore.Qt.AlignCenter)
        self.preview_label.setFixedHeight(100)  # Small preview height
        
        # Create layout
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.preview_label)
        
        # Create a worker and thread for this camera
        self.thread = QtCore.QThread()
        self.worker = CameraWorker(camera_config)
        self.worker.moveToThread(self.thread)
        
        # Connect signals and slots
        self.thread.started.connect(self.worker.start_capture)
        self.worker.status_changed.connect(self.update_status)
        self.worker.capture_ready.connect(self.process_captured_image)
        
        # Start the worker thread
        self.thread.start()
    
    def update_status(self, status_text, color):
        """Update the status label (called via signal from worker)"""
        self.status_label.setText(f"{self.camera_name}: {status_text}")
        self.status_label.setStyleSheet(f"background-color: #333; color: {color}; padding: 10px; font-size: 14px;")
    
    def trigger_capture(self):
        """Trigger the camera to capture an image"""
        return self.worker.trigger_capture()
    
    def process_captured_image(self, camera_name, image):
        """Process and save the captured image"""
        if image is None:
            print(f"Error: Received None image from {camera_name}")
            return
            
        try:
            # Create timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create directory if it doesn't exist
            save_dir = "captured_images"
            os.makedirs(save_dir, exist_ok=True)
            
            # Create filename
            filename = f"{save_dir}/{camera_name}_{timestamp}.jpg"
            
            # Save the image
            cv2.imwrite(filename, image)
            print(f"Saved image: {filename}")
            
            # Create a small preview
            h, w = image.shape[:2]
            preview_height = 100
            aspect_ratio = w / h
            preview_width = int(preview_height * aspect_ratio)
            preview = cv2.resize(image, (preview_width, preview_height))
            
            # Convert to QImage/QPixmap for display
            h, w, c = preview.shape
            bytesPerLine = w * 3
            qimg = QtGui.QImage(preview.data, w, h, bytesPerLine, QtGui.QImage.Format_RGB888).rgbSwapped()
            pixmap = QtGui.QPixmap.fromImage(qimg)
            
            # Display the preview
            self.preview_label.setPixmap(pixmap)
            self.preview_label.setToolTip(f"Saved as: {filename}")
            
        except Exception as e:
            print(f"Error processing captured image from {camera_name}: {e}")
    
    def closeEvent(self, event):
        """Handle the widget close event"""
        # Stop the worker and wait for the thread to finish
        self.worker.stop()
        self.thread.quit()
        self.thread.wait(1000)  # Wait up to 1 second
        event.accept()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Dual Camera Capture')
        
        # Create central widget and layout
        self.central_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)
        
        # Create a label with instructions
        self.instructions = QtWidgets.QLabel(
            "Use individual camera buttons or press SPACEBAR to capture from all cameras\n"
            "Images will be saved to the 'captured_images' folder in the current directory"
        )
        self.instructions.setStyleSheet("font-size: 16px; color: white; background-color: #444; padding: 15px;")
        self.instructions.setAlignment(QtCore.Qt.AlignCenter)
        
        # Create a horizontal layout for camera-specific capture buttons
        self.camera_button_layout = QtWidgets.QHBoxLayout()
        
        # Global capture and quit buttons
        self.capture_all_button = QtWidgets.QPushButton("Capture All Cameras (Spacebar)")
        self.capture_all_button.setStyleSheet("font-size: 16px; padding: 15px;")
        self.capture_all_button.clicked.connect(self.trigger_capture)
        
        self.quit_button = QtWidgets.QPushButton("Stop Cameras & Exit (Ctrl+Q)")
        self.quit_button.clicked.connect(self.close)
        
        # Add buttons to a button layout
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addWidget(self.capture_all_button)
        self.button_layout.addWidget(self.quit_button)
        
        # Grid layout for camera status widgets
        self.camera_layout = QtWidgets.QGridLayout()
        
        # Add widgets to main layout
        self.main_layout.addWidget(self.instructions)
        self.main_layout.addLayout(self.camera_layout)
        self.main_layout.addLayout(self.camera_button_layout)  # Add camera-specific button layout
        self.main_layout.addLayout(self.button_layout)
        
        # Status message
        self.status_message = QtWidgets.QLabel("Ready")
        self.status_message.setStyleSheet("font-size: 14px; padding: 5px; background-color: #333;")
        self.main_layout.addWidget(self.status_message)
        
        # Camera widgets and individual capture buttons will be stored here
        self.cameras = []
        self.camera_capture_buttons = []
        
        # Set up shortcut for quitting
        self.quit_shortcut = QtGui.QShortcut(QtGui.QKeySequence('Ctrl+Q'), self)
        self.quit_shortcut.activated.connect(self.close)
        
        # Set up shortcut for capture (spacebar)
        self.capture_shortcut = QtGui.QShortcut(QtGui.QKeySequence('Space'), self)
        self.capture_shortcut.activated.connect(self.trigger_capture)
    
    def add_camera(self, camera_widget, row, col):
        # Add camera to grid layout
        self.camera_layout.addWidget(camera_widget, row, col)
        self.cameras.append(camera_widget)
        
        # Create a capture button for this specific camera
        camera_name = camera_widget.camera_name
        capture_button = QtWidgets.QPushButton(f"Capture {camera_name}")
        capture_button.setStyleSheet("font-size: 14px; padding: 10px;")
        
        # Connect button to a lambda to capture this specific camera
        capture_button.clicked.connect(lambda checked, cam=camera_widget: self.trigger_single_camera_capture(cam))
        
        # Add button to camera button layout and tracking list
        self.camera_button_layout.addWidget(capture_button)
        self.camera_capture_buttons.append(capture_button)
    
    def trigger_single_camera_capture(self, camera):
        """Trigger capture for a specific camera"""
        if camera.trigger_capture():
            self.status_message.setText(f"Capturing {camera.camera_name}")
            self.status_message.setStyleSheet("font-size: 14px; padding: 5px; background-color: #333; color: green;")
        else:
            self.status_message.setText(f"Failed to capture {camera.camera_name}")
            self.status_message.setStyleSheet("font-size: 14px; padding: 5px; background-color: #333; color: red;")
    
    def trigger_capture(self):
        """Trigger capture on all cameras"""
        success_count = 0
        
        # Start a capture on all cameras
        for camera in self.cameras:
            if camera.trigger_capture():
                success_count += 1
        
        # Update status message
        if success_count == 0:
            self.status_message.setText("Failed to capture - No cameras ready")
            self.status_message.setStyleSheet("font-size: 14px; padding: 5px; background-color: #333; color: red;")
        elif success_count < len(self.cameras):
            self.status_message.setText(f"Partial capture ({success_count}/{len(self.cameras)} cameras)")
            self.status_message.setStyleSheet("font-size: 14px; padding: 5px; background-color: #333; color: orange;")
        else:
            self.status_message.setText(f"Capturing from all {len(self.cameras)} cameras")
            self.status_message.setStyleSheet("font-size: 14px; padding: 5px; background-color: #333; color: green;")
    
    def closeEvent(self, event):
        """Handle the window close event"""
        # Update status
        self.status_message.setText("Stopping cameras and exiting...")
        self.status_message.setStyleSheet("font-size: 14px; padding: 5px; background-color: #333; color: yellow;")
        QtWidgets.QApplication.processEvents()  # Make sure UI updates
        
        # Stop all cameras
        for camera in self.cameras:
            camera.worker.stop()
            camera.thread.quit()
        
        # Wait for all threads to finish
        for camera in self.cameras:
            camera.thread.wait(1000)
        
        event.accept()


def load_camera_config(config_file=None):
    """Load camera configuration from a JSON file or use default config"""
    if config_file and os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    else:
        return [
            {
                "camera_name": "tan",
                "ip_address": "192.168.3.2",
                "port": "8080",
                "username": "",
                "password": "",
                "protocol": "HTTP"
            },
            {
                "camera_name": "Camera2",
                "ip_address": "192.168.214.217",
                "port": "8080",
                "username": "",
                "password": "",
                "protocol": "HTTP"
            }
        ]


if __name__ == '__main__':
    # Create main application window
    app = QtWidgets.QApplication(sys.argv)
    
    # Apply dark style
    try:
        # First try to use QtMaterial if available
        from qt_material import apply_stylesheet
        apply_stylesheet(app, theme='dark_teal.xml')
    except ImportError:
        try:
            # Then try to use qdarkstyle
            import qdarkstyle
            app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6'))
        except ImportError:
            print("Neither qt_material nor qdarkstyle installed. Using default dark style.")
            # Set a dark palette as fallback
            dark_palette = QtGui.QPalette()
            dark_palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(53, 53, 53))
            dark_palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtCore.Qt.GlobalColor.white)
            dark_palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(25, 25, 25))
            dark_palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(53, 53, 53))
            dark_palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtCore.Qt.GlobalColor.white)
            dark_palette.setColor(QtGui.QPalette.ColorRole.ToolTipText, QtCore.Qt.GlobalColor.white)
            dark_palette.setColor(QtGui.QPalette.ColorRole.Text, QtCore.Qt.GlobalColor.white)
            dark_palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(53, 53, 53))
            dark_palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtCore.Qt.GlobalColor.white)
            dark_palette.setColor(QtGui.QPalette.ColorRole.Link, QtGui.QColor(42, 130, 218))
            dark_palette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(42, 130, 218))
            dark_palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtCore.Qt.GlobalColor.black)
            app.setPalette(dark_palette)
            app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")
    
    # Create main window
    main_window = MainWindow()
    
    # Load camera configuration
    camera_configs = load_camera_config()
    
    print('Creating Camera Status Widgets...')
    
    for i, camera_config in enumerate(camera_configs):
        # Create camera status widget
        camera = CameraStatus(camera_config)
        
        # Add to main window (arrange in a grid)
        row = i // 2
        col = i % 2
        main_window.add_camera(camera, row, col)
    
    # Set window size and show
    main_window.setGeometry(100, 100, 800, 400)
    main_window.show()
    
    # Start application event loop
    sys.exit(app.exec())
    