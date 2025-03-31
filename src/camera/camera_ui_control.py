import json
import os
from datetime import datetime

import cv2
import psutil
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtWidgets import (QFileDialog, QListWidgetItem, QMessageBox,
                               QWidget)

from camera.cam_handler import CameraThread
from camera.camera_configuration_manager import CameraConfigManager
from camera.check_ping import ping_camera
from model.model_yolo import YOLODetector
from ui.camera_design import Ui_Form
from ui.camera_dialog import CameraDialog


class CameraWidget(QWidget):
    """Main widget for camera management and display."""

    def __init__(self):
        """Initialize widget and set up configuration."""
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
        # Create a single YOLODetector instance to be shared by all camera threads

        self.yolo_detector = YOLODetector(model_path="src/model/bestv11.pt", rois = [(13, 148, 224, 418), 
                                                                                     (172, 132, 395, 402), 
                                                                                     (391, 98, 642, 420), 
                                                                                     (625, 107, 870, 377), 
                                                                                     (849, 137, 1088, 408), 
                                                                                     (1065, 136, 1245, 402)])
        self.cart = None
        self.load_saved_cameras()

    def _setup_ui(self):
        """Connect UI elements to their handlers."""
        # Connect UI buttons
        self.ui.add_cam.clicked.connect(self.add_camera)
        self.ui.connect.clicked.connect(self.connect_all_cameras)
        self.ui.disconnect.clicked.connect(self.stop_camera)
        self.ui.stop_all.clicked.connect(self.stop_all_cameras)  # Fixed: Added correct connection
        self.ui.display.clicked.connect(self.toggle_display)
        self.ui.trigger.clicked.connect(self.trigger_cameras)
        self.ui.detect.clicked.connect(self.detect)
        self.ui.listWidget.itemClicked.connect(self.select_camera)
        self.ui.remove_cam.clicked.connect(self.remove_camera)
        # Add double-click handler to connect to camera
        self.ui.listWidget.itemDoubleClicked.connect(self.connect_on_double_click)



    def print_memory_usage(self, tag=""):
        process = psutil.Process(os.getpid())
        print(f"🛠️ [Memory Debug] {tag}: {process.memory_info().rss / (1024 * 1024)} MB")  # in MB

    # Before connecting cameras
    print_memory_usage("Before connecting cameras")


    def load_saved_cameras(self):
        """Load saved camera configurations from file."""
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

    def count_cart(self, cart_count):
        self.cart = cart_count


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

    def connect_on_double_click(self, item):
        """Handle double-click on camera list item to connect without displaying."""
        camera_name = item.text()

        # Check if camera is already streaming
        if camera_name in self.camera_threads and self.camera_threads[camera_name].isRunning():
            print(f"ℹ️ {camera_name} is already streaming")
            self.log_message(f"Camera {camera_name} is already connected")
            return

        # Start the camera without displaying it
        print(f"🔄 Double-clicked to connect camera: {camera_name}")
        self.log_message(f"Connecting to {camera_name}...")
        self.start_camera(camera_name)

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
        if self.ui.listWidget.count() >= 50:
            QMessageBox.warning(self, "Camera Limit Reached", "Max 40 cameras allowed.", QMessageBox.Ok)
            return

        while True:
            dialog = CameraDialog()
            if not dialog.exec():
                return  # User canceled

            camera_info = dialog.get_camera_info()
            ip_address = camera_info["ip_address"]
            camera_name = camera_info["camera_name"] or f"Camera {self.ui.listWidget.count()}"

            # Check for duplicate name
            if any(self.ui.listWidget.item(i).text() == camera_name for i in range(self.ui.listWidget.count())):
                QMessageBox.warning(self, "Duplicate Name", f"Camera '{camera_name}' already exists.", QMessageBox.Ok)
                continue  # Ask for a different name

            break  # Exit loop if all checks pass

        # Check if the camera is reachable **without threading**
        if ping_camera(ip_address):
            self.ui.listWidget.addItem(QListWidgetItem(QIcon(self.icon_offline), camera_name))
            self.camera_properties[camera_name] = camera_info
            self.config_manager.add_camera(camera_info)
            print(f"✅ Camera {camera_name} is reachable at {ip_address}")
        else:
            QMessageBox.warning(self, "Camera Unreachable", f"Camera at {ip_address} is not responding.", QMessageBox.Ok)
            print(f"❌ Camera at {ip_address} is unreachable!")

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
        self._update_camera_icon(camera_name, status)

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
        event.accept()

    """ Camera Operation """
    def start_camera(self, specific_camera=None):
        """
        Start real-time streaming for a single selected or specified camera.
        This method remains mostly unchanged from your current implementation.
        """
        # If a specific camera was provided, use it, otherwise get from selection
        camera_name = specific_camera
        if not camera_name:
            item = self.ui.listWidget.currentItem()
            if not item:
                print("⚠️ No camera selected!")
                return False
            camera_name = item.text()

        camera_props = self.camera_properties.get(camera_name, None)

        if not camera_props:
            print(f"❌ No properties found for {camera_name}")
            return False

        # If thread already exists and is running, just log that
        if camera_name in self.camera_threads and self.camera_threads[camera_name].isRunning():
            print(f"ℹ️ {camera_name} is already streaming")
            return True

        # Update icon to connecting
        self._update_camera_icon(camera_name, "connecting")



        # Start new camera thread with all properties
        try:
            self.camera_threads[camera_name] = CameraThread(
                camera_props["ip_address"],
                camera_props["port"],
                camera_props["username"],
                camera_props["password"],
                camera_props["camera_name"],
                camera_props["protocol"],
                yolo_detector= self.yolo_detector
            )

            # Connect signals
            thread = self.camera_threads[camera_name]
            thread.frame_signal.connect(
                lambda pixmap, cam=camera_name: self._handle_new_frame(pixmap, cam)
            )
            thread.log_signal.connect(self.log_message)
            thread.cart_count.connect(self.count_cart)
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
            return True

        except Exception as e:
            print(f"❌ Error starting {camera_name}: {str(e)}")
            return False

    def connect_all_cameras(self):
        """Connect all cameras listed in the ListWidget by reusing start_camera"""

        # Before connecting cameras
        self.print_memory_usage("Before connecting cameras")

        # Get the total number of cameras in the list
        total_cameras = self.ui.listWidget.count()

        if total_cameras == 0:
            self.log_message("⚠️ No cameras in the list to connect")
            return

        # Connection results tracking
        connection_results = {
            'total': total_cameras,
            'successful': [],
            'failed': [],
            'skipped': []
        }

        # Log start of connection attempt
        self.log_message(f"🔌 Initiating connection for {total_cameras} cameras")

        # Iterate through all items in the ListWidget
        for i in range(total_cameras):
            item = self.ui.listWidget.item(i)

            if not item:
                # self.log_message(f"⚠️ Invalid item at index {i}")
                connection_results['skipped'].append(f"Invalid Item {i}")
                continue

            camera_name = item.text().strip()

            if not camera_name:
                # self.log_message("⚠️ Skipping empty camera name")
                connection_results['skipped'].append("Empty Name")
                continue

            # Try to start the camera using `start_camera`
            success = self.start_camera(camera_name)

            if success:
                connection_results['successful'].append(camera_name)
            else:
                connection_results['failed'].append(camera_name)

        # Log connection summary
        self.log_connection_summary(connection_results)

        self.print_memory_usage("After connecting cameras")

    def stop_all_cameras(self):
        """Stop all connected cameras using a simple direct approach without progress dialog."""
        # Find fully connected cameras
        connected_cameras = []

        # Start from index 0 to include all cameras
        for i in range(self.ui.listWidget.count()):
            item = self.ui.listWidget.item(i)
            camera_name = item.text()

            # Check if camera is in threads and running
            if (camera_name in self.camera_threads and
                self.camera_threads[camera_name].isRunning()):

                # Use the connection_status attribute directly
                if self.camera_threads[camera_name].connection_status == "connected":
                    connected_cameras.append(camera_name)
                    print(f"Adding camera {camera_name} to stop list (connected)")

        total_cameras = len(connected_cameras)

        if total_cameras == 0:
            QMessageBox.information(self, "No Cameras Connected",
                                "ℹ️ No fully connected cameras to stop.")
            return

        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Stop",
            f"⚠️ Are you sure you want to stop all {total_cameras} connected cameras?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.No:
            print("⏹️ Stop process canceled.")
            return

        # Track results
        stopped_cameras = []
        failed_cameras = []

        # Log start of operation
        self.log_message(f"🛑 Stopping all {total_cameras} connected cameras...")

        # Process each camera directly
        for camera_name in connected_cameras:
            # Stop the camera
            success = self.stop_camera(camera_name)

            if success:
                stopped_cameras.append(camera_name)
            else:
                failed_cameras.append(camera_name)

        # Show results
        if stopped_cameras and failed_cameras:
            self.log_message(f"✅ Stopped {len(stopped_cameras)} cameras, {len(failed_cameras)} failed")
        elif stopped_cameras:
            self.log_message(f"✅ Successfully stopped all {len(stopped_cameras)} cameras")
        else:
            self.log_message("❌ Failed to stop any cameras")


    def update_progress(self, progress, camera_name):
        """Update progress dialog with the current camera being stopped."""
        self.progress_dialog.setValue(progress)
        self.progress_dialog.setLabelText(f"Stopping {camera_name}...")

    def on_stop_completed(self, stopped_cameras, failed_cameras):
        """Handle the completion of camera stopping."""
        self.progress_dialog.setValue(self.progress_dialog.maximum())  # Complete progress
        self.progress_dialog.close()

        if stopped_cameras:
            QMessageBox.information(self, "Stop Completed", f"🛑 Stopped: {', '.join(stopped_cameras)}")
        if failed_cameras:
            QMessageBox.warning(self, "Stop Failed", f"⚠️ Failed to stop: {', '.join(failed_cameras)}")

        # Cleanup thread
        self.worker_thread.quit()
        self.worker_thread.wait()
        self.worker_thread = None
        self.worker = None

    def log_connection_summary(self, connection_results):
        """
        Log a detailed summary of camera connection attempts

        Args:
            connection_results (dict): Dictionary containing connection results
        """
        # Separator for readability
        self.log_message("\n=== Camera Connection Summary ===")

        # Total cameras
        self.log_message(f"📊 Total Cameras: {connection_results['total']}")

        # Successfully Connected Cameras
        if connection_results['successful']:
            self.log_message(f"✅ Successfully Connected: {len(connection_results['successful'])}")
            self.log_message(f"   Cameras: {', '.join(connection_results['successful'])}")

        # Failed Connections
        if connection_results['failed']:
            self.log_message(f"❌ Failed to Connect: {len(connection_results['failed'])}")
            self.log_message(f"   Cameras: {', '.join(connection_results['failed'])}")

        # Skipped Cameras
        if connection_results['skipped']:
            self.log_message(f"⏩ Skipped Cameras: {len(connection_results['skipped'])}")
            self.log_message(f"   Cameras: {', '.join(map(str, connection_results['skipped']))}")

    def _handle_new_frame(self, pixmap, camera_name):
        """Handle incoming frames from camera threads."""
        # Only update the display if this is the current camera AND display is enabled
        if self.displaying and camera_name == self.current_camera:
            self.ui.label.setPixmap(pixmap)

    def stop_camera(self, specific_camera=None):
        """Stop streaming for the selected or specified camera with proper isolation."""
        try:
            camera_name = self._get_camera_name(specific_camera)
            if not camera_name:
                return False

            # Check if camera exists in threads
            if camera_name not in self.camera_threads:
                print(f"ℹ️ No active stream for {camera_name}")
                return False

            # Check if camera is running and connected
            if self.camera_threads[camera_name].connection_status == "connected":
                    thread_ref = self.camera_threads[camera_name]
                    return self._stop_camera_thread(camera_name, thread_ref)
            else:
                # Thread exists but not running
                self.log_message(f"⚠️ Camera thread for {camera_name} exists but is not running")
                return False

        except Exception as e:

            self.log_message(f"Error stopping camera: {str(e)}")
            return False

    def _get_camera_name(self, specific_camera):
        """Get the camera name from the specific camera or the current selection."""
        if specific_camera:
            return specific_camera
        item = self.ui.listWidget.currentItem()
        if not item:
            print("⚠️ No camera selected!")
            return None
        return item.text()

    def _stop_camera_thread(self, camera_name, thread_ref):
        """Stop the camera thread and handle cleanup."""
        try:
            print(f"🛑 Stopping {camera_name}...")
            self._disconnect_signals(thread_ref)

            # Ensure connection status is updated
            thread_ref.connection_status = "disconnected"

            self._cleanup_gpu_memory(thread_ref)
            self._update_ui_on_stop(camera_name)
            del self.camera_threads[camera_name]
            return self._terminate_thread(camera_name, thread_ref)
        except Exception as e:
            print(f"❌ Error stopping {camera_name}: {str(e)}")
            if camera_name in self.camera_threads:
                del self.camera_threads[camera_name]
            return False

    def _disconnect_signals(self, thread_ref):
        """Disconnect signals to prevent callbacks during shutdown."""
        try:
            thread_ref.frame_signal.disconnect()
            thread_ref.log_signal.disconnect()
            thread_ref.connection_status_signal.disconnect()
            thread_ref.trigger_completed_signal.disconnect()
            thread_ref.cart_count.disconnect()
            thread_ref.finished.disconnect()
        except (TypeError, RuntimeError):
            pass

    def _cleanup_gpu_memory(self, thread_ref):
        """Force any GPU memory cleanup for YOLO."""
        if thread_ref.yolo_detector is not None:
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except (ImportError, AttributeError):
                pass

    def _update_ui_on_stop(self, camera_name):
        """Update the UI immediately for responsiveness."""
        self._update_camera_icon(camera_name, "disconnected")
        if self.displaying and self.current_camera == camera_name:
            self._clear_display()

    def _terminate_thread(self, camera_name, thread_ref):
        """Terminate the camera thread."""
        thread_ref.stop()
        if thread_ref.isRunning():
            print(f"⏱️ Waiting for {camera_name} thread to finish...")
            success = thread_ref.wait(500)
            if not success:
                print(f"⚠️ Thread for {camera_name} didn't stop properly, forcing termination")
                thread_ref.terminate()
                thread_ref.wait(100)
        print(f"✅ Successfully stopped {camera_name}")
        return True

    def _handle_camera_stopped(self, camera_name):
        """Handle when a camera thread stops by itself (due to disconnection or error)"""
        if camera_name not in self.camera_threads:
            return

        # Store a reference to the thread
        thread = self.camera_threads[camera_name]

        # Make sure the thread's connection_status is updated
        thread.connection_status = "disconnected"

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

    """ Trigger Management """
    def trigger_cameras(self):
        json_path = self._get_json_path()

        if not json_path:
            return

        try:
            trigger_configs = self._load_json_config(json_path)
            triggered_cameras, failed_cameras, skipped_cameras, _ = self._process_trigger_configs(
                trigger_configs
            )
            self._print_trigger_summary(trigger_configs, triggered_cameras, failed_cameras, skipped_cameras)

        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON file: {str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error in trigger_cameras: {str(e)}")

    def _get_json_path(self):
        """Get the JSON path from the file dialog."""
        json_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Camera Trigger JSON",
            "",
            "JSON Files (*.json);;All Files (*)"
        )

        if not json_path or not os.path.exists(json_path):
            print("❌ Trigger JSON file not found or canceled")
            return None

        return json_path

    def _load_json_config(self, json_path):
        """Load configurations from the JSON file."""
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _process_trigger_configs(self, trigger_configs):
        triggered_cameras = []
        failed_cameras = []
        skipped_cameras = []
        cart_counts = {}

        # Handle dict-style JSON config (like your example)
        if isinstance(trigger_configs, dict):
            config_items = []
            for camera_name, config in trigger_configs.items():
                # Convert each entry to the format expected by the rest of the method
                config_entry = {"camera_name": camera_name}
                # Copy all properties from the config
                config_entry.update(config)
                config_items.append(config_entry)
            trigger_configs = config_items

        # Now process each camera configuration
        for config in trigger_configs:
            camera_name = config.get("camera_name")

            if not camera_name:
                print("⚠️ Skipping entry: No camera_name specified in config")
                continue

            # Get the trigger type from config (default to "capture" if not specified)
            config_trigger_type = config.get("type", "capture")

            if camera_name not in self.camera_threads:
                print(f"⚠️ Camera {camera_name} not connected")
                skipped_cameras.append(camera_name)
                continue

            try:
                thread = self.camera_threads[camera_name]

                if not thread.isRunning():
                    print(f"⚠️ Camera {camera_name} thread not running")
                    skipped_cameras.append(camera_name)
                    continue

                # Call the trigger method with the camera-specific trigger type
                print(f"🔄 Triggering {camera_name} with type: {config_trigger_type}")
                result = thread.trigger(config_trigger_type)

                if result:
                    cart_counts[camera_name] = self.cart
                    triggered_cameras.append(camera_name)
                    print(f"✅ Triggered {camera_name}")
                else:
                    cart_counts[camera_name] = 0
                    failed_cameras.append(camera_name)
                    print(f"❌ Failed to trigger {camera_name}")

            except Exception as e:
                print(f"❌ Error triggering {camera_name}: {str(e)}")
                failed_cameras.append(camera_name)

        return triggered_cameras, failed_cameras, skipped_cameras, cart_counts

    def _print_trigger_summary(self, trigger_configs, triggered_cameras, failed_cameras, skipped_cameras):
        """Print a summary of trigger results."""
        print("\n=== Trigger Summary ===")
        # print(f"✅ Successfully triggered: {len(triggered_cameras)}/{len(trigger_configs)} cameras")

        if triggered_cameras:
            print(f"📸 Triggered cameras: {', '.join(triggered_cameras)}")

        if failed_cameras:
            print(f"❌ Failed cameras: {', '.join(failed_cameras)}")

        if skipped_cameras:
            print(f"⏩ Skipped cameras: {', '.join(skipped_cameras)}")

    def detect(self):
        """Implement real-time detection with YOLO."""
        # Get the currently selected camera
        item = self.ui.listWidget.currentItem()
        if not item:
            self.log_message("⚠️ No camera selected for detection!")
            return

        camera_name = item.text()

        # Check if camera is running
        if camera_name not in self.camera_threads or not self.camera_threads[camera_name].isRunning():
            reply = QMessageBox.question(
                self,
                "Start Camera for Detection",
                f"Camera '{camera_name}' is not streaming. Start it now?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                success = self.start_camera(camera_name)
                if not success:
                    self.log_message(f"❌ Failed to start {camera_name} for detection")
                    return
            else:
                return

        # Log that we're starting detection
        self.log_message(f"🤖 Starting real-time detection on {camera_name}")

        # Call AI trigger on the camera
        thread = self.camera_threads[camera_name]
        result = thread.trigger("ai")

        if result:
            self.log_message(f"✅ Started AI detection on {camera_name}")
            # Display the camera if not already displaying
            if not self.displaying or self.current_camera != camera_name:
                self.current_camera = camera_name
                self.displaying = True
                self.ui.display.setText("HIDE")
        else:
            self.log_message(f"❌ Failed to start AI detection on {camera_name}")

    def detect(self, save_result=True):
        """Process a single image file with the YOLO detector.

        Args:
            image_path (str): Path to the image file to process
            save_result (bool): Whether to save the annotated result image

        Returns:
            tuple: (annotated_image_path, detection_summary, cart_count, roi_status)
                or None if processing failed
        """
        # Open File Dialog to select an image
        image_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not os.path.exists(image_path):
            self.log_message(f"❌ Image file not found: {image_path}")
            return None

        if self.yolo_detector is None:
            self.log_message("❌ No YOLO detector configured")
            return None

        try:
            # Read the image
            frame = cv2.imread(image_path)
            if frame is None:
                self.log_message(f"❌ Could not read image: {image_path}")
                return None
            # Process with YOLO detector
            annotated_frame, detection_summary, cart_count, roi_status = self.yolo_detector.detect(
                frame,
                None
            )
            annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            height, width, _ = annotated_frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(annotated_frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            qpixmap = QPixmap.fromImage(q_image) 
            scaled_pixmap = qpixmap.scaled(self.ui.label.width(), self.ui.label.height(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            
            # Set image to QLabel
            self.ui.label.setPixmap(scaled_pixmap)
            # Log results
            self.log_message(f"🖼️ Processed image: {image_path}")
            if detection_summary:
                self.log_message(f"🔍 Detection results: {detection_summary}")
            self.log_message(f"👥 cart count: {cart_count}")
            self.log_message(f"📌 ROI status: {roi_status}")

        except Exception as e:
            self.log_message(f"❌ Error processing image: {str(e)}")
            return None
