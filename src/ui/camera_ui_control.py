from PySide6.QtWidgets import QWidget, QListWidgetItem, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import QThread
from ui.camera_design import Ui_Form
from ui.camera_dialog import CameraDialog
from camera.cam_handler import CameraThread
from camera.check_ping import PingThread
from camera.camera_configuration_manager import CameraConfigManager
from datetime import datetime
import os


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
        self.ui.run_once.clicked.connect(self.run_ai_once)
        self.ui.run_continuous.clicked.connect(self.run_ai_continuous)
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
        self.ui.display.setText("Hide")
        self.log_message(f"🖥️ Now displaying {camera_name}")
    
    def _clear_display(self):
        """Helper method to clear the display and reset display state."""
        self.ui.label.clear()
        self.current_camera = None
        self.displaying = False
        self.ui.display.setText("Display")
    
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
            camera_name = f"Camera {self.ui.listWidget.count() + 1}"
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
        
        # Search for camera with this IP in our properties
        for i in range(self.ui.listWidget.count()):
            item = self.ui.listWidget.item(i)
            camera_name = item.text()
            props = self.camera_properties.get(camera_name)
            
            if props and props["ip_address"] == camera_ip:
                found_camera = camera_name
                found_item = item
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
            # Update to offline icon
            found_item.setIcon(QIcon(self.icon_offline))
            
            # Save to config
            self.config_manager.add_camera(self.camera_properties[found_camera])
            self.log_message(f"❌ Camera {found_camera} at {camera_ip} is unreachable!")
            
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
            "online": self.icon_online,
            "offline": self.icon_offline,
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
   
    def run_ai_once(self):
        """Process the binary command from the lineEdit to trigger specific cameras."""
        # Get the command from lineEdit as a hex string
        command_hex = self.ui.lineEdit.text().strip()
        
        if not command_hex:
            self.log_message("⚠️ Please enter a camera command in the text field")
            return
            
        # Try to convert hex string to bytes
        try:
            # Remove spaces, 0x prefixes, etc. and convert to bytes
            clean_hex = command_hex.replace(" ", "").replace("0x", "")
            if len(clean_hex) % 2 != 0:
                self.log_message("⚠️ Invalid hex string: odd number of characters")
                return
                
            command_bytes = bytes.fromhex(clean_hex)
            self.log_message(f"🤖 Processing binary command: {command_bytes.hex(' ').upper()}")
        except ValueError:
            self.log_message("⚠️ Invalid hex format. Use format like: AA 55 01 02 01 02 XX XX")
            return
        
        # Check minimum length (header + command type + camera count + at least one camera + action + checksum)
        if len(command_bytes) < 7:
            self.log_message("⚠️ Command too short. Minimum length is 7 bytes.")
            return
        
        # Validate header (0xAA 0x55)
        if command_bytes[0] != 0xAA or command_bytes[1] != 0x55:
            self.log_message("⚠️ Invalid header. Expected: AA 55")
            return
        
        # Validate command type (0x01 for trigger)
        if command_bytes[2] != 0x01:
            self.log_message(f"⚠️ Unknown command type: {command_bytes[2]:02X}")
            return
        
        # Get camera count
        camera_count = command_bytes[3]
        if camera_count == 0:
            self.log_message("⚠️ No cameras specified")
            return
        
        # Check if the packet is long enough based on camera_count
        expected_length = 6 + camera_count  # Header(2) + CmdType(1) + CamCount(1) + CamIndexes(n) + Action(1) + Checksum(2)
        if len(command_bytes) != expected_length:
            self.log_message(f"⚠️ Invalid packet length. Expected {expected_length} bytes for {camera_count} cameras.")
            return
        
        # Validate checksum
        calculated_checksum = 0
        for i in range(len(command_bytes) - 2):
            calculated_checksum ^= command_bytes[i]
        
        received_checksum = (command_bytes[-2] << 8) | command_bytes[-1]
        if calculated_checksum != received_checksum:
            self.log_message(f"⚠️ Checksum error. Calculated: {calculated_checksum:04X}, Received: {received_checksum:04X}")
            return
        
        # Get action code
        action_code = command_bytes[4 + camera_count]
        action = self._get_action_from_code(action_code)
        if not action:
            self.log_message(f"⚠️ Unknown action code: {action_code:02X}")
            return
        
        # Process each camera
        for i in range(camera_count):
            camera_index = command_bytes[4 + i]
            # Convert 0-based index to 1-based for user display
            display_index = camera_index + 1
            
            # Get camera name from index
            target_camera = self._get_camera_by_index(camera_index)
            if target_camera:
                self._trigger_camera(target_camera, action)
            else:
                self.log_message(f"❌ Camera with index {display_index} not found")

    def _get_action_from_code(self, action_code):
        """Convert action code to action string."""
        action_map = {
            0x01: "capture",
            0x02: "stop"
        }
        return action_map.get(action_code)

    def _get_camera_by_index(self, index):
        """Get camera name by its index (0-based)."""
        if 0 <= index < self.ui.listWidget.count():
            return self.ui.listWidget.item(index).text()
        return None

    def _calculate_checksum(self, data):
        """Calculate XOR checksum for the given data."""
        checksum = 0
        for byte in data:
            checksum ^= byte
        return checksum

    def create_binary_command(self, camera_indexes, action_code):
        """Create a binary command for the given camera indexes and action code.
        
        Args:
            camera_indexes (list): List of camera indexes (0-based)
            action_code (int): Action code (0x01 for capture, 0x02 for stop)
            
        Returns:
            bytes: The binary command
        """
        # Create the command up to before the checksum
        command = bytearray([
            0xAA, 0x55,             # Header
            0x01,                   # Command Type (Trigger)
            len(camera_indexes)     # Camera Count
        ])
        
        # Add camera indexes
        command.extend(camera_indexes)
        
        # Add action code
        command.append(action_code)
        
        # Calculate checksum
        checksum = self._calculate_checksum(command)
        
        # Add checksum (2 bytes, big endian)
        command.append((checksum >> 8) & 0xFF)  # High byte
        command.append(checksum & 0xFF)         # Low byte
        
        return bytes(command)

    def format_command_for_display(self, command_bytes):
        """Format a binary command for display."""
        return ' '.join([f"{b:02X}" for b in command_bytes])

    # Helper function to show example of creating a command
    def show_command_example(self):
        """Show an example of creating a binary command."""
        # Example: trigger cameras 0 and 2 with capture action
        camera_indexes = [0, 2]
        action_code = 0x01  # Capture
        
        command = self.create_binary_command(camera_indexes, action_code)
        formatted = self.format_command_for_display(command)
        
        self.log_message(f"📝 Example command: {formatted}")
        self.log_message(f"ℹ️ This triggers cameras 1 and 3 to capture")
        
        # Set the example in the line edit
        self.ui.lineEdit.setText(formatted)

    def run_ai_continuous(self):
        """Run AI in continuous mode. Currently a placeholder."""
        self.log_message("♻️ Running AI continuously...")
        # Implementation for continuous mode would go here

    

    