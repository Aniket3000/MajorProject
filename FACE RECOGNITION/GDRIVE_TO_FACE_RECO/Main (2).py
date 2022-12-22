from logging import exception
import pickle
import os
from PIL.Image import new
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request

import face_embeddings

import serial
import time

import face_recognition
import cv2
import numpy as np
import shutil

import io
import cv2
from matplotlib import pyplot as plt
import numpy as np
import imutils
# import easyocr
# from sqlalchemy.sql.functions import user
# from sqlalchemy.sql.schema import PrimaryKeyConstraint
# import user_website
# import SMS
import math

from threading import Thread

scopes = ['https://www.googleapis.com/auth/drive']
#text_id = '1M1_8Zl8C4s6Yo9LVnPIvO1ZAOpfqYa9H'

def get_image(client_secret_file, api_name, api_version, text_file_id, *scopes):
    '''This function downloads the image from the google drive
       and also sets up the drive accesss

    Paramters :
        client_secret_file
        api_name
        api_version
        scopes
        text_file_id   

    Returns :
        a downloaded image in images folder ith name ESP.JPG

    '''
    #print(client_secret_file, api_name, api_version, scopes, sep='-')
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]
    print(SCOPES)

    cred = None

    pickle_file = f'token_{API_SERVICE_NAME}_{API_VERSION}.pickle'
    # print(pickle_file)

    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            cred = flow.run_local_server()

        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
        print(API_SERVICE_NAME, 'service created successfully')

    except Exception as e:
        print('Unable to connect.')
        print(e)
        return None
    
    res = service.files().list(orderBy='createdTime desc',fields='files(id,name)',pageSize=1).execute()
    file_name = ""
    print(res)
    for file in res.get('files', []):
        text_file_id = file.get("id")
        file_name = file.get("name")
    
    # print(text_file_id)

    request = service.files().get_media(fileId=text_file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fd=fh, request=request,chunksize=204800)
    done = False
    try:
        while not done:
            status, done = downloader.next_chunk()
            # print('Downloading ID of image {0}'.format(status.progress()*100))

        fh.seek(0)
        with open(os.path.join('./images', file_name), 'wb') as f:
            shutil.copyfileobj(fh,f)
    except:
        print("Error!!")
        return False
    return file_name

def face_reco(path,known_face_encodings,known_face_names):
    # Initialize some variables

    frame = cv2.imread(path)
    # small_frame = cv2.resize(frame, (0,0), fx=0.5,fy=0.5,interpolation=cv2.INTER_AREA)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    store = cv2.GaussianBlur(frame, (13, 13), 0)
    rgb_small_frame = store[:, :, ::-1]

    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(rgb_small_frame,model="cnn")
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    # print(face_encodings)
    face_names = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        # print(face_distances)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
        # print(name)
        face_names.append(name)
    # print(face_names)
    return face_names

# def write_read(x):
    # str1 = ""
    # x = (str1.join(x))
    # print(x)
    # arduino.write(bytes(x, 'utf-8'))
    # time.sleep(0.05)
    # data = arduino.readline()
    # return data

def led_on_off(arduino,data):
    # user_input = input("\n Type on / off / quit : ")
    user_input = ""
    # print(data)
    if len(data)>0:
        user_input = "on"
    else:
        user_input = "off"
    if user_input =="on":
        print("Face is detected so door can open!!!!")
        time.sleep(10000) 
        arduino.write(b'H') 
        # led_on_off()
    elif user_input =="off":
        print("Face is not detected")
        time.sleep(0.1)
        arduino.write(b'L')
        # led_on_off()
    elif user_input =="quit" or user_input == "q":
        print("Program Exiting")
        time.sleep(0.1)
        arduino.write(b'L')
        arduino.close()
    else:
        print("Invalid input. Type on / off / quit.")
        # led_on_off()



if __name__ == '__main__':
    # thread = Thread(target = myfunc)
    # thread.start()
    # thread.run()

    # open database for every user get esp id , fetch umage , update amount
    # Create arrays of known face encodings and their names
    text_id = ""        
    # nm = get_image('credentials.json', 'drive', 'v3', text_id, scopes)
    path = "./images/20221220092340-ESP32-CAM.jpg"
    # path = "./images/passportsizeofficialphoto.png"
    # print(path)

    known_face_encodings, known_face_names = face_embeddings.setup()

    res = face_reco(path,known_face_encodings,known_face_names)
    print(res)
    arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1)

    time.sleep(2) # wait for the serial connection to initialize
    # data = write_read(res)
    led_on_off(arduino,res)