import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QSizePolicy
from ui.camera_ui import CameraWidget  # ✅ Import CameraWidget
from ui.main_window import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Management")
        self.resize(1330, 830)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # ✅ Initialize UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # ✅ Create CameraWidget instance
        self.camera_widget = CameraWidget()

        # ✅ Add CameraWidget to stackedWidget
        self.ui.stackedWidget.addWidget(self.camera_widget)

        # ✅ Optionally, connect a button to switch to CameraWidget page
        self.ui.camera_page.clicked.connect(self.show_camera_page)

    def show_camera_page(self):
        """Switches to the CameraWidget page."""
        self.ui.stackedWidget.setCurrentWidget(self.camera_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
