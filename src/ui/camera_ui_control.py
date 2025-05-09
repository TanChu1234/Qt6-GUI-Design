from PySide6.QtWidgets import QWidget, QListWidgetItem, QMessageBox, QFileDialog
from PySide6.QtGui import QIcon
from ui.camera_design import Ui_Form
from ui.camera_dialog import CameraDialog
from camera.cam_handler import CameraThread
from camera.check_ping import PingThread
from camera.camera_configuration_manager import CameraConfigManager
from datetime import datetime
import os
import time
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
        # Connect UI buttons
        self.ui.add_cam.clicked.connect(self.add_camera)
        self.ui.connect.clicked.connect(self.start_camera)
        self.ui.disconnect.clicked.connect(self.stop_camera)
        self.ui.display.clicked.connect(self.toggle_display)
        self.ui.trigger_http.clicked.connect(self.trigger_http)
        self.ui.detect.clicked.connect(self.run_ai_model)
        self.ui.listWidget.itemClicked.connect(self.select_camera)
        self.ui.remove_cam.clicked.connect(self.remove_camera)
    
    def load_saved_cameras(self):
        """Load saved camera configurations from file"""
        cameras = self.config_manager.load_config()
        print(f"📋 Loaded {len(cameras)} saved cameras")
        
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
            
        # Add print statement
        print(log_entry)

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
            print(log_entry)
            # Don't log password for security reasons
        else:
            print(f"⚠️ No properties found for {camera_name}")
    
    def toggle_display(self):
        """Toggle display of the currently selected camera."""
        # Check if we currently have a displayed camera
        if self.displaying:
            # Stop displaying but keep threads running
            self._clear_display()
            print("🔍 Display turned off")
            return
            
        # Start displaying a camera
        item = self.ui.listWidget.currentItem()
        if not item:
            print("⚠️ No camera selected to display!")
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
        print(f"🖥️ Now displaying {camera_name}")
    
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

        print(f"🔍 Checking connection to {ip_address}...")

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
            print(f"⚠️ Could not find camera with IP {camera_ip} in the list!")
            return
            
        if is_reachable:
            # Update to offline icon initially (will update when connected)
            found_item.setIcon(QIcon(self.icon_offline))
            
            # Save to config
            self.config_manager.add_camera(self.camera_properties[found_camera])
            print(f"✅ Camera {found_camera} is reachable at {camera_ip}")
        else:
            # Remove the camera from the list since it's unreachable
            self.ui.listWidget.takeItem(found_index)
            
            # Remove from properties dictionary
            if found_camera in self.camera_properties:
                del self.camera_properties[found_camera]
                
            print(f"❌ Camera {found_camera} at {camera_ip} is unreachable! Camera removed.")
            
        # Clean up the ping thread
        for i, thread in enumerate(self.ping_threads):
            if not thread.isRunning():
                self.ping_threads.pop(i)
    
    def remove_camera(self):
        """Remove the selected camera from the list and configuration."""
        item = self.ui.listWidget.currentItem()
        if not item:
            print("⚠️ No camera selected to remove!")
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
            print(f"🗑️ Removed camera '{camera_name}'")
        else:
            print(f"⚠️ Failed to remove camera '{camera_name}' from configuration")
        
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
    
    def _handle_camera_stopped(self, camera_name):
        """Handle when a camera thread stops by itself (due to disconnection)"""
        if camera_name not in self.camera_threads:
            return
            
        # Ensure thread is fully finished
        try:
            if self.camera_threads[camera_name].isRunning():
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
                
        print(f"🛑 Camera {camera_name} stopped due to disconnection")
        
        # The key improvement: Don't affect other cameras - just handle this one
    
    def closeEvent(self, event):
        """Ensure all camera threads stop when closing the window."""
        # Create a copy of the keys to avoid modification during iteration
        camera_names = list(self.camera_threads.keys())
        for camera_name in camera_names:
            self.stop_camera(camera_name)
        
        # Save configuration on close
        self.config_manager.save_config()
        
        # Also clean up ping threads
        for thread in self.ping_threads:
            if thread.isRunning():
                try: 
                    thread.terminate()
                    thread.wait(500)
                except Exception as e:
                    print(f"⚠️ Error terminating ping thread: {str(e)}")
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
                print("⚠️ No camera selected!")
                return
            camera_name = item.text()

        camera_props = self.camera_properties.get(camera_name, None)

        if not camera_props:
            print(f"❌ No properties found for {camera_name}")
            return

        # If thread already exists and is running, just log that
        if camera_name in self.camera_threads and self.camera_threads[camera_name].isRunning():
            print(f"ℹ️ {camera_name} is already streaming")
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
        print(f"✅ Started streaming {camera_name}")

    def _handle_new_frame(self, pixmap, camera_name):
        """Handle incoming frames from camera threads."""
        # Only update the display if this is the current camera AND display is enabled
        if self.displaying and camera_name == self.current_camera:
            self.ui.label.setPixmap(pixmap)
        
    # Stop Camera        
    def stop_camera(self, specific_camera=None):
        """Stop streaming for the selected or specified camera with proper isolation."""
        # If a specific camera was provided, use it, otherwise get from selection
        camera_name = specific_camera
        if not camera_name:
            item = self.ui.listWidget.currentItem()
            if not item:
                print("⚠️ No camera selected!")
                return False
            camera_name = item.text()

        # Check if camera thread exists
        if camera_name not in self.camera_threads:
            print(f"ℹ️ No active stream for {camera_name}")
            return False
            
        # Get the thread reference
        thread = self.camera_threads[camera_name]
        
        # Make a copy of the thread reference before removal
        # to prevent affecting dictionary during operations
        thread_ref = thread
        
        try:
            print(f"🛑 Stopping {camera_name}...")
            
            # Disconnect all signals from this thread first to prevent conflicts
            # Use try/except since some signals may not be connected
            try:
                thread_ref.frame_signal.disconnect()
                thread_ref.log_signal.disconnect()
                thread_ref.connection_status_signal.disconnect()
                thread_ref.trigger_completed_signal.disconnect()
                thread_ref.finished.disconnect()
            except TypeError:
                # It's okay if some signals were not connected
                pass
                
            # Now stop the thread's operation
            thread_ref.stop()
            
            # Update icon to offline before waiting (for UI responsiveness)
            self._update_camera_icon(camera_name, "disconnected")
            
            # Clear the display if this was the current camera being displayed
            if self.displaying and self.current_camera == camera_name:
                self._clear_display()
                
            # Remove the thread from our dictionary BEFORE waiting
            # This ensures other code won't try to use this thread anymore
            del self.camera_threads[camera_name]
            
            # Wait for the thread to finish, with a reasonable timeout
            if thread_ref.isRunning():
                print(f"⏱️ Waiting for {camera_name} thread to finish...")
                success = thread_ref.wait(2000)  # Wait up to 2 seconds
                if not success:
                    print(f"⚠️ Thread for {camera_name} didn't stop properly, forcing termination")
                    thread_ref.terminate()  # Force termination as a last resort
                    thread_ref.wait(500)   # Give it a moment to clean up
            
            print(f"✅ Successfully stopped {camera_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error stopping {camera_name}: {str(e)}")
            # Still try to remove from dictionary if there was an error
            if camera_name in self.camera_threads:
                del self.camera_threads[camera_name]
            return False
   
   
    def _handle_camera_stopped(self, camera_name):
        """Handle when a camera thread stops by itself (due to disconnection or error)"""
        if camera_name not in self.camera_threads:
            return
            
        # Store a reference to the thread
        thread = self.camera_threads[camera_name]
        
        # Remove the thread reference FIRST to prevent other code from using it
        del self.camera_threads[camera_name]
        
        # Update the icon
        self._update_camera_icon(camera_name, "disconnected")
        
        # Clear the display if this was the current camera being displayed
        if self.displaying and self.current_camera == camera_name:
            self._clear_display()
                
        # Ensure thread is fully finished without blocking the UI
        try:
            if thread.isRunning():
                # Use a short timeout to avoid blocking UI
                thread.wait(500)  
                
                # If it's still running after timeout, we'll terminate it
                if thread.isRunning():
                    print(f"⚠️ Force terminating {camera_name} thread")
                    thread.terminate()
        except RuntimeError as e:
            print(f"⚠️ Runtime error cleaning up {camera_name} thread: {str(e)}")
        except Exception as e:
            print(f"⚠️ Error cleaning up {camera_name} thread: {str(e)}")
            
        print(f"🛑 Camera {camera_name} stopped")
    
    def _handle_trigger_result(self, result, camera_name):
        """
        Handle the result of a camera trigger.
        
        Args:
            result (str): Result of the trigger operation
            camera_name (str): Name of the camera that was triggered
        """
        if result == "error":
            print(f"❌ Trigger failed for {camera_name}")
        else:
            # Successful trigger, log the result (usually the filename)
            print(f"✅ Trigger successful for {camera_name}: {result}")
        
        # Store the result in trigger_results dictionary
        self.trigger_results[camera_name] = result

    def trigger_http(self):
        """Trigger cameras independently based on JSON configuration with improved isolation."""
        json_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Camera Trigger JSON", 
            "", 
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not json_path or not os.path.exists(json_path):
            print(f"❌ Trigger JSON file not found or canceled")
            return
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                trigger_configs = json.load(f)
            
            triggered_cameras = []
            failed_cameras = []
            skipped_cameras = []
            
            # Process each camera completely independently
            for config in trigger_configs:
                camera_name = config.get("camera_name")
                trigger_type = config.get("type", "capture")
                
                if not camera_name:
                    print("⚠️ Skipping entry: No camera_name specified in config")
                    continue
                
                # Check if camera is in running threads
                if camera_name not in self.camera_threads:
                    print(f"⚠️ Camera {camera_name} not connected")
                    skipped_cameras.append(camera_name)
                    continue
                
                try:
                    # Get the thread for this camera
                    thread = self.camera_threads[camera_name]
                    
                    # Verify thread is running
                    if not thread.isRunning():
                        print(f"⚠️ Camera {camera_name} thread not running")
                        skipped_cameras.append(camera_name)
                        continue
                    
                    # Attempt to trigger
                    result = thread.trigger(trigger_type)
                    
                    if result:
                        triggered_cameras.append(camera_name)
                        print(f"✅ Triggered {camera_name}")
                    else:
                        failed_cameras.append(camera_name)
                        print(f"❌ Failed to trigger {camera_name}")
                    
                except Exception as e:
                    print(f"❌ Error triggering {camera_name}: {str(e)}")
                    failed_cameras.append(camera_name)
            
            # Final summary
            print("\n=== Trigger HTTP Summary ===")
            print(f"✅ Successfully triggered: {len(triggered_cameras)}/{len(trigger_configs)} cameras")
            
            if triggered_cameras:
                print(f"📸 Triggered cameras: {', '.join(triggered_cameras)}")
            
            if failed_cameras: 
                print(f"❌ Failed cameras: {', '.join(failed_cameras)}")
                
            if skipped_cameras:
                print(f"⏩ Skipped cameras: {', '.join(skipped_cameras)}")
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON file: {str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error in trigger_http: {str(e)}")
            
    def run_ai_model(self):    
        """Trigger cameras independently based on JSON configuration with improved isolation."""
        json_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Camera Trigger JSON", 
            "", 
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not json_path or not os.path.exists(json_path):
            print(f"❌ Trigger JSON file not found or canceled")
            return
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                trigger_configs = json.load(f)
            
            triggered_cameras = []
            failed_cameras = []
            skipped_cameras = []
            
            # Process each camera completely independently
            for config in trigger_configs:
                camera_name = config.get("camera_name")  
                    
                if not camera_name:
                    print("⚠️ Skipping entry: No camera_name specified in config")
                    continue
                
                # Check if camera is in running threads
                if camera_name not in self.camera_threads:
                    print(f"⚠️ Camera {camera_name} not connected")
                    skipped_cameras.append(camera_name)
                    continue
                
                try:
                    # Get the thread for this camera
                    thread = self.camera_threads[camera_name]
                    
                    # Verify thread is running
                    if not thread.isRunning():
                        print(f"⚠️ Camera {camera_name} thread not running")
                        skipped_cameras.append(camera_name)
                        continue
                    
                    # Attempt to trigger
                    result = thread.trigger_and_process()
                    
                    if result:
                        triggered_cameras.append(camera_name)
                        print(f"✅ Triggered {camera_name}")
                    else:
                        failed_cameras.append(camera_name)
                        print(f"❌ Failed to trigger {camera_name}")
                    
                except Exception as e:
                    print(f"❌ Error triggering {camera_name}: {str(e)}")
                    failed_cameras.append(camera_name)
            
            # Final summary
            print("\n=== Trigger HTTP Summary ===")
            print(f"✅ Successfully triggered: {len(triggered_cameras)}/{len(trigger_configs)} cameras")
            
            if triggered_cameras:
                print(f"📸 Triggered cameras: {', '.join(triggered_cameras)}")
            
            if failed_cameras: 
                print(f"❌ Failed cameras: {', '.join(failed_cameras)}")
                
            if skipped_cameras:
                print(f"⏩ Skipped cameras: {', '.join(skipped_cameras)}")
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON file: {str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error in detect: {str(e)}")