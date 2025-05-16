import os, pickle
import numpy as np

DATA_FILE = os.path.join('data', 'face_data.pkl')

def load_face_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'rb') as f:
            return pickle.load(f)
    return {}

def save_face_data(face_data: dict):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'wb') as f:
        pickle.dump(face_data, f)

def add_encoding(face_data: dict, name: str, encodings: list):
    """
    Lưu encoding trung bình từ danh sách encodings.
    """
    face_data[name] = np.mean(encodings, axis=0)
    save_face_data(face_data)

def delete_encoding(face_data: dict, name: str):
    if name in face_data:
        del face_data[name]
        save_face_data(face_data)
