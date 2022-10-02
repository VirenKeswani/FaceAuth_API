
from importlib.resources import path
import re
from urllib import response
from flask import Flask,redirect, url_for, request , Response , render_template , g, url_for
import pymongo
from flask_pymongo import PyMongo
import json
import secrets
import os
import face_recognition
import cv2
import numpy as np

app= Flask(__name__)


try:
    mongo=pymongo.MongoClient(host="localhost", 
    port=27017, 
    serverSelectionTimeoutMS=1000)

    db=mongo.FaceAuthUser

    mongo.server_info() #trigger exception if cannot connect to db
    print("Connected to mongodb")

except:    
    print(f"Error cannot connect to db {mongo.server_info()}")

# app.config["MONGO_URI"]="mongodb://localhost:27017/FaceAuthUser"
# mongo = PyMongo(app)




#face reg -----------------------


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
            
            
camera = cv2.VideoCapture(0)
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

detected_face = 'none'

def gen_frames():  
    global detected_face
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Only process every other frame of video to save time
           
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"
                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                face_names.append(name)
                
            

            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        #if face name is not empty then redirect to home page
        if face_names:
            detected_face = face_names
            return
            # detected_face = face_names[0]

        

        






@app.route('/video_feed')
def video_feed():
    print(request.method)
    return Response( gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/getface')
def getface():
    print(detected_face[0])
    return str(detected_face)
@app.route('/')
# def hello_world():
#     return secrets.token_urlsafe(16)
def index():
    print(request.method)
    if request.method == 'GET':
        return render_template('index.html')
    else:
        return redirect('/getface' , code=302)
    # print(detected_face)
    # while detected_face != 'none':
    #     return render_template('login.html', name=detected_face)

   
    

@app.route('/<id>/Register/', methods=['POST','GET'])
def login(id):
    if request.method=='POST':
        try:
            key= secrets.token_urlsafe(16)

            user={"name": request.form['name'],
            "password": request.form['password'],
            "email": request.form['email'],
            "api_key": key,
            "company_id": id
            }

            path = os.path.join("./known_users", key)
            os.mkdir(path)
            dbRes = db.users.insert_one(user)
            return Response(
                response=json.dumps(
                    {"message": "User created successfully", "id": f"{dbRes.inserted_id}"}
                ),
                status=200,
                mimetype="application/json"
            )
        except Exception as e:
            return(str(e))
    if request.method=='GET':
        try:
            data = list(db.users.find())
            cmp = list(db.users.find({},{"_id": 0 ,"company_id" : 1}))
            #if cmp does not exist in the db
            print('\n\n',cmp[0]['company_id'],'\n\n')
            # if len(cmp)!=0:
            #if cmp equals to the id
            if cmp[0]['company_id']==id:
                print(data, "here")
                return Response(str(data), status=200, mimetype="application/json")
                # return render_template("login.html")
            else:
                throw = "No user found"
                return Response(str(throw), status=200, mimetype="application/json")

        except Exception as e:
            return(str(e))


@app.route('/<id>/login/', methods=['POST','GET'])
def register(id):
    if request.method=='POST':
        data = {"name": request.form['name'],
            "password": request.form['password'],
            "email": request.form['email'],
            }

        try:
            print(list(db.users.find({},{"_id": 0 ,"company_id" : 1}))[0]['company_id'])
            if db.users.find_one(data) and list(db.users.find({},{"_id": 0 ,"company_id" : 1}))[0]['company_id'] == id:
                return Response(
                    response=json.dumps(
                        {"message": "User found successfully", "id": f"{db.users.find_one(data)['_id']}"}
                    ),
                    status=200,
                    mimetype="application/json"
                )
            else:
                return Response(
                    response=json.dumps(
                        {"message": "User not found"}
                    ),
                    status=200,
                    mimetype="application/json"
                )
        except Exception as e:
            return(str(e))
    if request.method=='GET':
        try:
            data = list(db.users.find())
            print(data)
            return Response(str(data), status=200, mimetype="application/json")
        except Exception as e:
            return(str(e))

@app.route('/creg', methods=['POST','GET'])
def clogin():
    if request.method=='POST':
        try:
            key = secrets.token_urlsafe(8)
            company={"cname": request.form['cname'],
            "cpassword": request.form['cpassword'],
            "cemail": request.form['cemail'],
            "capi_key": key
            }

            dbRes = db.company.insert_one(company)
            return Response(
                response=json.dumps(
                    {"message": "User created successfully", "id": f"{dbRes.inserted_id}"}
                ),
                status=200,
                mimetype="application/json"
            )
        except Exception as e:
            return(str(e))
    if request.method=='GET':
        try:
            data = list(db.company.find())
            print(data)
            return Response(str(data), status=200, mimetype="application/json")
            #return response(data, status=200, mimetype="application/json")

        except Exception as e:
            return(str(e))

@app.route('/clogin', methods=['POST','GET'])
def cregister():
    if request.method=='POST':

        data = {
            "cpassword": request.form['cpassword'],
            "cemail": request.form['cemail']
        }
        try:
            if(db.company.find_one(data)):
                return Response(
                    response=json.dumps(
                        {"message": "User found successfully"}
                    ),
                    status=200,
                    mimetype="application/json"
                )
            else:
                return Response(
                    response=json.dumps(
                        {"message": "User not found"}
                    ),
                    status=200,
                    mimetype="application/json"
                )
        except Exception as e:
            return(str(e))

    if request.method=='GET':
        try:
            data = list(db.company.find())
            print(data)
            return Response(str(data), status=200, mimetype="application/json")
        except Exception as e:
            return(str(e))
    

if __name__ == '__main__':
    app.run(debug=True)