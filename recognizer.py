import face_recognition

def find_faces(frame_rgb):
    """ Trả về face_locations và face_encodings """
    locs = face_recognition.face_locations(frame_rgb)
    encs = face_recognition.face_encodings(frame_rgb, locs)
    return locs, encs

def match_faces(encodings, known_data: dict, threshold=0.4):
    """
    Với mỗi encoding, so sánh khoảng cách tới known_data.
    Trả về list các tuple (name, color) tương ứng.
    """
    results = []
    for enc in encodings:
        name = "Unknown"
        color = (0, 0, 255)
        if known_data:
            # tính khoảng cách
            dists = {n: face_recognition.face_distance([e], enc)[0]
                     for n, e in known_data.items()}
            best = min(dists, key=dists.get)
            if dists[best] < threshold:
                name, color = best, (0, 255, 0)
        results.append((name, color))
    return results
