# # Trigger camera
#     def trigger_http(self):
#         """Process the command from the lineEdit to trigger specific cameras."""
#         # Get the command from lineEdit
#         command = self.ui.lineEdit.text().strip()
        
#         if not command:
#             self.log_message("⚠️ Please enter a camera command in the text field")
#             return
            
#         self.log_message(f"🤖 Running AI once with command: {command}")
        
#         # Parse the command
#         parts = command.split()
        
#         # Check for trigger command
#         if parts[0].lower() == "trigger":
#             # Format: trigger camera1 camera2 camera3 [action]
            
#             # Check if there's at least one camera specified
#             if len(parts) < 2:
#                 self.log_message("⚠️ Please specify at least one camera to trigger")
#                 return
            
#             # Determine if the last part is an action
#             action = "capture"  # Default action
#             camera_names = parts[1:]
            
#             # If the last part doesn't look like a camera name, assume it's an action
#             if len(parts) > 2 and not self._is_camera_name(parts[-1]):
#                 action = parts[-1]
#                 camera_names = parts[1:-1]
            
#             # Process each camera
#             for camera_name in camera_names:
#                 target_camera = self._find_camera_by_partial_name(camera_name)
#                 if target_camera:
#                     self._trigger_camera(target_camera, action)
#                 else:
#                     self.log_message(f"❌ Camera matching '{camera_name}' not found")
            
#             return
#         # Check if the command is for a specific camera
#         if parts[0].startswith("cam"):
#             # Extract camera number or name
#             target_camera = self._find_camera(parts[0])
#             if not target_camera:
#                 return
            
#             # Start and display the camera
#             self._activate_camera(target_camera)
#         else:
#             self.log_message(f"⚠️ Unknown command: {command}")
#             self.log_message("ℹ️ Use 'cam1', 'trigger cam2 cam3', etc.")

#     def _trigger_camera(self, camera_name, action="capture"):
#         """Trigger an action on a specific camera and stop it after completion."""
#         # Check if camera is running
#         if camera_name not in self.camera_threads or not self.camera_threads[camera_name].isRunning():
#             # Try to start the camera first
#             self.log_message(f"🔄 Starting camera {camera_name} before triggering...")
#             self.start_camera(camera_name)
            
#             # Wait a bit for the camera to connect
#             QThread.msleep(300)
            
#             # Check again
#             if camera_name not in self.camera_threads or not self.camera_threads[camera_name].isRunning():
#                 self.log_message(f"❌ Failed to start camera {camera_name} for triggering")
#                 return
        
#         # Connect to the trigger_completed signal if not already connected
#         if not hasattr(self.camera_threads[camera_name], "_trigger_connected"):
#             self.camera_threads[camera_name].trigger_completed_signal.connect(
#                 lambda result, cam=camera_name: self.handle_trigger_result(result, cam)
#             )
#             self.camera_threads[camera_name]._trigger_connected = True
        
#         # Trigger the camera
#         self.camera_threads[camera_name].trigger(action)
#         self.log_message(f"🔔 Triggered {camera_name} with action: {action}")
    
#     def _handle_trigger_result(self, result, camera_name):
#         """Handle the result of a camera trigger and stop the camera."""
#         if result == "error":
#             self.log_message(f"❌ Trigger failed for {camera_name}")
#         else:
#             # Store the result
#             self.trigger_results[camera_name] = result
            
#             # Log the result
#             if result.endswith(".jpg"):
#                 self.log_message(f"📸 Image captured from {camera_name}: {result}")
#             else:
#                 self.log_message(f"✅ Trigger result for {camera_name}: {result}")
        
#         # Stop the camera after trigger completes
#         self.log_message(f"🛑 Stopping camera {camera_name} after trigger")
#         self.stop_camera(camera_name)
        
#         # Clear the display if this was the current camera being displayed
#         if self.displaying and self.current_camera == camera_name:
#             self.ui.label.clear()
#             self.current_camera = None
#             self.displaying = False
#             self.ui.display.setText("Display")
    
#     """ Utils for searching camera """
#     def _find_camera(self, cam_identifier):
#         """Find a camera by number or name."""
#         if cam_identifier.startswith("cam"):
#             cam_identifier = cam_identifier[3:]  # Remove "cam" prefix
        
#         # If it's a number, try to find by index
#         if cam_identifier.isdigit():
#             cam_index = int(cam_identifier) - 1  # Convert to 0-based index
#             if 0 <= cam_index < self.ui.listWidget.count():
#                 return self.ui.listWidget.item(cam_index).text()
#             else:
#                 self.log_message(f"❌ Camera {cam_identifier} not found in the list")
#                 return None
#         else:
#             # Try to find by name
#             for i in range(self.ui.listWidget.count()):
#                 camera_name = self.ui.listWidget.item(i).text()
#                 if cam_identifier.lower() in camera_name.lower():
#                     return camera_name
            
#             self.log_message(f"❌ Camera matching '{cam_identifier}' not found")
#             return None

#     def _is_camera_name(self, name):
#         """Check if the given name is a potential camera name by searching for matches."""
#         for i in range(self.ui.listWidget.count()):
#             camera_name = self.ui.listWidget.item(i).text()
#             if name.lower() in camera_name.lower():
#                 return True
#         return False

#     def _find_camera_by_partial_name(self, name):
#         """Find a camera that contains the given name."""
#         for i in range(self.ui.listWidget.count()):
#             camera_name = self.ui.listWidget.item(i).text()
#             if name.lower() in camera_name.lower():
#                 return camera_name
#         return None
    
#     def _activate_camera(self, camera_name):
#         """Start and display a camera."""
#         # Check if the camera is already running
#         if camera_name in self.camera_threads and self.camera_threads[camera_name].isRunning():
#             self.log_message(f"✅ Using camera: {camera_name}")
#         else:
#             # Start the camera
#             self.log_message(f"🔄 Starting camera: {camera_name}")
#             self.start_camera(camera_name)
        
#         # Set this as the current camera to display
#         self.current_camera = camera_name
#         self.displaying = True
#         self.ui.display.setText("Hide")
#         self.log_message(f"🖥️ Now displaying {camera_name}")

#     def trigger_tcp(self):
#         """Run AI in continuous mode. Currently a placeholder."""
#         self.log_message("♻️ Running AI continuously...")
#         # Implementation for continuous mode would go here
            
    