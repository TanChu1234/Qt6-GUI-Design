import json
import os

class CameraConfigManager:
    """Manages saving and loading camera configurations"""
    
    def __init__(self, config_file="src/asset/camera_storage/camera_config.json"):
        # Use absolute path or relative to execution directory
        self.config_file = config_file
        self.cameras = []
        
    def load_config(self):
        """Load camera configurations from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.cameras = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}")
                self.cameras = []
                
        return self.cameras
        
    def save_config(self):
        """Save camera configurations to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.cameras, f, indent=4)
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False
            
    def add_camera(self, camera_info):
        """Add or update a camera in the configuration"""
        # Load latest configuration to avoid overwriting other changes
        self.load_config()
        
        # Check if camera with same IP already exists
        for i, camera in enumerate(self.cameras):
            if camera["ip_address"] == camera_info["ip_address"]:
                # Update existing camera
                self.cameras[i] = camera_info
                self.save_config()
                return "updated"
                
        # Add new camera
        self.cameras.append(camera_info)
        self.save_config()
        return "added"
        
    def remove_camera(self, camera_info):
        """Remove a camera from the configuration"""
        # Load latest configuration
        self.load_config()
        
        # Find and remove camera based on IP address
        for i, camera in enumerate(self.cameras):
            if camera["ip_address"] == camera_info["ip_address"]:
                del self.cameras[i]
                self.save_config()
                return True
                
        return False  # Camera not found
        
    def remove_camera_by_name(self, camera_name):
        """Remove a camera from the configuration by name"""
        # Load latest configuration
        self.load_config()
        
        # Find and remove camera based on name
        for i, camera in enumerate(self.cameras):
            if camera["camera_name"] == camera_name:
                del self.cameras[i]
                self.save_config()
                return True
                
        return False  # Camera not found