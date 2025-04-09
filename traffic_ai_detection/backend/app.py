from flask import Flask, jsonify, send_from_directory, Response
from flask_cors import CORS
import os
from traffic_detection import TrafficDetector
from database import init_db
import cv2
import numpy as np

app = Flask(__name__)
CORS(app)
VIDEOS_FOLDER = 'C:/TEST/traffic_ai_detection/backend/video'
print(f"Videos folder path: {VIDEOS_FOLDER}")
# Khởi tạo database
init_db()

detector = TrafficDetector()

def generate_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    while True:
        success, frame = cap.read()
        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset video về đầu
            continue
            
        # Xử lý frame với YOLO để phát hiện phương tiện
        results = detector.model(frame)
        
        # Vẽ bounding box và đếm phương tiện
        vehicle_count = 0
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Chỉ đếm các phương tiện (class 2, 3, 5, 7 trong COCO dataset)
                if box.cls in [2, 3, 5, 7]:
                    vehicle_count += 1
                    x1, y1, x2, y2 = box.xyxy[0]
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        
        # Thêm text hiển thị số lượng phương tiện
        cv2.putText(frame, f'Vehicles: {vehicle_count}', (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed/<path:filename>')
def video_feed(filename):
    video_path = os.path.join(VIDEOS_FOLDER, filename)
    return Response(generate_frames(video_path),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/videos/<path:filename>')
def serve_video(filename):
    try:
        return send_from_directory(
            VIDEOS_FOLDER,
            filename,
            mimetype='video/mp4',
            as_attachment=False
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/traffic')
def get_traffic_data():
    try:
        points = detector.get_all_points_status()
        print("Traffic points:", points)  # Debug log
        return jsonify(points)
    except Exception as e:
        print(f"Error getting traffic data: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs(VIDEOS_FOLDER, exist_ok=True)
    app.run(debug=True)