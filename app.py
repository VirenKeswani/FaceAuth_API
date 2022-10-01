from asyncio.windows_events import NULL
from importlib.resources import path
from urllib import response
from flask import Flask,redirect, url_for, request , Response , render_template , g, url_for
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

        data = {"cname": request.form['cname'],
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