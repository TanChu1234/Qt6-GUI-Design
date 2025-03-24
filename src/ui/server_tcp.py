import json
import socket
import threading
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal, QObject
from ui.tcp_ui import Ui_Form

class SignalRelay(QObject):
    """
    Custom signal relay to safely update UI from another thread
    """
    log_signal = Signal(str)
    command_signal = Signal(dict)  # New signal for handling commands

class TCPServerApp(QWidget):
    def __init__(self, camera_widget=None):
        super().__init__()
        
        # Setup UI
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        # Store reference to camera widget
        self.camera_widget = camera_widget
        
        # Setup signal relay
        self.signal_relay = SignalRelay()
        self.signal_relay.log_signal.connect(self.update_log)
        self.signal_relay.command_signal.connect(self.process_command)
        
        # Socket server attributes
        self.server_socket = None
        self.server_thread = None
        self.is_server_running = False
        
        # Connect buttons
        self.ui.start_socket.clicked.connect(self.start_server)
        self.ui.stop_socket.clicked.connect(self.stop_server)
        
        # Disable stop button initially
        self.ui.stop_socket.setEnabled(False)

    def update_log(self, message):
        """
        Update the log list widget with a new message
        """
        if self.ui.listWidget:
            self.ui.listWidget.addItem(message)
            # Scroll to the bottom
            self.ui.listWidget.scrollToBottom()
            
    def log_message(self, message):
        """
        Add message to the log list widget using signal relay
        """
        self.signal_relay.log_signal.emit(message)
    
    def start_server(self):
        """
        Start the TCP socket server in a separate thread
        """
        if self.is_server_running:
            return
        
        try:
            # Get IP from text field or use default
            ip_address = '192.168.1.26'  # Use the requested IP
            port = 502  # You can change port or make it configurable
            
            # Create server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((ip_address, port))
            self.server_socket.listen(5)
            
            # Update UI
            self.ui.start_socket.setEnabled(False)
            self.ui.stop_socket.setEnabled(True)
            
            # Clear previous logs
            self.ui.listWidget.clear()
            
            # Start server in a separate thread
            self.is_server_running = True
            self.server_thread = threading.Thread(target=self.run_server, daemon=True)
            self.server_thread.start()
            
            # Log server start
            self.log_message(f"Server started on {ip_address}:{port}")
        
        except Exception as e:
            self.log_message(f"Error starting server: {e}")
            self.stop_server()

    def run_server(self):
        """
        Main server loop to accept and process connections
        """
        while self.is_server_running:
            try:
                # Wait for a connection with a timeout
                self.server_socket.settimeout(1.0)
                client_socket, address = self.server_socket.accept()
                
                # Log connection
                self.log_message(f"Connection from {address}")
                
                # Receive data
                data = client_socket.recv(1024).decode('utf-8')
                
                try:
                    # Try to parse JSON
                    json_data = json.loads(data)
                    self.log_message(f"Received JSON: {json_data}")
                    # print(json_data["type"])
                    # Process the command
                    response = self.handle_command(json_data)
                    
                    # Send the response
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    
                except json.JSONDecodeError:
                    self.log_message(f"Invalid JSON received: {data}")
                    
                    # Send error response
                    error_response = {"status": "error", "message": "Invalid JSON format"}
                    client_socket.send(json.dumps(error_response).encode('utf-8'))
                
                # Close client connection
                client_socket.close()
            
            except socket.timeout:
                # This is expected, allows checking is_server_running
                continue
            except Exception as e:
                if self.is_server_running:
                    self.log_message(f"Server error: {e}")
                break

    def handle_command(self, json_data):
        # Add debug logging
        self.log_message(f"DEBUG: Received JSON data type: {type(json_data)}")
        self.log_message(f"DEBUG: JSON data content: {json_data}")
        
        # Handle dictionary with camera commands (keys are camera names)
        if isinstance(json_data, dict) and any(isinstance(value, dict) and "type" in value for value in json_data.values()):
            self.log_message("DEBUG: Direct camera command dictionary detected")
            self.signal_relay.command_signal.emit({"command": "trigger", "data": json_data})
            return {"status": "success", "message": "Camera trigger commands received"}
        
        # Handle list format (original format with list containing dictionary)
        elif isinstance(json_data, list):
            # Check if it's our expected list with dictionary inside
            if len(json_data) > 0 and isinstance(json_data[0], dict):
                camera_dict = json_data[0]
                # Check if this is a camera command dictionary
                if any(isinstance(value, dict) and "type" in value for value in camera_dict.values()):
                    self.log_message("DEBUG: List-wrapped camera command dictionary detected")
                    self.signal_relay.command_signal.emit({"command": "trigger", "data": camera_dict})
                    return {"status": "success", "message": "Trigger command received"}
        
        # For other command types, you can add more handlers here
        command = json_data.get("command") if isinstance(json_data, dict) else None
        if command == "status":
            # Return the status of all cameras
            if self.camera_widget:
                return {
                    "status": "success", 
                    "cameras": self.get_camera_status()
                }
            else:
                return {"status": "error", "message": "Camera widget not available"}
        
        # Unknown command
        return {"status": "error", "message": "Unknown command format"}
    
    def get_camera_status(self):
        """
        Get the status of all cameras for status response
        
        Returns:
            dict: Status information for all cameras
        """
        if not self.camera_widget:
            return {}
            
        status = {}
        for camera_name, thread in self.camera_widget.camera_threads.items():
            status[camera_name] = {
                "connected": thread.isRunning(),
                "ip": self.camera_widget.camera_properties.get(camera_name, {}).get("ip_address", "")
            }
        
        return status
    
    def process_command(self, command_data):
        command_type = command_data.get("command")
        
        if command_type == "trigger":
            # Get the data (which could be a dict)
            trigger_data = command_data.get("data", {})
            self.log_message(f"DEBUG: Processing trigger data: {trigger_data}")
            
            # Process the trigger commands
            if self.camera_widget:
                triggered_cameras, failed_cameras, skipped_cameras = self.camera_widget._process_trigger_configs(
                    trigger_data
                )
                
                # Log the summary
                self.log_message("\n=== Trigger Summary ===")
                
                # Use appropriate length calculation based on data type
                if isinstance(trigger_data, dict):
                    total_cameras = len(trigger_data)
                elif isinstance(trigger_data, list):
                    total_cameras = len(trigger_data)
                else:
                    total_cameras = 0
                    
                self.log_message(f"✅ Successfully triggered: {len(triggered_cameras)}/{total_cameras} cameras")
                
                if triggered_cameras:
                    self.log_message(f"📸 Triggered cameras: {', '.join(triggered_cameras)}")
                
                if failed_cameras:
                    self.log_message(f"❌ Failed cameras: {', '.join(failed_cameras)}")
                    
                if skipped_cameras:
                    self.log_message(f"⏩ Skipped cameras: {', '.join(skipped_cameras)}")
                    
    def stop_server(self):
        """
        Stop the server and clean up resources
        """
        self.is_server_running = False
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
            
            self.server_socket = None
        
        # Reset UI
        self.ui.start_socket.setEnabled(True)
        self.ui.stop_socket.setEnabled(False)
        
        self.log_message("Server stopped")

    def closeEvent(self, event):
        """
        Ensure server is stopped when app closes
        """
        self.stop_server()
        event.accept()