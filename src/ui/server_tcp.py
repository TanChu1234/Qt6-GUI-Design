import json
import asyncio
import socket
import threading
import queue
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal, QObject, QTimer
from ui.tcp_ui import Ui_Form

class SignalRelay(QObject):
    """
    Custom signal relay to safely update UI from another thread
    """
    log_signal = Signal(str)
    command_signal = Signal(dict)  # Signal for handling commands
    check_cart = Signal(bool)
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
        self.server = None
        self.server_thread = None
        self.is_server_running = False
        self.event_loop = None
        
        # Command queue to ensure all commands are processed
        self.command_queue = queue.Queue()
        
        # Create a timer to process command queue items
        self.command_timer = QTimer(self)
        self.command_timer.timeout.connect(self.process_command_queue)
        self.command_timer.start(100)  # Check queue every 100ms
        
        # Command processing flag to avoid overlaps
        self.is_processing_command = False
        
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
        Start the async TCP socket server in a separate thread
        """
        if self.is_server_running:
            return
        
        try:
            # Get IP from text field or use default
            ip_address = '192.168.1.26'  # Use the requested IP
            port = 502  # You can change port or make it configurable
            
            # Update UI
            self.ui.start_socket.setEnabled(False)
            self.ui.stop_socket.setEnabled(True)
            
            # Clear previous logs
            self.ui.listWidget.clear()
            
            # Start server in a separate thread with asyncio
            self.is_server_running = True
            self.server_thread = threading.Thread(target=self.run_async_server, 
                                                 args=(ip_address, port), 
                                                 daemon=True)
            self.server_thread.start()
            
            # Log server start
            self.log_message(f"Async server starting on {ip_address}:{port}")
        
        except Exception as e:
            self.log_message(f"Error starting server: {e}")
            self.stop_server()

    def run_async_server(self, host, port):
        """
        Run the asyncio event loop in a separate thread
        """
        try:
            # Create a new event loop for this thread
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)
            
            # Create and run the server
            server_coro = asyncio.start_server(
                self.handle_client, host, port, backlog=10)
            
            self.server = self.event_loop.run_until_complete(server_coro)
            
            # Signal that server is now running
            self.log_message(f"Async server is now running on {host}:{port}")
            
            # Run the event loop
            self.event_loop.run_forever()
            
        except Exception as e:
            self.log_message(f"Error in async server: {e}")
        finally:
            if self.event_loop and not self.event_loop.is_closed():
                self.event_loop.close()
            self.log_message("Async server event loop stopped")
    
    async def handle_client(self, reader, writer):
        """
        Handle an individual client connection asynchronously
        
        Args:
            reader: StreamReader for reading client data
            writer: StreamWriter for writing responses
        """
        # Get client info
        client_addr = writer.get_extra_info('peername')
        client_id = f"{client_addr[0]}:{client_addr[1]}"
        self.log_message(f"Connection from {client_id}")
        
        try:
            # Read data (up to 4KB)
            data = await reader.read(4096)
            message = data.decode('utf-8')
            
            if not message:
                self.log_message(f"Empty message from {client_id}")
                return
            
            try:
                # Parse JSON data
                json_data = json.loads(message)
                self.log_message(f"Received JSON from {client_id}: {type(json_data).__name__}")
                
                # Process the command and get response
                response = await self.async_handle_command(json_data, client_id)
                
                # Send response
                writer.write(json.dumps(response).encode('utf-8'))
                await writer.drain()
                
            except json.JSONDecodeError:
                # Handle invalid JSON
                self.log_message(f"Invalid JSON from {client_id}: {message}")
                error_response = {"status": "error", "message": "Invalid JSON format"}
                writer.write(json.dumps(error_response).encode('utf-8'))
                await writer.drain()
                
        except Exception as e:
            self.log_message(f"Error handling client {client_id}: {e}")
        finally:
            # Close the connection
            writer.close()
            try:
                await writer.wait_closed()
            except:
                pass  # Ignore errors on close
    
    async def async_handle_command(self, json_data, client_id):
        """
        Process the received JSON command asynchronously
        
        Args:
            json_data: The JSON data received from the client
            client_id: Client identifier for tracing requests
            
        Returns:
            dict: Response to send back to the client
        """
        # Handle dictionary with camera commands (keys are camera names)
        if isinstance(json_data, dict) and any(isinstance(value, dict) and "type" in value for value in json_data.values()):
            self.log_message(f"Direct camera command dictionary detected from {client_id}")
            
            # Add command to the queue with a unique ID
            command_id = f"cmd_{client_id}_{hash(str(json_data))}"
            
            # Create a future that will be resolved when the command completes
            future = asyncio.Future()
            
            # Add to the queue: command data and the future to resolve
            self.command_queue.put((command_id, json_data, future))
            
            # Wait for the command to be processed
            try:
                # Wait with a timeout to avoid blocking the server
                result = await asyncio.wait_for(future, timeout=10)
                
                # Return a more detailed response that includes person counts
                return {
                    "status": "success", 
                    "message": f"Camera trigger completed for {client_id}",
                    "data": result  # This will contain triggered_cameras, person_counts, etc.
                }
            except asyncio.TimeoutError:
                return {"status": "success", "message": "Command queued but processing timed out"}

    
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
    
    def process_command_queue(self):
        """
        Process commands from the queue at regular intervals (called by QTimer)
        """
        if self.is_processing_command or self.command_queue.empty():
            return
            
        try:
            self.is_processing_command = True
            
            # Get next command from queue
            command_id, command_data, future = self.command_queue.get_nowait()
            
            self.log_message(f"Processing queued command: {command_id}")
            
            # Emit signal to process the command in UI thread
            self.signal_relay.command_signal.emit({
                "command": "trigger", 
                "data": command_data,
                "id": command_id,
                "future": future
            })
            
        except queue.Empty:
            pass
        finally:
            self.is_processing_command = False
    
    def process_command(self, command_data):
        """
        Process commands from the signal (runs in the UI thread)
        
        Args:
            command_data (dict): The command data to process
        """
        command_type = command_data.get("command")
        
        try:
            if command_type == "trigger":
                # Get the data (which could be a dict)
                trigger_data = command_data.get("data", {})
                command_id = command_data.get("id", "unknown")
                future = command_data.get("future")
                
                self.log_message(f"Processing trigger data for command {command_id}")
                
                # Process the trigger commands
                if self.camera_widget:
                    triggered_cameras, failed_cameras, skipped_cameras, person_counts = self.camera_widget._process_trigger_configs(
                        trigger_data
                    )
                    
                    # Log the summary
                    self.log_message(f"\n=== Trigger Summary for {command_id} ===")
                    
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
                    
                    # Include person counts in the log for debugging
                    self.log_message(f"👤 Person counts: {person_counts}")
                    
                    # Create a result object that includes the person counts
                    result = {
                        "triggered_cameras": triggered_cameras,
                        "f_cameras": failed_cameras,
                        "skipped_cameras": skipped_cameras,ailed
                        "person_counts": person_counts
                    }
                    
                    # Resolve the future to notify the asyncio thread that processing is complete
                    if future and not future.done():
                        # This needs to be passed back to the asyncio thread
                        asyncio.run_coroutine_threadsafe(
                            self._complete_command(future, result), 
                            self.event_loop
                        )
        except Exception as e:
            self.log_message(f"Error in process_command: {e}")
    
    async def _complete_command(self, future, result):
        """
        Helper to set the future result from the asyncio thread
        """
        if not future.done():
            future.set_result(result)
    
    def stop_server(self):
        """
        Stop the server and clean up resources
        """
        self.is_server_running = False
        
        # Stop the asyncio event loop
        if self.event_loop and not self.event_loop.is_closed():
            # Schedule a call to stop the server and close the event loop
            asyncio.run_coroutine_threadsafe(self.cleanup_server(), self.event_loop)
            
            # Give it a moment to clean up
            self.server_thread.join(1.0)
        
        # Reset UI
        self.ui.start_socket.setEnabled(True)
        self.ui.stop_socket.setEnabled(False)
        
        self.log_message("Server stopped")
    
    async def cleanup_server(self):
        """
        Async cleanup of server resources
        """
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None
        
        # Stop the event loop
        self.event_loop.stop()

    def closeEvent(self, event):
        """
        Ensure server is stopped when app closes
        """
        self.stop_server()
        event.accept()