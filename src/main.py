import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QSizePolicy, QWidget
from PySide6.QtGui import QIcon
from camera.camera_ui_control import CameraWidget
from communication.server_tcp import TCPServerApp
from ui.main_window import Ui_MainWindow
from ui.dash_board import Ui_dashboard

class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create the UI for the dashboard
        self.ui = Ui_dashboard()
        self.ui.setupUi(self)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Management System")
        self.setWindowIcon(QIcon("src/asset/images/thado.png"))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Initialize UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Create widget instances
        self.dashboard_widget = DashboardWidget()  # Now a proper QWidget
        self.camera_widget = CameraWidget()
        self.tcp_widget = TCPServerApp(self.camera_widget)

        # Add widgets to stackedWidget
        self.camera_index = self.ui.stackedWidget.addWidget(self.camera_widget)
        self.tcp_index = self.ui.stackedWidget.addWidget(self.tcp_widget)
        self.dashboard_index = self.ui.stackedWidget.addWidget(self.dashboard_widget)

        # Set initial page
        self.ui.stackedWidget.setCurrentIndex(self.camera_index)
        
        # Store navigation buttons in a list for easy management
        self.nav_buttons = [
            self.ui.dashboard_page,  # Dashboard
            self.ui.camera_page,  # Camera
            self.ui.tcp_page,     # TCP
        ]
        
        # Connect navigation buttons
        self.ui.camera_page.clicked.connect(lambda: self.show_page(self.camera_index, self.ui.camera_page))
        self.ui.tcp_page.clicked.connect(lambda: self.show_page(self.tcp_index, self.ui.tcp_page))
        self.ui.dashboard_page.clicked.connect(lambda: self.show_page(self.dashboard_index, self.ui.dashboard_page))
    
        # Set initial button style
        self.reset_button_styles()
        self.highlight_current_button(self.ui.dashboard_page)
        
    def reset_button_styles(self):
        """Reset all navigation buttons to default style."""
        default_style = (
            "QPushButton {"
            "    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, "
            "                                stop:0 #007AFF, stop:1 #009FFF);"
            "    border: none;"
            "    padding: 12px 20px;"
            "    font-size: 20px;"
            "    font-weight: bold;"
            "    border-radius: 10px;"
            "    color: white;"
            "    min-width: 150px;"
            "    text-align: left;"
            "    padding-left: 10px;"
            "}"
            "\n"
            "/* Button Hover Effect */\n"
            "QPushButton:hover {\n"
            "    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, \n"
            "                                stop:0 #66BFFF, stop:1 #80D5FF);\n"
            "}\n"
        )
        for button in self.nav_buttons:
            button.setStyleSheet(default_style)

    def highlight_current_button(self, current_button):
        """Highlight the currently selected button."""
        selected_style = (
            "QPushButton {"
            "    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, "
            "                                stop:0 #0056b3, stop:1 #003366);"  # Darker blue gradient
            "    border: none;"
            "    padding: 12px 20px;"
            "    font-size: 20px;"
            "    font-weight: bold;"
            "    border-radius: 10px;"
            "    color: white;"
            "    min-width: 150px;"
            "    text-align: left;"
            "    padding-left: 10px;"
            "}"            
        )
        # Reset all buttons first
        self.reset_button_styles()
        # Apply highlight to current button
        current_button.setStyleSheet(selected_style)

    def show_page(self, page_index, current_button):
        # Switch to the selected page
        self.ui.stackedWidget.setCurrentIndex(page_index)
        
        # Highlight the current button
        self.highlight_current_button(current_button)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())