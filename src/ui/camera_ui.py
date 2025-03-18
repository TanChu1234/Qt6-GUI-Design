from PySide6.QtWidgets import QWidget, QListWidgetItem, QMessageBox
from PySide6.QtGui import QIcon
from ui.camera_design import Ui_Form
from ui.camera_dialog import CameraDialog
from camera.cam_handler import CameraThread
from camera.check_ping import PingThread
from camera.camera_configuration_manerger import CameraConfigManager

class CameraWidget(QWidget):
    def __init__(self):
        super().__init__()
        # ✅ Load the UI
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.camera_threads = {}  # Store running threads
        self.camera_properties = {}  # Store all camera properties
        self.current_camera = None  # Track which camera is currently displayed
        self.displaying = False  # Track if we're currently displaying any camera
        
        # Initialize config manager
        self.config_manager = CameraConfigManager()
        
        # Define icon paths
        self.icon_offline = "src/asset/images/red.png"
        self.icon_online = "src/asset/images/green.png"
        self.icon_connecting = "src/asset/images/yellow.png"
    
            
        # ✅ Connect UI buttons
        self.ui.add_cam.clicked.connect(self.add_camera)
        self.ui.start_cam.clicked.connect(self.start_camera)
        self.ui.stop_cam.clicked.connect(self.stop_camera)
        self.ui.display.clicked.connect(self.toggle_display)
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

            # Add camera with connecting icon
            camera_name = camera_info["camera_name"]
            if not camera_name:  # If name is empty, generate default
                camera_name = f"Camera {self.ui.listWidget.count()}"
                camera_info["camera_name"] = camera_name
            
            # Add item with connecting icon
            item = QListWidgetItem(QIcon(self.icon_offline), camera_name)
            self.ui.listWidget.addItem(item)
            
            # Store camera properties with temporary status
            camera_info["status"] = "connecting"
            self.camera_properties[camera_name] = camera_info

            self.log_message(f"🔍 Checking connection to {ip_address}...")

            # Ping the camera
            ping_thread = PingThread(ip_address)
            ping_thread.result_signal.connect(self.handle_ping_result)

            # Prevent garbage collection
            if not hasattr(self, "ping_threads"):
                self.ping_threads = []
            self.ping_threads.append(ping_thread)

            ping_thread.start()
 
    # Modify handle_ping_result to update icons:
    def handle_ping_result(self, camera_ip, is_reachable):
        """Handle result of ping test."""
        # Find the camera in our list that matches this IP
        found_camera = None
        found_item = None
        
        for i in range(self.ui.listWidget.count()):
            item = self.ui.listWidget.item(i)
            camera_name = item.text()
            props = self.camera_properties.get(camera_name)
            if props and props["ip_address"] == camera_ip:
                found_camera = camera_name
                found_item = item
                break
        
        # If this was a new camera being added
        if not found_camera and hasattr(self, 'temp_camera_info'):
            camera_name = self.temp_camera_info["camera_name"]
            
            # The item should already be in the list with connecting icon
            for i in range(self.ui.listWidget.count()):
                item = self.ui.listWidget.item(i)
                if item.text() == camera_name:
                    found_camera = camera_name
                    found_item = item
                    break
        
        if found_camera and found_item:
            if is_reachable:
                # Update to online icon
                found_item.setIcon(QIcon(self.icon_offline))            
                # Save to config
                self.config_manager.add_camera(self.camera_properties[found_camera])
                
                self.log_message(f"✅ Camera {found_camera} is reachable at {camera_ip}")
            else:
                # Update to offline icon
                found_item.setIcon(QIcon(self.icon_offline))
                self.camera_properties[found_camera]["status"] = "offline"
                
                # Save to config (optional - you might not want to save offline cameras)
                self.config_manager.add_camera(self.camera_properties[found_camera])
                
                self.log_message(f"❌ Camera {found_camera} at {camera_ip} is unreachable!")
        else:
            self.log_message(f"⚠️ Could not find camera with IP {camera_ip} in the list!")
    
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
            self.stop_camera(camera_name)
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
                
        # Remove from configuration manager using the new method
        success = self.config_manager.remove_camera_by_name(camera_name)
        
        if success:
            self.log_message(f"🗑️ Removed camera '{camera_name}'")
        else:
            self.log_message(f"⚠️ Failed to remove camera '{camera_name}' from configuration")
        
        # Clear display if this was the current camera
        if self.current_camera == camera_name:
            self.ui.label.clear()
            self.current_camera = None
            self.displaying = False
            self.ui.display.setText("Display")
            
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
    
    def toggle_display(self):
        """Toggle display of the currently selected camera."""
        # Check if we currently have a displayed camera
        if self.displaying:
            # Stop displaying but keep threads running
            self.ui.label.clear()
            self.current_camera = None
            self.displaying = False
            self.ui.display.setText("Display")
            self.log_message("🔍 Display turned off")
            return
            
        # Start displaying a camera
        item = self.ui.listWidget.currentItem()
        if not item:
            self.log_message("⚠️ No camera selected to display!")
            return

        camera_name = item.text()

        # Check if camera is running, if not, suggest starting it
        if camera_name not in self.camera_threads:
            reply = QMessageBox.question(
                self,
                "Start Camera",
                f"Camera '{camera_name}' is not streaming. Start it now?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.start_camera(camera_name)
            else:
                return
                
        # Set this as the current camera to display
        self.current_camera = camera_name
        self.displaying = True
        self.ui.display.setText(f"Hide")
        self.log_message(f"🖥️ Now displaying {camera_name}")
    
    def start_camera(self, specific_camera=None):
        """Start real-time streaming for the selected or specified camera."""
        # If a specific camera was provided, use it, otherwise get from selection
        camera_name = specific_camera
        if not camera_name:
            item = self.ui.listWidget.currentItem()
            if not item:
                self.log_message("⚠️ No camera selected!")
                return
            camera_name = item.text()

        camera_props = self.camera_properties.get(camera_name, None)

        if not camera_props:
            self.log_message(f"❌ No properties found for {camera_name}")
            return

        # If thread already exists and is running, just log that
        if camera_name in self.camera_threads and self.camera_threads[camera_name].isRunning():
            self.log_message(f"ℹ️ {camera_name} is already streaming")
            return

        # Update status to connecting
        self.camera_properties[camera_name]["status"] = "connecting"
        
        # Find and update the icon in the list
        for i in range(self.ui.listWidget.count()):
            item = self.ui.listWidget.item(i)
            if item.text() == camera_name:
                item.setIcon(QIcon(self.icon_connecting))
                break

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
        self.camera_threads[camera_name].frame_signal.connect(
            lambda pixmap, cam=camera_name: self.handle_new_frame(pixmap, cam)
        )
        self.camera_threads[camera_name].log_signal.connect(self.log_message)
        self.camera_threads[camera_name].connection_status_signal.connect(
            lambda status, cam=camera_name: self.update_camera_status(cam, status)
        )
        
        # Handle thread finished signal to clean up properly
        self.camera_threads[camera_name].finished.connect(
            lambda cam=camera_name: self.handle_camera_stopped(cam)
        )
        
        self.camera_threads[camera_name].start()
        self.log_message(f"✅ Started streaming {camera_name}")

    # Add a new method to update camera status:
    def update_camera_status(self, camera_name, status):
        """Update the camera status and icon."""
        # Find the item in list
        for i in range(self.ui.listWidget.count()):
            item = self.ui.listWidget.item(i)
            if item.text() == camera_name:
                if status == "connected":
                    item.setIcon(QIcon(self.icon_online))
                    self.camera_properties[camera_name]["status"] = "online"
                elif status == "disconnected":
                    item.setIcon(QIcon(self.icon_offline))
                    self.camera_properties[camera_name]["status"] = "offline"
                elif status == "connecting":
                    item.setIcon(QIcon(self.icon_connecting))
                    self.camera_properties[camera_name]["status"] = "connecting"
                break

    
    def handle_new_frame(self, pixmap, camera_name):
        """Handle incoming frames from camera threads."""
        # Only update the display if this is the current camera AND display is enabled
        if self.displaying and camera_name == self.current_camera:
            self.ui.label.setPixmap(pixmap)
        
    # Modify handle_camera_stopped to update the icon:
    def handle_camera_stopped(self, camera_name):
        """Handle when a camera thread stops by itself (due to disconnection)"""
        if camera_name in self.camera_threads:
            # Remove the thread reference
            self.camera_threads[camera_name].wait()  # Ensure thread is fully finished
            del self.camera_threads[camera_name]
            
            # Update the status and icon
            self.update_camera_status(camera_name, "disconnected")
            
            # Clear the display if this was the current camera being displayed
            if self.displaying and self.current_camera == camera_name:
                self.ui.label.clear()  # Clear the display
                self.current_camera = None
                self.displaying = False
                self.ui.display.setText("Display")
                
            self.log_message(f"🛑 Camera {camera_name} stopped due to disconnection")
            
    # Modify stop_camera to update the icon status:
    def stop_camera(self, specific_camera=None):
        """Stop streaming for the selected or specified camera."""
        # If a specific camera was provided, use it, otherwise get from selection
        camera_name = specific_camera
        if not camera_name:
            item = self.ui.listWidget.currentItem()
            if not item:
                self.log_message("⚠️ No camera selected!")
                return
            camera_name = item.text()

        if camera_name in self.camera_threads:
            self.camera_threads[camera_name].stop()
            self.camera_threads[camera_name].wait()  # Ensure thread exits before removing it
            del self.camera_threads[camera_name]
            
            # Update status to offline
            self.update_camera_status(camera_name, "disconnected")
            
            # Clear the display if this was the current camera being displayed
            if self.displaying and self.current_camera == camera_name:
                self.ui.label.clear()
                self.current_camera = None
                self.displaying = False
                self.ui.display.setText("Display")
                
            self.log_message(f"🛑 Stopped {camera_name}")
        else:
            self.log_message(f"⚠️ No active stream for {camera_name}")

    # Modify load_saved_cameras to set appropriate icons based on saved status:
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
            
            # Set default status if not saved
            if "status" not in camera:
                camera["status"] = "offline"
                
            # Choose icon based on last known status
            icon_path = self.icon_offline  # Default to offline
            if camera["status"] == "online":
                icon_path = self.icon_online
            elif camera["status"] == "connecting":
                icon_path = self.icon_connecting
                
            item = QListWidgetItem(QIcon(icon_path), camera_name)
            self.ui.listWidget.addItem(item)
            
            # Store camera properties
            self.camera_properties[camera_name] = camera
    
    def closeEvent(self, event):
        """Ensure all camera threads stop when closing the window."""
        # Create a copy of the keys to avoid modification during iteration
        camera_names = list(self.camera_threads.keys())
        for camera_name in camera_names:
            self.camera_threads[camera_name].stop()
            self.camera_threads[camera_name].wait()
        
        # Save configuration on close - though this shouldn't be necessary
        # as we save after each add/remove/update  
        self.config_manager.save_config()
        event.accept()
        
    def run_ai_once(self):
        self.log_message("🤖 Running AI once...")

    def run_ai_continuous(self):
        self.log_message("♻️ Running AI continuously...")