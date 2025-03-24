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
            ip_address = '192.168.28.1'  # Use the requested IP
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
        """
        Process the received JSON command
        
        Args:
            json_data: The JSON data received from the client
            
        Returns:
            dict: Response to send back to the client
        """
        # Check if we have a command type
        if isinstance(json_data, list):
            # This is a trigger configuration
            if self.camera_widget:
                # Emit signal to process the command in the main thread
                self.signal_relay.command_signal.emit({"command": "trigger", "data": json_data})
                return {"status": "success", "message": "Trigger command received"}
            else:
                return {"status": "error", "message": "Camera widget not available"}
        
        # For other command types, you can add more handlers here
        command = json_data.get("command")
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
        return {"status": "error", "message": "Unknown command"}
    
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
        """
        Process commands from the signal (runs in the main thread)
        
        Args:
            command_data (dict): The command data to process
        """
        command_type = command_data.get("command")
        
        if command_type == "trigger":
            # This is a trigger command
            trigger_configs = command_data.get("data", [])
            self.log_message(f"Processing trigger command for {len(trigger_configs)} cameras")
            
            # Process the trigger configs directly
            if self.camera_widget:
                triggered_cameras, failed_cameras, skipped_cameras = self.camera_widget._process_trigger_configs(
                    trigger_configs  # Each config has its own trigger_type
                )
                
                # Log the summary
                self.log_message("\n=== Trigger Summary ===")
                self.log_message(f"✅ Successfully triggered: {len(triggered_cameras)}/{len(trigger_configs)} cameras")
                
                if triggered_cameras:
                    self.log_message(f"📸 Triggered cameras: {', '.join(triggered_cameras)}")
                
                if failed_cameras:
                    self.log_message(f"❌ Failed cameras: {', '.join(failed_cameras)}")
                    
                if skipped_cameras:
                    self.log_message(f"⏩ Skipped cameras: {', '.join(skipped_cameras)}")
        
        # Add handlers for other command types as needed

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