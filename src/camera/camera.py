from flask import Flask, Response
import cv2

app = Flask(__name__)

# Địa chỉ RTSP của camera
rtsp_url = "rtsp://chunhattan:12345678@192.168.192.189:554/stream1"

def generate_frames():
    cap = cv2.VideoCapture(rtsp_url)
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return "<h1>RTSP Stream</h1><img src='/video_feed' width='640'>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
