import face_recognition
import cv2
import os


def setup():
    known_face_encodings = []
    known_face_names = []

    for name in os.listdir("dataset"):
        for filename in os.listdir(f"dataset/{name}"):
            image = face_recognition.load_image_file(f"dataset/{name}/{filename}")
            embedding = face_recognition.face_encodings(image)[0]
            # print(filename)
            known_face_encodings.append(embedding)
            known_face_names.append(name)

    return known_face_encodings,known_face_names
