import subprocess
import sys

def ping_camera(ip):
    """Simple function to check if the camera IP is reachable."""
    try:
        if sys.platform == "win32":
            command = ["ping", "-n", "1", "-w", "1000", ip]  # Windows: 1 ping, 1s timeout
        # else:
        #     command = ["ping", "-c", "1", "-W", "1", ip]  # Linux/macOS: 1 ping, 1s timeout
        
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=2)
        return result.returncode == 0  # Returns True if reachable, False otherwise
    except subprocess.TimeoutExpired:
        return False
    except Exception as e:
        print(f"Error pinging {ip}: {str(e)}")
        return False