import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QSizePolicy
from camera.camera_ui_control import CameraWidget  # ✅ Import CameraWidget
from communication.server_tcp import TCPServerApp
from ui.main_window import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Management")
        # self.resize(1330, 830)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # ✅ Initialize UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

         # Create widget instances
        self.camera_widget = CameraWidget()
        self.tcp_widget = TCPServerApp(self.camera_widget)

        # Add widgets to stackedWidget
        self.camera_index = self.ui.stackedWidget.addWidget(self.camera_widget)
        self.tcp_index = self.ui.stackedWidget.addWidget(self.tcp_widget)

        # Set initial page
        self.ui.stackedWidget.setCurrentIndex(self.camera_index)

        # Connect navigation buttons
        self.ui.camera_page.clicked.connect(self.show_camera_page)
        self.ui.tcp_page.clicked.connect(self.show_tcp_page)

    def show_camera_page(self):
        """Switches to the CameraWidget page."""
        self.ui.stackedWidget.setCurrentIndex(self.camera_index)

    def show_tcp_page(self):
        """Switches to the TCPServerApp page."""
        self.ui.stackedWidget.setCurrentIndex(self.tcp_index)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
