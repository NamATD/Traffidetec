import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import os

# Load biến môi trường từ file .env
load_dotenv()

def init_postgres_db():
    # Lấy thông tin kết nối từ biến môi trường
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')

    print("Đang kết nối đến PostgreSQL server...")
    
    try:
        # Kết nối đến PostgreSQL server (không phải database cụ thể)
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Kiểm tra xem database đã tồn tại chưa
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Đang tạo database {DB_NAME}...")
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"Database {DB_NAME} đã được tạo thành công!")
        else:
            print(f"Database {DB_NAME} đã tồn tại!")

        cursor.close()
        conn.close()

        # Kết nối đến database mới tạo để tạo các bảng
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        
        cursor = conn.cursor()
        
        # Tạo bảng traffic_data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS traffic_data (
                id SERIAL PRIMARY KEY,
                location_name VARCHAR(100) NOT NULL,
                density FLOAT NOT NULL,
                vehicle_count INTEGER NOT NULL,
                status VARCHAR(50) NOT NULL,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                lat FLOAT NOT NULL,
                lng FLOAT NOT NULL
            )
        """)
        
        # Tạo bảng traffic_history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS traffic_history (
                id SERIAL PRIMARY KEY,
                location_name VARCHAR(100) NOT NULL,
                density FLOAT NOT NULL,
                vehicle_count INTEGER NOT NULL,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tạo indexes cho các trường thường xuyên tìm kiếm
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_traffic_data_location 
            ON traffic_data(location_name)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_traffic_data_timestamp 
            ON traffic_data(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_traffic_history_location 
            ON traffic_history(location_name)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_traffic_history_timestamp 
            ON traffic_history(timestamp)
        """)
        
        conn.commit()
        print("Các bảng và index đã được tạo thành công!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Lỗi: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Bắt đầu khởi tạo database...")
    if init_postgres_db():
        print("Khởi tạo database hoàn tất!")
    else:
        print("Có lỗi xảy ra trong quá trình khởi tạo database!")