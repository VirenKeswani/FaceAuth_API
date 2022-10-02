import face_recognition
import cv2
import os
import numpy as np

known_face_encodings = [

]
known_face_names = [
]

path  = './known_users'
folders = os.listdir(path)
for i in folders:
    # print(i,"\n")
    #list all the files in the folder
    files = os.walk(os.path.join(path,i))
    for j in files:
        k=j[2]
        for l in k:
            face_name = l.split('.')[0]
            print(face_name)
            newface = face_recognition.load_image_file(os.path.join(path,i,l))
            known_face_names.append(face_name)
            known_face_encodings.append(face_recognition.face_encodings(newface)[0])
            
            




        


# obama_image = face_recognition.load_image_file("trial.jpg")
# obama_face_encoding = face_recognition.face_encodings(obama_image)[0]