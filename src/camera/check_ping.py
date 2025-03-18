import subprocess
import sys
from PySide6.QtCore import QThread, Signal

class PingThread(QThread):
    result_signal = Signal(str, bool, str)  # Signal to send (IP, is_reachable, message)

    def __init__(self, ip):
        super().__init__()
        self.ip = ip

    def run(self):
        try: 
            # Use `-n 1` for Windows, `-c 1` for Linux/macOS, add timeout
            if sys.platform == "win32":
                command = ["ping", "-n", "1", "-w", "1000", self.ip]  # 1 second timeout on Windows
           
            # Run the ping command
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=2)
            
            # Check if ping was successful
            is_reachable = result.returncode == 0
            
            # Get the ping output for debugging
            output = result.stdout
            
        except subprocess.TimeoutExpired:
            is_reachable = False
            output = "Ping process timed out"
        except Exception as e:
            is_reachable = False
            output = f"Error: {str(e)}"
        
        # Send back the result and debug info
        self.result_signal.emit(self.ip, is_reachable, output)