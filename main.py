import cv2
import face_recognition
import numpy as np
import pickle
import os
import time

# Đường dẫn đến file lưu trữ dữ liệu khuôn mặt
DATA_FILE = 'face_data.pkl'

# Hàm để tải dữ liệu khuôn mặt từ file
def load_face_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'rb') as f:
            return pickle.load(f)
    return {}

# Hàm để lưu dữ liệu khuôn mặt vào file
def save_face_data(face_data):
    with open(DATA_FILE, 'wb') as f:
        pickle.dump(face_data, f)

# Hàm để thêm khuôn mặt mới
def add_face(name):
    cap = cv2.VideoCapture(0)
    # Đặt kích thước khung camera
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    face_data = load_face_data()
    if name in face_data:
        print(f"Khuôn mặt của {name} đã tồn tại.")
        cap.release()
        return
    print(f"Bắt đầu chụp 20 mẫu khuôn mặt cho {name}. Vui lòng nhìn vào camera.")
    # Tạo cửa sổ với kích thước lớn hơn
    cv2.namedWindow('Capturing Face', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Capturing Face', 1280, 720)
    samples = []
    count = 0
    while count < 20:
        ret, frame = cap.read()
        if not ret:
            continue
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        if face_locations:
            face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
            samples.append(face_encoding)
            count += 1
            print(f"Đã chụp mẫu thứ {count}")
            # Vẽ khung chữ nhật xung quanh khuôn mặt
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, f"Sample {count}/20", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            time.sleep(0.5)
        cv2.imshow('Capturing Face', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    if samples:
        face_data[name] = samples
        save_face_data(face_data)
        print(f"Đã thêm khuôn mặt của {name}.")

# Hàm để xóa khuôn mặt
def delete_face(name):
    face_data = load_face_data()
    if name in face_data:
        del face_data[name]
        save_face_data(face_data)
        print(f"Đã xóa khuôn mặt của {name}.")
    else:
        print(f"Không tìm thấy khuôn mặt của {name}.")

# Hàm để nhận dạng khuôn mặt
def recognize_faces():
    face_data = load_face_data()
    if not face_data:
        print("Không có dữ liệu khuôn mặt nào để nhận dạng.")
        return
    cap = cv2.VideoCapture(0)
    # Đặt kích thước khung camera
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    # Tạo cửa sổ với kích thước lớn hơn
    cv2.namedWindow('Face Recognition', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Face Recognition', 1280, 720)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            name = "Unknown"
            for person, samples in face_data.items():
                results = face_recognition.compare_faces(samples, face_encoding)
                if all(results):
                    name = person
                    break
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        cv2.imshow('Face Recognition', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

# Hàm để liệt kê các khuôn mặt trong cơ sở dữ liệu
def list_faces():
    face_data = load_face_data()
    if not face_data:
        print("Cơ sở dữ liệu khuôn mặt hiện đang trống.")
    else:
        print("Danh sách các khuôn mặt trong cơ sở dữ liệu:")
        for name in face_data.keys():
            print(f"- {name}")

# Menu chính
def main():
    while True:
        print("\nChọn chức năng:")
        print("1. Thêm khuôn mặt mới")
        print("2. Xóa khuôn mặt")
        print("3. Nhận dạng khuôn mặt")
        print("4. Xem danh sách khuôn mặt")
        print("5. Thoát")
        choice = input("Nhập lựa chọn (1-5): ")
        if choice == '1':
            name = input("Nhập tên của người cần thêm: ")
            add_face(name)
        elif choice == '2':
            name = input("Nhập tên của người cần xóa: ")
            delete_face(name)
        elif choice == '3':
            recognize_faces()
        elif choice == '4':
            list_faces()
        elif choice == '5':
            break
        else:
            print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")

if __name__ == "__main__":
    main()