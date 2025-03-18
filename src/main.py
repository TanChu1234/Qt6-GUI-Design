import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QSizePolicy
from ui.camera_ui import CameraWidget  # ✅ Corrected import

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Management")
        self.resize(1330, 830)
         # ✅ Allow resizing
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # ✅ Create a central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # ✅ Add CameraWidget
        self.ui = CameraWidget()
        layout.addWidget(self.ui)  # ✅ Corrected: Add to layout instead of calling setupUi(central_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
