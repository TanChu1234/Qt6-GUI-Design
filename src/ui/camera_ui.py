from PySide6.QtWidgets import QWidget, QListWidgetItem, QMessageBox
from PySide6.QtGui import QIcon
from ui.camera_design import Ui_Form
from ui.camera_dialog import CameraDialog
from camera.cam_handler import CameraThread
from camera.check_ping import PingThread
from camera.camera_configuration_manerger import CameraConfigManager  # Import the new class

class CameraWidget(QWidget):
    def __init__(self):
        super().__init__()
        # ✅ Load the UI
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.camera_threads = {}  # Store running threads
        self.camera_properties = {}  # Store all camera properties
        self.current_camera = None  # Track which camera is currently displayed
        
        # Initialize config manager
        self.config_manager = CameraConfigManager()
            
        # ✅ Connect UI buttons
        self.ui.add_cam.clicked.connect(self.add_camera)
        self.ui.start_cam.clicked.connect(self.start_camera)
        self.ui.stop_cam.clicked.connect(self.stop_camera)
        self.ui.display.clicked.connect(self.display)
        self.ui.run_once.clicked.connect(self.run_ai_once)
        self.ui.run_continuous.clicked.connect(self.run_ai_continuous)
        self.ui.listWidget.itemClicked.connect(self.select_camera)  # Handle camera selection
        self.ui.remove_cam.clicked.connect(self.remove_camera)
        
        # Load saved camera configurations
        self.load_saved_cameras()
        
    def load_saved_cameras(self):
        """Load saved camera configurations from file"""
        cameras = self.config_manager.load_config()
        self.log_message(f"📋 Loaded {len(cameras)} saved cameras")
        
        # Add cameras to the list and properties dictionary
        for camera in cameras:
            camera_name = camera["camera_name"]
            if not camera_name:  # If name is empty, generate default
                camera_name = f"Camera {self.ui.listWidget.count()}"
                camera["camera_name"] = camera_name
                
            item = QListWidgetItem(QIcon("D:/Qt6 GUI Design/src/asset/images/icons8-camera-48.png"), camera_name)
            self.ui.listWidget.addItem(item)
            
            # Store camera properties
            self.camera_properties[camera_name] = camera
            
    def log_message(self, message):
        """Append log messages to the log listWidget."""
        self.ui.log_list.addItem(message)  # Ensure log_listWidget exists in UI
        self.ui.log_list.scrollToBottom()  # Auto-scroll to the latest message

    # ✅ Camera-specific functions
    def add_camera(self):
        """Show the custom camera dialog and get user input."""
        dialog = CameraDialog(self)
        if dialog.exec():  # If user clicks OK
            camera_info = dialog.get_camera_info()
            ip_address = camera_info["ip_address"]
            
            # Store camera info temporarily
            self.temp_camera_info = camera_info

            self.log_message(f"🔍 Checking connection to {ip_address}...")

            # Ping the camera
            ping_thread = PingThread(ip_address)
            ping_thread.result_signal.connect(self.handle_ping_result)

            # Prevent garbage collection
            if not hasattr(self, "ping_threads"):
                self.ping_threads = []
            self.ping_threads.append(ping_thread)

            ping_thread.start()
 
    def handle_ping_result(self, camera_ip, is_reachable):
        """Handle result of ping test."""
        if is_reachable:
            # Use the camera_name from dialog instead of generating one
            camera_name = self.temp_camera_info["camera_name"]
            if not camera_name:  # If name is empty, generate default
                camera_name = f"Camera {self.ui.listWidget.count()}"
                self.temp_camera_info["camera_name"] = camera_name  # Update the name in properties

            # Check if camera already exists in list
            for i in range(self.ui.listWidget.count()):
                item = self.ui.listWidget.item(i)
                props = self.camera_properties.get(item.text())
                if props and props["ip_address"] == camera_ip:
                    # Update existing camera
                    item.setText(camera_name)
                    self.camera_properties[camera_name] = self.temp_camera_info
                    
                    # Save to config
                    self.config_manager.add_camera(self.temp_camera_info)
                    
                    self.log_message(f"🔄 Updated {camera_name} with IP {camera_ip}")
                    return

            # Add new camera
            item = QListWidgetItem(QIcon("D:/Qt6 GUI Design/src/asset/images/icons8-camera-48.png"), camera_name)
            self.ui.listWidget.addItem(item)

            # Store all camera properties
            self.camera_properties[camera_name] = self.temp_camera_info
            
            # Save to config
            self.config_manager.add_camera(self.temp_camera_info)
            
            self.log_message(f"✅ Added {camera_name} with IP {camera_ip}")
        else:
            self.log_message(f"❌ Camera at {camera_ip} is unreachable!")
    
    def remove_camera(self):
        """Remove the selected camera from the list and configuration."""
        item = self.ui.listWidget.currentItem()
        if not item:
            self.log_message("⚠️ No camera selected to remove!")
            return

        camera_name = item.text()
        
        # Check if the camera is currently streaming
        if camera_name in self.camera_threads:
            # Ask the user to confirm stopping and removing
            reply = QMessageBox.question(
                self,
                "Remove Active Camera",
                f"Camera '{camera_name}' is currently streaming. Stop and remove it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
                
            # Stop the camera thread first
            self.stop_camera()
        else:
            # Just confirm removal for inactive cameras
            reply = QMessageBox.question(
                self,
                "Remove Camera",
                f"Are you sure you want to remove camera '{camera_name}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
                
        # Remove camera from list widget
        row = self.ui.listWidget.row(item)
        self.ui.listWidget.takeItem(row)
        
        # Remove from our properties dictionary
        if camera_name in self.camera_properties:
            del self.camera_properties[camera_name]
            
        # Remove from configuration manager
        success = self.config_manager.remove_camera(camera_name)
        if success:
            self.log_message(f"🗑️ Removed camera '{camera_name}'")
        else:
            self.log_message(f"⚠️ Failed to remove camera '{camera_name}' from configuration")
        
        # Clear display if this was the current camera
        if self.current_camera == camera_name:
            self.ui.label.clear()
            self.current_camera = None
            
    def select_camera(self, item):
        """Handle camera selection from listWidget."""
        camera_name = item.text()
        camera_props = self.camera_properties.get(camera_name, None)

        if camera_props:
            self.log_message(f"📷 Selected {camera_name}:")
            self.log_message(f"   IP: {camera_props['ip_address']}")
            self.log_message(f"   Port: {camera_props['port']}")
            self.log_message(f"   Username: {camera_props['username']}")
            # Don't log password for security reasons
        else:
            self.log_message(f"⚠️ No properties found for {camera_name}")
            
    def display(self):
        self.log_message("🔍 Searching for cameras...")
    
    def start_camera(self):
        """Start real-time streaming for the selected camera."""
        item = self.ui.listWidget.currentItem()
        if not item:
            self.log_message("⚠️ No camera selected!")
            return

        camera_name = item.text()
        camera_props = self.camera_properties.get(camera_name, None)

        if not camera_props:
            self.log_message(f"❌ No properties found for {camera_name}")
            return

        # Stop existing thread if running
        if camera_name in self.camera_threads:
            self.stop_camera()

        # Start new camera thread with all properties
        self.camera_threads[camera_name] = CameraThread(
            camera_props["ip_address"],
            camera_props["port"],
            camera_props["username"],
            camera_props["password"],
            camera_props["camera_name"],
            camera_props["protocol"],
        )
        
        # Connect signals
        self.camera_threads[camera_name].frame_signal.connect(self.update_frame)
        self.camera_threads[camera_name].log_signal.connect(self.log_message)
        
        # Handle thread finished signal to clean up properly
        self.camera_threads[camera_name].finished.connect(lambda: self.handle_camera_stopped(camera_name))
        
        self.camera_threads[camera_name].start()
        self.current_camera = camera_name
        self.log_message(f"✅ Started streaming {camera_name}")
        
    def handle_camera_stopped(self, camera_name):
        """Handle when a camera thread stops by itself (due to disconnection)"""
        if camera_name in self.camera_threads:
            # Remove the thread reference
            self.camera_threads[camera_name].wait()  # Ensure thread is fully finished
            del self.camera_threads[camera_name]
            
            # Clear the display if this was the current camera
            if self.current_camera == camera_name:
                self.ui.label.clear()  # Clear the display
                self.current_camera = None
                
            self.log_message(f"🛑 Camera {camera_name} stopped due to disconnection")
            
    def stop_camera(self):
        """Stop streaming for the selected camera."""
        item = self.ui.listWidget.currentItem()
        if not item:
            self.log_message("⚠️ No camera selected!")
            return

        camera_name = item.text()

        if camera_name in self.camera_threads:
            self.camera_threads[camera_name].stop()
            self.camera_threads[camera_name].wait()  # Ensure thread exits before removing it
            del self.camera_threads[camera_name]
            # # Clear the display if this was the current camera
            # if self.current_camera == camera_name:
            #     self.ui.label.clear()  # Clear the display
            #     self.current_camera = None
                
            self.log_message(f"🛑 Stopped {camera_name}")
        else:
            self.log_message(f"⚠️ No active stream for {camera_name}")

    def update_frame(self, pixmap):
        """Update the QLabel with the latest frame."""
        self.ui.label.setPixmap(pixmap)  # Display the frame

    def closeEvent(self, event):
        """Ensure all camera threads stop when closing the window."""
        for thread in self.camera_threads.values():
            thread.stop()
        # Save configuration on close - though this shouldn't be necessary
        # as we save after each add/remove/update
        self.config_manager.save_config()
        event.accept()
        
    def run_ai_once(self):
        self.log_message("🤖 Running AI once...")

    def run_ai_continuous(self):
        self.log_message("♻️ Running AI continuously...")