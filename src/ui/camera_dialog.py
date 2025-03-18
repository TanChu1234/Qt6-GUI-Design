from PySide6.QtWidgets import QDialog
from ui.camera_information import Ui_Form  # Import the generated UI class

class CameraDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # Connect button actions
        self.ui.ok_button.clicked.connect(self.accept)  # Close dialog and return success
        self.ui.cancel_button.clicked.connect(self.reject)  # Close dialog and return failure

    def get_camera_info(self):
        """Retrieve user input values."""
        return {
            "camera_name": self.ui.cam_name.text(),
            "ip_address": self.ui.cam_ip.text(),
            "port": self.ui.cam_port.text(),
            "username": self.ui.cam_user.text(),
            "password": self.ui.cam_pass.text(),
            "protocol": self.ui.comboBox.currentText(),
        }
