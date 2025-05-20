from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout, QInputDialog, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QIcon
import cv2
import face_recognition
import unicodedata

from face_data import load_face_data, add_encoding, delete_encoding
from camera import Camera
from recognizer import find_faces, match_faces
from voice_greeter import VoiceGreeter

class FaceRecognitionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Au Lac Face Recognition System")
        self.setWindowIcon(QIcon("assets/AULAC.png"))

        self.face_data = load_face_data()
        self.recognizing = False
        self.voice_greeter = VoiceGreeter()
        self.last_greeted = set()  # Lưu những người đã được chào trong frame hiện tại

        self.camera = Camera()
        self._init_ui()
        self._start_timer()

    def _init_ui(self):
        # Video display
        self.video_label = QLabel(alignment=Qt.AlignCenter)
        self.video_label.setFixedSize(1280, 720)

        # Buttons
        self.btn_add = QPushButton("Thêm khuôn mặt")
        self.btn_delete = QPushButton("Xóa khuôn mặt")
        self.btn_recognize = QPushButton("Nhận dạng khuôn mặt")
        self.btn_list = QPushButton("Xem danh sách")
        self.btn_exit = QPushButton("Thoát")

        # Kết nối signal
        self.btn_add.clicked.connect(self.add_face)
        self.btn_delete.clicked.connect(self.delete_face)
        self.btn_recognize.clicked.connect(self.toggle_recognition)
        self.btn_list.clicked.connect(self.list_faces)
        self.btn_exit.clicked.connect(self.close)

        # Đặt chiều cao cho các nút
        for btn in [self.btn_add, self.btn_delete, self.btn_recognize, self.btn_list, self.btn_exit]:
            btn.setFixedHeight(50)

        # Info labels / logo
        self.system_label = QLabel("Au Lac Face Recognition System", alignment=Qt.AlignCenter)
        self.system_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.logo_label = QLabel(alignment=Qt.AlignCenter)
        self.logo_label.setPixmap(QPixmap("assets/AULAC.png").scaledToWidth(150, Qt.SmoothTransformation))
        self.company_label = QLabel("AU LAC CONSTRUCTION", alignment=Qt.AlignCenter)
        self.company_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        # Layouts
        right_layout = QVBoxLayout()
        for w in [self.btn_add, self.btn_delete, self.btn_recognize, self.btn_list, self.btn_exit]:
            right_layout.addWidget(w)
        right_layout.addStretch()
        right_layout.addWidget(self.system_label)
        right_layout.addWidget(self.logo_label)
        right_layout.addWidget(self.company_label)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.video_label)
        main_layout.addLayout(right_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def _start_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def normalize_name_for_display(self, name: str) -> str:
        # NFKD tách ký tự gốc và dấu, sau đó loại bỏ dấu và chuyển in hoa
        nfkd = unicodedata.normalize('NFKD', name)
        no_diacritics = ''.join(c for c in nfkd if not unicodedata.combining(c))
        return no_diacritics.upper()

    def update_frame(self):
        ret, frame = self.camera.read_frame()
        if not ret:
            return
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if self.recognizing and self.face_data:
            locs, encs = find_faces(rgb)
            matches = match_faces(encs, self.face_data)

            current_faces = set()
            for ((top, right, bottom, left), (name, color)) in zip(locs, matches):
                display_name = self.normalize_name_for_display(name)

                # Vẽ hộp và tên hiển thị
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(
                    frame,
                    display_name,
                    (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2,
                    color,
                    3
                )

                # Voice greeting vẫn dùng tên gốc có dấu
                if name not in self.last_greeted and name != "Unknown":
                    self.voice_greeter.greet(name)

                current_faces.add(name)

            self.last_greeted = current_faces

        h, w, ch = frame.shape
        qt_img = QImage(frame.data, w, h, ch * w, QImage.Format_BGR888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_img))

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
            ret, frame = self.camera.read_frame()
            if not ret:
                continue
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            locs, _ = find_faces(rgb)
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
        add_encoding(self.face_data, name, samples)
        QMessageBox.information(self, "Thành công", f"Đã thêm {name}.")

    def delete_face(self):
        name, ok = QInputDialog.getText(self, "Xóa khuôn mặt", "Nhập tên:")
        if not ok or not name:
            return
        if name in self.face_data:
            delete_encoding(self.face_data, name)
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
        self.camera.release()
        super().closeEvent(event)

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = FaceRecognitionApp()
    window.show()
    sys.exit(app.exec_())