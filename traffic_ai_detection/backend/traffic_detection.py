import cv2
import numpy as np
from ultralytics import YOLO
import os
from datetime import datetime
import random
from database import SessionLocal, TrafficData, TrafficHistory

class TrafficDetector:
    def __init__(self):
        # Sử dụng dấu '/' thay vì dấu '\\'
        self.traffic_points = {
            'Hàng Xanh': {
                'lat': 10.8035, 
                'lng': 106.6963,
                'video_path': 'videos/hang_xanh.mp4',  # Sử dụng dấu '/' thay vì '\\'
                'name': 'Hàng Xanh',
                'address': 'Ngã tư Hàng Xanh, Bình Thạnh'
            },
            'Điện Biên Phủ': {
                'lat': 10.8012, 
                'lng': 106.7001,
                'video_path': 'videos/dien_bien_phu.mp4',  # Sử dụng dấu '/' thay vì '\\'
                'name': 'Điện Biên Phủ',
                'address': 'Điện Biên Phủ, Bình Thạnh'
            },
            'Bình Quới': {
                'lat': 10.7988, 
                'lng': 106.7045,
                'video_path': 'videos/binh_quoi.mp4',  # Sử dụng dấu '/' thay vì '\\'
                'name': 'Bình Quới',
                'address': 'Bình Quới, Bình Thạnh'
            },
            'Bình Lợi': {
                'lat': 10.7955, 
                'lng': 106.7089,
                'video_path': 'videos/binh_loi.mp4',  # Sử dụng dấu '/' thay vì '\\'
                'name': 'Bình Lợi',
                'address': 'Cầu Bình Lợi, Bình Thạnh'
            }
        }
        try:
            self.model = YOLO('yolov8n.pt')
        except:
            self.model = None
            print("Warning: YOLO model not loaded")

    def get_mock_data(self):
        density = random.uniform(20, 90)
        vehicle_count = random.randint(10, 50)
        
        if density < 30:
            status = "Thông thoáng"
        elif density < 60:
            status = "Đông đúc"
        else:
            status = "Ùn tắc"
            
        return {
            'density': round(density, 2),
            'status': status,
            'vehicle_count': vehicle_count,
            'timestamp': datetime.now().isoformat()
        }

    def get_all_points_status(self):
        db = SessionLocal()
        try:
            results = []
            for point_name, point_data in self.traffic_points.items():
                mock_data = self.get_mock_data()
                
                # Lưu vào database
                traffic_data = TrafficData(
                    location_name=point_name,
                    density=mock_data['density'],
                    vehicle_count=mock_data['vehicle_count'],
                    status=mock_data['status'],
                    lat=point_data['lat'],
                    lng=point_data['lng']
                )
                db.add(traffic_data)
                
                # Lưu vào history
                history_data = TrafficHistory(
                    location_name=point_name,
                    density=mock_data['density'],
                    vehicle_count=mock_data['vehicle_count']
                )
                db.add(history_data)
                
                # Thêm vào kết quả
                results.append({
                    'name': point_name,
                    'lat': point_data['lat'],
                    'lng': point_data['lng'],
                    'video_path': point_data['video_path'],
                    'address': point_data['address'],
                    'density': mock_data['density'],
                    'status': mock_data['status'],
                    'vehicle_count': mock_data['vehicle_count'],
                    'timestamp': mock_data['timestamp']
                })
            
            db.commit()
            return results
            
        except Exception as e:
            print(f"Database error: {e}")
            db.rollback()
            return []
            
        finally:
            db.close()