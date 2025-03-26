
from PySide6.QtCore import Signal, QObject

class CameraStopWorker(QObject):
    """Worker class to stop cameras in a separate thread."""
    progress_signal = Signal(int, str)  # (progress value, camera name)
    finished_signal = Signal(list, list)  # (stopped_cameras, failed_cameras)

    def __init__(self, camera_threads, stop_camera_method):
        super().__init__()
        self.camera_threads = camera_threads
        self.stop_camera_method = stop_camera_method  # Pass stop_camera function

    def run(self):
        """Stops cameras in a background thread."""
        connected_cameras = [name for name, thread in self.camera_threads.items() if thread.isRunning()]
        # total_cameras = len(connected_cameras)

        stopped_cameras = []
        failed_cameras = []

        for i, camera_name in enumerate(connected_cameras):
            success = self.stop_camera_method(camera_name)
            if success:
                stopped_cameras.append(camera_name)
            else:
                failed_cameras.append(camera_name)

            # Emit progress update
            self.progress_signal.emit(i + 1, camera_name)

        # Emit finished signal
        self.finished_signal.emit(stopped_cameras, failed_cameras)

