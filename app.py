from importlib.resources import path
from flask import Flask,redirect, url_for, request , Response
import pymongo
from flask_pymongo import PyMongo
import json
import secrets
import os


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

@app.route('/')
def hello_world():
    return secrets.token_urlsafe(16)

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method=='POST':
        try:
            key= secrets.token_urlsafe(16)

            user={"name": request.form['name'],
            "password": request.form['password'],
            "email": request.form['email'],
            "api_key": key
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
    else:
        try:
            data = list(db.users.find())
            print(data)
            return Response(str(data), status=200, mimetype="application/json")

        except Exception as e:
            return(str(e))

if __name__ == '__main__':
    app.run(debug=True)