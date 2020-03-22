#!/usr/bin/env python
# coding: utf-8

from flask import Flask, jsonify, Response
from flask_pymongo import PyMongo
import json
from bson import ObjectId
from bson.json_util import dumps

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
mongo = PyMongo(app, uri="mongodb://localhost:27017/mydb")

gender_map = {"M":"男", "F":"女", "B":"男女"}
city_map = {"T":"台北市", "NT":"新北市"}

# mongodb query result to json
def getResultJson(myQuery):
    arr = []
    rent = mongo.db.rent.find(myQuery, {"_id" : 0})
    for x in rent:
        arr.append(json.loads(dumps(x)))
        
    if arr == []:
        return "Nothing return, please change the query conditions!"
    else:
        return jsonify(arr)


# restful api
@app.route('/api/all', methods=['GET'])
def getAllData():
    myQuery = {}
    return getResultJson(myQuery)

@app.route('/api/<string:city>/<string:gender>', methods=['GET'])
def getRentData(city, gender):
    myQuery = { 
        "city" : city_map.get(city, ""),
        "性別要求": { "$regex": ("[%s]" % gender_map.get(gender, "") ) }
    }
    return getResultJson(myQuery)

@app.route('/api/phone/<string:number>', methods=['GET'])
def getPhoneData(number):
    myQuery = { 
        "phone": { "$regex": ("(%s)" % number ) }
    }
    return getResultJson(myQuery)

@app.route('/api/agent', methods=['GET'])
def getAgentData():
    myQuery = {
        "identity" : { "$not" : { "$regex": ("(屋主)") } }
    }     
    return getResultJson(myQuery)

@app.route('/api/owner/<string:city>/<string:gender>/<string:name>', methods=['GET'])
def getOwnerData(city, gender, name):
    if gender=="UN":
        gender = "unknown"
    
    myQuery = {
        "identity" : { "$regex": ("(屋主)") },
        "city" : city_map.get(city, ""),
        "gender" : gender,
        "owner": { "$regex": ("[%s]" % name ) }
    }
    return getResultJson(myQuery)

app.run(host='127.0.0.1', port=8080)

