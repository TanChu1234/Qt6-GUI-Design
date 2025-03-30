import sys
import cv2
import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QHBoxLayout
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QThread, Signal

# URL của Camera IP (thay đổi theo hệ thống của bạn)
URL_CAM1 = "http://192.168.1.100:8080/video"  # Thay URL camera 1
URL_CAM2 = "http://192.168.1.101:8080/video"  # Thay URL camera 2

class CameraThread(QThread):
    frame_signal = Signal(QImage)  # Phát tín hiệu chứa hình ảnh

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.running = False

    def run(self):
        self.running = True
        # cap = cv2.VideoCapture(self.url)

        # if not cap.isOpened():
        #     print(f"❌ Không thể kết nối đến {self.url}")
        #     return

        # while self.running:
        #     ret, frame = cap.read()
        #     if ret:
        #         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #         h, w, ch = frame.shape
        #         bytes_per_line = ch * w
        #         q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        #         self.frame_signal.emit(q_img)  # Gửi hình ảnh đến QLabel

        # cap.release()

    def stop(self):
        self.running = False
        self.quit()
        self.wait()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Cấu hình cửa sổ
        self.setWindowTitle("Camera Control")
        self.setGeometry(100, 100, 1000, 500)

        # Nút điều khiển
        self.start_button = QPushButton("Mở Camera")
        self.start_button.clicked.connect(self.start_cameras)

        self.stop_button = QPushButton("Tắt Camera")
        self.stop_button.clicked.connect(self.stop_cameras)

        # QLabel để hiển thị hình ảnh camera
        self.cam1_label = QLabel()
        self.cam1_label.setFixedSize(400, 300)
        self.cam1_label.setStyleSheet("background-color: black; border-radius: 10px;")

        self.cam2_label = QLabel()
        self.cam2_label.setFixedSize(400, 300)
        self.cam2_label.setStyleSheet("background-color: black; border-radius: 10px;")

        # Layout hiển thị camera
        cam_layout = QHBoxLayout()
        cam_layout.addWidget(self.cam1_label)
        cam_layout.addWidget(self.cam2_label)

        # Layout chính
        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addLayout(cam_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Threads
        self.cam1_thread = CameraThread(URL_CAM1)
        self.cam1_thread.frame_signal.connect(self.update_cam1)

        self.cam2_thread = CameraThread(URL_CAM2)
        self.cam2_thread.frame_signal.connect(self.update_cam2)

    def start_cameras(self):
        """Mở cả hai camera"""
        if not self.cam1_thread.isRunning():
            self.cam1_thread.start()
        if not self.cam2_thread.isRunning():
            self.cam2_thread.start()

    def stop_cameras(self):
        """Tắt cả hai camera"""
        if self.cam1_thread.isRunning():
            self.cam1_thread.stop()
            self.cam1_label.clear()
            self.cam1_label.setStyleSheet("background-color: black; border-radius: 10px;")
        if self.cam2_thread.isRunning():
            self.cam2_thread.stop()
            self.cam2_label.clear()
            self.cam2_label.setStyleSheet("background-color: black; border-radius: 10px;")

    def update_cam1(self, image):
        """Cập nhật hình ảnh từ Camera 1"""
        self.cam1_label.setPixmap(QPixmap.fromImage(image))

    def update_cam2(self, image):
        """Cập nhật hình ảnh từ Camera 2"""
        self.cam2_label.setPixmap(QPixmap.fromImage(image))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
