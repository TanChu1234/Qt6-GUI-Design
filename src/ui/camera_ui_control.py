from PySide6.QtWidgets import QWidget, QListWidgetItem, QMessageBox, QFileDialog
from PySide6.QtGui import QIcon
from PySide6.QtCore import QThread
from ui.camera_design import Ui_Form
from ui.camera_dialog import CameraDialog
from camera.cam_handler import CameraThread
from camera.check_ping import PingThread
from camera.camera_configuration_manager import CameraConfigManager
from datetime import datetime
import os
import json

class CameraWidget(QWidget):
    """Main widget for camera management and display."""
    
    """ Initialize and set configuration """
    def __init__(self):
        super().__init__()
        # UI Setup
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        # Instance variables
        self.camera_threads = {}  # Store running camera threads
        self.camera_properties = {}  # Store all camera properties
        self.current_camera = None  # Track which camera is currently displayed
        self.displaying = False  # Track if we're currently displaying any camera
        self.trigger_results = {}  # Store results from triggers
        self.ping_threads = []  # Store ping threads to prevent garbage collection
        
        # Initialize config manager
        self.config_manager = CameraConfigManager()
        
        # Define icon paths
        self.icon_offline = "src/asset/images/red.png"
        self.icon_online = "src/asset/images/green.png"
        self.icon_connecting = "src/asset/images/yellow.png"
        
        self._setup_ui()
        self.load_saved_cameras()
    
    def _setup_ui(self):
        """Connect UI elements to their handlers."""
        # Set placeholder text for the lineEdit
        self.ui.lineEdit.setPlaceholderText("Enter camera command (e.g., cam1, trigger cam2)")
        
        # Connect UI buttons
        self.ui.add_cam.clicked.connect(self.add_camera)
        self.ui.start_cam.clicked.connect(self.start_camera)
        self.ui.stop_cam.clicked.connect(self.stop_camera)
        self.ui.display.clicked.connect(self.toggle_display)
        self.ui.trigger_http.clicked.connect(self.trigger_http)
        self.ui.trigger_tcp.clicked.connect(self.trigger)
        self.ui.listWidget.itemClicked.connect(self.select_camera)
        self.ui.remove_cam.clicked.connect(self.remove_camera)
    
    def load_saved_cameras(self):
        """Load saved camera configurations from file"""
        cameras = self.config_manager.load_config()
        self.log_message(f"📋 Loaded {len(cameras)} saved cameras")
        
        # Add cameras to the list and properties dictionary
        for camera in cameras:
            camera_name = camera["camera_name"]
            if not camera_name:  # If name is empty, generate default
                camera_name = f"Camera {self.ui.listWidget.count() + 1}"
                camera["camera_name"] = camera_name
                
            # Add with offline icon (cameras start offline)
            item = QListWidgetItem(QIcon(self.icon_offline), camera_name)
            self.ui.listWidget.addItem(item)
            
            # Store camera properties (without status)
            self.camera_properties[camera_name] = camera
    
    """ User Interface Management """
    def log_message(self, message):
        """Append log messages with a timestamp to the log listWidget and export if exceeding 100 lines."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"

        self.ui.log_list.addItem(log_entry)
        self.ui.log_list.scrollToBottom()  # Auto-scroll to the latest message

        # Check if log_list exceeds 100 items
        if self.ui.log_list.count() > 100:
            self.export_log()

    def export_log(self):
        """Export log messages to 'outputs/logs' folder and clear the list."""
        log_folder = "outputs/logs"
        os.makedirs(log_folder, exist_ok=True)  # Ensure the directory exists

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(log_folder, f"log_{timestamp}.txt")

        with open(filename, "w", encoding="utf-8") as file:
            for index in range(self.ui.log_list.count()):
                file.write(self.ui.log_list.item(index).text() + "\n")

        self.ui.log_list.clear()  # Clear the log after exporting
        print(f"Log exported to {filename}")  # Debug print
    
    def select_camera(self, item):
        """Handle camera selection from listWidget."""
        camera_name = item.text()
        camera_props = self.camera_properties.get(camera_name, None)

        if camera_props:
            log_entry = (
            f"📷 Selected {camera_name}:\n"
            f"   IP: {camera_props['ip_address']}\n"
            f"   Port: {camera_props['port']}\n"
            f"   Username: {camera_props['username']}"
            )
            self.log_message(log_entry)
            # Don't log password for security reasons
        else:
            self.log_message(f"⚠️ No properties found for {camera_name}")
    
    def toggle_display(self):
        """Toggle display of the currently selected camera."""
        # Check if we currently have a displayed camera
        if self.displaying:
            # Stop displaying but keep threads running
            self._clear_display()
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
        self.ui.display.setText("HIDE")
        self.log_message(f"🖥️ Now displaying {camera_name}")
    
    def _clear_display(self):
        """Helper method to clear the display and reset display state."""
        self.ui.label.clear()
        self.current_camera = None
        self.displaying = False
        self.ui.display.setText("DISPLAY")
    
    """ Camera Management (Add, Remove, Save, Check Connection) """
    def add_camera(self):
        """Show the custom camera dialog and get user input."""
        dialog = CameraDialog()
        if not dialog.exec():  # If user cancels
            return
            
        camera_info = dialog.get_camera_info()
        ip_address = camera_info["ip_address"]
        
        # Generate default name if empty
        camera_name = camera_info["camera_name"]
        if not camera_name:
            camera_name = f"Camera {self.ui.listWidget.count()}"
            camera_info["camera_name"] = camera_name
        
        # Add item with connecting icon
        item = QListWidgetItem(QIcon(self.icon_connecting), camera_name)
        self.ui.listWidget.addItem(item)
        
        # Store camera properties without status
        self.camera_properties[camera_name] = camera_info

        self.log_message(f"🔍 Checking connection to {ip_address}...")

        # Ping the camera
        ping_thread = PingThread(ip_address)
        ping_thread.result_signal.connect(self._handle_ping_result)
        self.ping_threads.append(ping_thread)
        ping_thread.start()
 
    def _handle_ping_result(self, camera_ip, is_reachable):
        """Handle result of ping test."""
        # Find the camera in our list that matches this IP
        found_camera = None
        found_item = None
        found_index = -1
        
        # Search for camera with this IP in our properties
        for i in range(self.ui.listWidget.count()):
            item = self.ui.listWidget.item(i)
            camera_name = item.text()
            props = self.camera_properties.get(camera_name)
            
            if props and props["ip_address"] == camera_ip:
                found_camera = camera_name
                found_item = item
                found_index = i
                break
        
        if not found_camera or not found_item:
            self.log_message(f"⚠️ Could not find camera with IP {camera_ip} in the list!")
            return
            
        if is_reachable:
            # Update to offline icon initially (will update when connected)
            found_item.setIcon(QIcon(self.icon_offline))
            
            # Save to config
            self.config_manager.add_camera(self.camera_properties[found_camera])
            self.log_message(f"✅ Camera {found_camera} is reachable at {camera_ip}")
        else:
            # Remove the camera from the list since it's unreachable
            self.ui.listWidget.takeItem(found_index)
            
            # Remove from properties dictionary
            if found_camera in self.camera_properties:
                del self.camera_properties[found_camera]
                
            self.log_message(f"❌ Camera {found_camera} at {camera_ip} is unreachable! Camera removed.")
            
        # Clean up the ping thread
        for i, thread in enumerate(self.ping_threads):
            if not thread.isRunning():
                self.ping_threads.pop(i)
    
    def remove_camera(self):
        """Remove the selected camera from the list and configuration."""
        item = self.ui.listWidget.currentItem()
        if not item:
            self.log_message("⚠️ No camera selected to remove!")
            return

        camera_name = item.text()
        
        # Check if the camera is currently streaming
        if camera_name in self.camera_threads:
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
                
        # Remove from configuration manager
        success = self.config_manager.remove_camera_by_name(camera_name)
        
        if success:
            self.log_message(f"🗑️ Removed camera '{camera_name}'")
        else:
            self.log_message(f"⚠️ Failed to remove camera '{camera_name}' from configuration")
        
        # Clear display if this was the current camera
        if self.current_camera == camera_name:
            self._clear_display()

    def _update_camera_icon(self, camera_name, status):
        """Update the camera icon based on status."""
        icon_map = {
            "connecting": self.icon_connecting,
            "connected": self.icon_online,
            "disconnected": self.icon_offline
        }
        
        if status not in icon_map:
            return
            
        # Update icon in list
        for i in range(self.ui.listWidget.count()):
            item = self.ui.listWidget.item(i)
            if item.text() == camera_name:
                item.setIcon(QIcon(icon_map[status]))
                break

    def _update_camera_status(self, camera_name, status):
        """Update the camera icon only."""
        # Just update the icon
        self._update_camera_icon(camera_name, status)
    
    def closeEvent(self, event):
        """Ensure all camera threads stop when closing the window."""
        # Create a copy of the keys to avoid modification during iteration
        camera_names = list(self.camera_threads.keys())
        for camera_name in camera_names:
            self.camera_threads[camera_name].stop()
            try:
                self.camera_threads[camera_name].wait(1000)  # Wait with timeout
            except RuntimeError:
                pass  # Thread might already be finished
        
        # Save configuration on close
        self.config_manager.save_config()
        
        # Also clean up ping threads
        for thread in self.ping_threads:
            if thread.isRunning():
                try: 
                    thread.terminate()
                    thread.wait(500)
                except:
                    pass
                    
        event.accept()
    
    """ Camera Operation """
    # Start Camera
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

        # Update icon to connecting
        self._update_camera_icon(camera_name, "connecting")

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
        thread = self.camera_threads[camera_name]
        thread.frame_signal.connect(
            lambda pixmap, cam=camera_name: self._handle_new_frame(pixmap, cam)
        )
        thread.log_signal.connect(self.log_message)
        thread.connection_status_signal.connect(
            lambda status, cam=camera_name: self._update_camera_status(cam, status)
        )
        thread.trigger_completed_signal.connect(
            lambda result, cam=camera_name: self._handle_trigger_result(result, cam)
        )
        
        # Handle thread finished signal to clean up properly
        thread.finished.connect(
            lambda cam=camera_name: self._handle_camera_stopped(cam)
        )
        
        thread.start()
        self.log_message(f"✅ Started streaming {camera_name}")

    def _handle_new_frame(self, pixmap, camera_name):
        """Handle incoming frames from camera threads."""
        # Only update the display if this is the current camera AND display is enabled
        if self.displaying and camera_name == self.current_camera:
            self.ui.label.setPixmap(pixmap)
        
    def _handle_camera_stopped(self, camera_name):
        """Handle when a camera thread stops by itself (due to disconnection)"""
        if camera_name not in self.camera_threads:
            return
            
        # Ensure thread is fully finished
        try:
            self.camera_threads[camera_name].wait(1000)  # Wait with timeout
        except RuntimeError:
            pass  # Thread might already be finished
            
        # Remove the thread reference
        del self.camera_threads[camera_name]
        
        # Update the icon
        self._update_camera_icon(camera_name, "disconnected")
        
        # Clear the display if this was the current camera being displayed
        if self.displaying and self.current_camera == camera_name:
            self._clear_display()
                
        self.log_message(f"🛑 Camera {camera_name} stopped due to disconnection")
    
    # Stop Camera        
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
            thread = self.camera_threads[camera_name]
            thread.stop()
            
            try:
                thread.wait(1000)  # Wait with timeout
            except RuntimeError:
                pass  # Thread might already be finished
                
            del self.camera_threads[camera_name]
            
            # Update icon to offline
            self._update_camera_icon(camera_name, "disconnected")
            
            # Clear the display if this was the current camera being displayed
            if self.displaying and self.current_camera == camera_name:
                self._clear_display()
                
            self.log_message(f"🛑 Stopped {camera_name}")
        else:
            self.log_message(f"⚠️ No active stream for {camera_name}")
   
    def _handle_trigger_result(self, result, camera_name):
        """
        Handle the result of a camera trigger.
        
        Args:
            result (str): Result of the trigger operation
            camera_name (str): Name of the camera that was triggered
        """
        if result == "error":
            self.log_message(f"❌ Trigger failed for {camera_name}")
        else:
            # Successful trigger, log the result (usually the filename)
            self.log_message(f"✅ Trigger successful for {camera_name}: {result}")
        
        # Store the result in trigger_results dictionary
        self.trigger_results[camera_name] = result

    def trigger_http(self):
        """
        Trigger cameras by JSON configuration with signal-based handling.
        """
        # Open file dialog to select JSON file
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Camera Trigger JSON", 
            "", 
            "JSON Files (*.json);;All Files (*)"
        )
        
        # If no file selected, return
        if not file_path:
            self.log_message("⚠️ No JSON file selected")
            return
        
        try:
            # Read and parse the JSON file
            with open(file_path, 'r', encoding='utf-8') as file:
                trigger_config = json.load(file)
            
            # Validate JSON structure and process triggers
            if not isinstance(trigger_config, list):
                self.log_message("❌ Invalid JSON format. Expected a list of camera triggers.")
                return
            
            # Track trigger results for summary
            successful_triggers = []
            failed_triggers = []
            
            # Process each trigger in the JSON
            for trigger in trigger_config:
                # Validate trigger entry
                if not isinstance(trigger, dict):
                    self.log_message(f"⚠️ Skipping invalid trigger: {trigger}")
                    continue
                
                # Extract and validate camera name
                camera_name = trigger.get('camera_name')
                if not camera_name:
                    self.log_message("⚠️ Skipping trigger without camera name")
                    continue
                
                # Find the camera by partial name
                target_camera = self._find_camera_by_partial_name(camera_name)
                
                if target_camera:
                    # Determine action (default to capture)
                    action = trigger.get('type', 'capture').lower()
                    
                    # Attempt to trigger the camera
                    try:
                        result = self._trigger_and_handle_camera(target_camera, action)
                        if result:
                            successful_triggers.append(target_camera)
                        else:
                            failed_triggers.append(target_camera)
                    except Exception as e:
                        self.log_message(f"❌ Error triggering {target_camera}: {str(e)}")
                        failed_triggers.append(target_camera)
                else:
                    self.log_message(f"❌ Camera matching '{camera_name}' not found")
                    failed_triggers.append(camera_name)
            
            # Provide summary notification
            self._show_trigger_summary(successful_triggers, failed_triggers)
        
        except (json.JSONDecodeError, IOError) as e:
            self.log_message(f"❌ File error: {str(e)}")
        except Exception as e:
            self.log_message(f"❌ Unexpected error during trigger: {str(e)}")

    def _trigger_and_handle_camera(self, camera_name, action="capture"):
        """
        Comprehensive method to trigger a camera and handle its lifecycle.
        
        Returns:
            bool: True if trigger was successful, False otherwise
        """
        # Ensure camera is running
        if camera_name not in self.camera_threads or not self.camera_threads[camera_name].isRunning():
            try:
                self.log_message(f"🔄 Starting camera {camera_name} before triggering...")
                self.start_camera(camera_name)
                
                # Wait for camera to connect
                QThread.msleep(300)
                
                # Verify camera started
                if camera_name not in self.camera_threads or not self.camera_threads[camera_name].isRunning():
                    self.log_message(f"❌ Failed to start camera {camera_name} for triggering")
                    return False
            except Exception as e:
                self.log_message(f"❌ Error starting {camera_name}: {str(e)}")
                return False
        
        # Prepare trigger signal connection
        thread = self.camera_threads[camera_name]
        if not hasattr(thread, "_trigger_connected"):
            thread.trigger_completed_signal.connect(
                lambda result, cam=camera_name: self._handle_trigger_result(result, cam)
            )
            thread._trigger_connected = True
        
        # Trigger the camera
        try:
            trigger_result = thread.trigger(action)
            if trigger_result:
                self.log_message(f"🔔 Triggered {camera_name} with action: {action}")
                return True
            else:
                self.log_message(f"❌ Trigger failed for {camera_name}")
                return False
        except Exception as e:
            self.log_message(f"❌ Trigger error for {camera_name}: {str(e)}")
            return False

    def _handle_trigger_result(self, result, camera_name):
        """Handle the result of a camera trigger and manage its state."""
        # Determine and log result
        if result == "error":
            self.log_message(f"❌ Trigger failed for {camera_name}")
        else:
            # Store and log result
            self.trigger_results[camera_name] = result
            message = (f"📸 Image captured from {camera_name}: {result}" 
                    if result.endswith(".jpg") 
                    else f"✅ Trigger result for {camera_name}: {result}")
            self.log_message(message)
        
        # Stop the camera and manage display
        self.log_message(f"🛑 Stopping camera {camera_name} after trigger")
        self.stop_camera(camera_name)
        
        # Clear display if this was the current camera
        if self.displaying and self.current_camera == camera_name:
            self._clear_display()

    def _show_trigger_summary(self, successful_triggers, failed_triggers):
        """Display a summary of trigger operations."""
        if not (successful_triggers or failed_triggers):
            return
        
        summary_message = ""
        if successful_triggers:
            summary_message += f"✅ Triggered: {', '.join(successful_triggers)}\n"
        if failed_triggers:
            summary_message += f"❌ Failed: {', '.join(failed_triggers)}"

    def _find_camera_by_partial_name(self, name):
        """Find a camera that contains the given name."""
        name_lower = name.lower()
        for i in range(self.ui.listWidget.count()):
            camera_name = self.ui.listWidget.item(i).text()
            if name_lower in camera_name.lower():
                return camera_name
        return None


    def trigger_tcp(self, byte_array):
        """
        Trigger cameras using a 5-byte array over TCP.
        Each bit in the 5-byte array represents a camera (40 cameras total).
        
        Args:
            byte_array (bytes or list): A 5-byte array where each bit controls a camera.
        """
        # Validate byte array input
        if not isinstance(byte_array, (bytes, list)) or len(byte_array) != 5:
            self.log_message("❌ Invalid byte array. Expected 5 bytes for 40 cameras.")
            return
        
        # Convert list to bytes if necessary
        if isinstance(byte_array, list):
            try:
                byte_array = bytes(byte_array)
            except ValueError:
                self.log_message("❌ Invalid byte values in array. Must be 0-255.")
                return
        
        # Track trigger results for summary
        successful_triggers = []
        failed_triggers = []
        
        try:
            # Process each camera based on the byte array
            for camera_idx in range(40):  # 0 to 39 cameras
                byte_idx = camera_idx // 8  # Which byte (0-4)
                bit_idx = camera_idx % 8   # Which bit in that byte (0-7)
                
                # Check if the bit for this camera is set
                if byte_array[byte_idx] & (1 << bit_idx):
                    # Find the camera by index (assuming listWidget has camera names in order)
                    if camera_idx < self.ui.listWidget.count():
                        camera_name = self.ui.listWidget.item(camera_idx).text()
                        
                        # Attempt to trigger the camera
                        try:
                            result = self._trigger_and_handle_camera(camera_name, "capture")
                            if result:
                                successful_triggers.append(camera_name)
                            else:
                                failed_triggers.append(camera_name)
                        except Exception as e:
                            self.log_message(f"❌ Error triggering {camera_name}: {str(e)}")
                            failed_triggers.append(camera_name)
                    else:
                        self.log_message(f"❌ Camera index {camera_idx} not found in list")
                        failed_triggers.append(f"Camera_{camera_idx}")
        
            # Provide summary notification
            self._show_trigger_summary(successful_triggers, failed_triggers)
        
        except Exception as e:
            self.log_message(f"❌ Unexpected error during TCP trigger: {str(e)}")

    def trigger(self):
        byte_array = bytes([0x01, 0x00, 0x00, 0x00, 0x00])
        self.trigger_tcp(byte_array)
        