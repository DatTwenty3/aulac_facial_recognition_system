import sys
import cv2
import face_recognition
import numpy as np
import pickle
import os
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout, QInputDialog, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap

# Đường dẫn đến file lưu trữ dữ liệu khuôn mặt
DATA_FILE = 'face_data.pkl'

# Hàm để tải dữ liệu khuôn mặt từ file
# Lưu trữ encoding trung bình cho mỗi cá nhân để cải thiện độ chính xác

def load_face_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'rb') as f:
            return pickle.load(f)
    return {}

def save_face_data(face_data):
    with open(DATA_FILE, 'wb') as f:
        pickle.dump(face_data, f)

class FaceRecognitionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AU LAC FACE RECONGNITION SYSTEM")
        self.face_data = load_face_data()  # {'name': np.array(128)}
        self.recognizing = False

        # Thiết lập camera với độ phân giải lớn hơn
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # Giao diện
        self.video_label = QLabel()
        # Khung video to hơn
        self.video_label.setFixedSize(1280, 720)
        self.video_label.setAlignment(Qt.AlignCenter)

        self.btn_add = QPushButton("Thêm khuôn mặt")
        self.btn_delete = QPushButton("Xóa khuôn mặt")
        self.btn_recognize = QPushButton("Nhận dạng khuôn mặt")
        self.btn_list = QPushButton("Xem danh sách")
        self.btn_exit = QPushButton("Thoát")
        self.btn_add.clicked.connect(self.add_face)
        self.btn_delete.clicked.connect(self.delete_face)
        self.btn_recognize.clicked.connect(self.toggle_recognition)
        self.btn_list.clicked.connect(self.list_faces)
        self.btn_exit.clicked.connect(self.close)

        # Bố cục nút bên phải
        right_layout = QVBoxLayout()
        for btn in [self.btn_add, self.btn_delete, self.btn_recognize, self.btn_list, self.btn_exit]:
            btn.setFixedHeight(50)
            right_layout.addWidget(btn)
        right_layout.addStretch()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.video_label)
        main_layout.addLayout(right_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Timer cập nhật khung hình
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if self.recognizing and self.face_data:
            locs = face_recognition.face_locations(rgb_frame)
            encodings = face_recognition.face_encodings(rgb_frame, locs)
            for (top, right, bottom, left), encoding in zip(locs, encodings):
                name = "Unknown"
                distances = {person: face_recognition.face_distance([enc], encoding)[0]
                             for person, enc in self.face_data.items()}
                if distances:
                    best_match = min(distances, key=distances.get)
                    if distances[best_match] < 0.5:
                        name = best_match
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

        h, w, ch = frame.shape
        bytes_line = ch * w
        qt_image = QImage(frame.data, w, h, bytes_line, QImage.Format_BGR888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image))

    def add_face(self):
        name, ok = QInputDialog.getText(self, "Thêm khuôn mặt", "Nhập tên:")
        if not ok or not name:
            return
        if name in self.face_data:
            QMessageBox.information(self, "Thông báo", f"{name} đã tồn tại.")
            return
        QMessageBox.information(self, "Hướng dẫn", "Chương trình sẽ chụp 20 mẫu, vui lòng nhìn vào camera.")
        samples = []
        count = 0
        while count < 20:
            ret, frame = self.cap.read()
            if not ret:
                continue
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            locs = face_recognition.face_locations(rgb)
            if locs:
                enc = face_recognition.face_encodings(rgb, locs)[0]
                samples.append(enc)
                count += 1
                for (t, r, b, l) in locs:
                    cv2.rectangle(frame, (l, t), (r, b), (0, 255, 0), 2)
                    cv2.putText(frame, f"{count}/20", (l, t - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                cv2.imshow('Capturing', frame)
                cv2.waitKey(100)
        cv2.destroyWindow('Capturing')
        mean_encoding = np.mean(samples, axis=0)
        self.face_data[name] = mean_encoding
        save_face_data(self.face_data)
        QMessageBox.information(self, "Thành công", f"Đã thêm {name}.")

    def delete_face(self):
        name, ok = QInputDialog.getText(self, "Xóa khuôn mặt", "Nhập tên:")
        if not ok or not name:
            return
        if name in self.face_data:
            del self.face_data[name]
            save_face_data(self.face_data)
            QMessageBox.information(self, "Thành công", f"Đã xóa {name}.")
        else:
            QMessageBox.warning(self, "Lỗi", f"Không tìm thấy {name}.")

    def list_faces(self):
        if not self.face_data:
            QMessageBox.information(self, "Danh sách", "Không có dữ liệu.")
        else:
            names = '\n'.join(self.face_data.keys())
            QMessageBox.information(self, "Danh sách khuôn mặt", names)

    def toggle_recognition(self):
        if not self.recognizing:
            if not self.face_data:
                QMessageBox.warning(self, "Lỗi", "Chưa có dữ liệu.")
                return
            self.recognizing = True
            self.btn_recognize.setText("Dừng nhận dạng")
        else:
            self.recognizing = False
            self.btn_recognize.setText("Nhận dạng khuôn mặt")

    def closeEvent(self, event):
        self.cap.release()
        cv2.destroyAllWindows()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FaceRecognitionApp()
    window.show()
    sys.exit(app.exec_())
