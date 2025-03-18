import ultralytics
from ultralytics import YOLO
import time
import cv2
import threading
import queue
import numpy as np
import os

class WebcamVideoStream:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        self.ret, self.frame = self.stream.read()
        self.stopped = False
        
    def start(self):
        threading.Thread(target=self.update, args=(), daemon=True).start()
        return self
        
    def update(self):
        while not self.stopped:
            self.ret, self.frame = self.stream.read()
            
    def read(self):
        return self.ret, self.frame
        
    def stop(self):
        self.stopped = True
        self.stream.release()

class YOLODetector:
    def __init__(self, model_path="yolov8s.pt"):
        print("Khởi tạo model YOLO... (có thể mất vài giây)")
        self.model = YOLO(model_path)
        self.model.overrides['conf'] = 0.8
        self.model.overrides['iou'] = 0.5
        self.model.overrides['agnostic_nms'] = True
        self.model.overrides['max_det'] = 1
        
        dummy_frame = np.zeros((640, 640, 3), dtype=np.uint8)
        _ = self.model(dummy_frame)
        print("Model YOLO đã sẵn sàng!")
        
        self.processing_queue = queue.Queue(maxsize=1)
        self.results_queue = queue.Queue(maxsize=1)
        self.stopped = False
        self.processing_lock = threading.Lock()
        
    def start(self):
        threading.Thread(target=self.detect, args=(), daemon=True).start()
        return self
        
    def detect(self):
        while not self.stopped:
            if not self.processing_queue.empty():
                try:
                    frame = self.processing_queue.get(timeout=0.1)
                    results = self.model(frame)
                    annotated_frame = results[0].plot()
                    
                    with self.processing_lock:
                        if not self.results_queue.empty():
                            try:
                                self.results_queue.get_nowait()
                            except queue.Empty:
                                pass
                        self.results_queue.put(annotated_frame)
                except Exception as e:
                    print(f"Lỗi trong quá trình detect: {e}")
                    time.sleep(0.01)
            else:
                time.sleep(0.01)
    
    def submit_frame(self, frame):
        with self.processing_lock:
            if self.processing_queue.empty():
                try:
                    self.processing_queue.put_nowait(frame)
                    return True
                except queue.Full:
                    return False
        return False
    
    def get_results(self):
        with self.processing_lock:
            if not self.results_queue.empty():
                try:
                    return True, self.results_queue.get_nowait()
                except queue.Empty:
                    return False, None
        return False, None
    
    def stop(self):
        self.stopped = True

# Hàm chính
def main():
    print("Khởi động chương trình...")
    
    detector = YOLODetector().start()
    webcam = WebcamVideoStream(src=0).start()
    print("Camera đã sẵn sàng!")
    
    processing_active = False
    last_frame_time = time.time()
    process_every_n_seconds = 0.
    fps_values = []
    save_path = "output_images"
    os.makedirs(save_path, exist_ok=True)

    print("Hướng dẫn:")
    print("- Nhấn 'p' để bật xử lý liên tục")
    print("- Nhấn 's' để dừng xử lý")
    print("- Nhấn 'SPACE' để chụp và xử lý ảnh ngay lập tức")
    print("- Nhấn 'q' để thoát")
    
    try:
        while True:
            start_time = time.time()
            
            ret, frame = webcam.read()
            if not ret:
                print("Không đọc được frame từ camera!")
                time.sleep(0.5)
                continue

            display_frame = frame.copy()

            current_time = time.time()
            if processing_active and (current_time - last_frame_time) > process_every_n_seconds:
                if detector.submit_frame(frame.copy()):
                    last_frame_time = current_time

            has_result, result_frame = detector.get_results()
            if has_result:
                display_frame = result_frame

            status = "Trạng thái: PLAY" if processing_active else "Trạng thái: STOP"
            cv2.putText(display_frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            frame_time = time.time() - start_time
            fps = 1.0 / (frame_time + 0.001)
            fps_values.append(fps)
            if len(fps_values) > 10:
                fps_values.pop(0)
            avg_fps = sum(fps_values) / len(fps_values)

            cv2.putText(display_frame, f"FPS: {avg_fps:.1f}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            cv2.imshow("YOLOv8 Webcam", display_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('p'):
                processing_active = True
                print("Chế độ: PLAY")
            elif key == ord('s'):
                processing_active = False
                print("Chế độ: STOP")
            elif key == ord(' '):  # Nhấn SPACE để chụp và xử lý ngay lập tức
                print("Chụp và xử lý ảnh...")
                if detector.submit_frame(frame.copy()):
                    time.sleep(0.1)  # Chờ kết quả
                    has_result, processed_frame = detector.get_results()
                    if has_result:
                        timestamp = time.strftime("%Y%m%d-%H%M%S")
                        filename = os.path.join(save_path, f"captured_{timestamp}.jpg")
                        cv2.imwrite(filename, processed_frame)
                        print(f"Ảnh đã lưu tại: {filename}")
                        cv2.imshow("Processed Image", processed_frame)

    except Exception as e:
        print(f"Lỗi: {e}")
    
    finally:
        print("Đang đóng chương trình...")
        webcam.stop()
        detector.stop()
        cv2.destroyAllWindows()
        print("Đã đóng chương trình!")

if __name__ == "__main__":
    main()
