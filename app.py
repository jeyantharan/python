from crypt import methods
from heapq import merge
from this import d
from flask import Flask, jsonify, request, redirect,Response
from flask.helpers import url_for
from flask_pymongo import PyMongo
import json
import random
import ast
import datetime

app = Flask(__name__)
#app.config['MONGO_URI'] = 'mongodb+srv://Jeyanth:jeyanth2425@cluster0.hyf6v8i.mongodb.net/wasteManagement?retryWrites=true&w=majority'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/wasteManagement'
mongo = PyMongo(app)


#roads filtered by place
@app.route('/<placeName>', methods = ['GET'])
def retrieveAll(placeName):
    holder = list()
    print(placeName)
    currentCollection = mongo.db.place
    detail = currentCollection.find_one({"placeName":placeName})
    # for i in detail:
    #     holder.append(i["road"])
    # road = detail['road']
    # print(road)
    return jsonify({"road":detail["road"]})

#genarate time table
@app.route('/table/random/<mainPlace>', methods = ['GET'])
def genarateTimetable(mainPlace):
    mainHolder = list()
    empCollection = mongo.db.employee
    truckCollection = mongo.db.vehicle
    placeCollection = mongo.db.place

    place = placeCollection.find_one({"placeName":mainPlace})
    road = place["road"]
    #count = currentCollection.count()
    
    # for i in de:
        #  holder.append({'Employee Name':i["Employee Name"],'Employee ID':i["Employee ID"],'Area':i["Area"]})
    # print(holder)
    for x in range(0,7):
        holder = list()
        emp = list()
        extraEmployee = empCollection.aggregate([ { "$sample": { "size": 2 } } ])
        for n in extraEmployee:
            emp.append({"Employee Name":n["Employee Name"],"Employee ID":n["Employee ID"],"Area":n["Area"]})
        for y in range(0,5):
            holder1 = list()
            employee = empCollection.aggregate([ { "$sample": { "size": 4 } } ])
            
            t = 0
            for i in employee:
                truck = truckCollection.aggregate([ { "$sample": { "size": 1 } } ])
                for l in truck:
                    randRoad = random.choice(road)
                    the1 = str(i|l|randRoad)
                    the = ast.literal_eval(the1)
                    
                    
                    holder1.append({"Employee Name":the["Employee Name"],"Employee ID":the["Employee ID"],"EmployeeArea":the["Area"],"Driver's Name":the["Driver's Name"],"Tuck Number":the["Tuck Number"],"Road":the["name"]})
            time = ["06.00 AM - 09.00 AM","09.00 AM - 01.00 PM","01.00 PM - 04.00 PM","04.00 PM - 06.00 PM","06.00 PM - 09.00 PM",]
            subDic = {
                time[y]:holder1
            }
            holder.append(subDic)
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday","Sunday"];
            mainDic = {
                days[x]:holder,
                "Extra Employee":emp
            }
        mainHolder.append(mainDic)
        #     holder.append({'Employee Name':i["Employee Name"],'Employee ID':i["Employee ID"],'Area':i["Area"]})
        # holder.append({"6.00am - 9.00am":{'truck':truck[0]}})
        
    table = {"Place":mainPlace,"timeTable":mainHolder}
    currentCollection = mongo.db.timeTable
    currentCollection.insert_one(table)
    return jsonify(mainHolder)


#get time table
@app.route('/time-table/<mainPlace>', methods = ['GET'])
def getTable(mainPlace):
    holder = list()
    currentCollection = mongo.db.timeTable
    detail = currentCollection.find({"Place":mainPlace})
    #print(len(detail))
    for i in detail:
        holder.append({"place":i["Place"],'timeTable':i["timeTable"]})
    print(len(holder))
    return (holder[len(holder)-1])



#employee request leave
@app.route('/request/leave', methods = ['POST'])
def requastLeave():
    try:
        leave = {"Employee ID":request.form["empId"],"Name":request.form["name"],"Reason":request.form["reason"],"Date":int(request.form["date"]),"Accepeted":False}
        currentCollection = mongo.db.leave
        res = currentCollection.insert_one(leave)
        print(res.inserted_id)
        return Response(
            response=json.dumps(
                {"mes":"leave request send"}),
            status=200,
            mimetype="application/json"
        )
    except Exception as ex:
        print(ex)


# admin accept or reject leave
@app.route('/leave-state/<empId>/<date>', methods = ['PATCH'])
def changeLeaveState(empId,date):
    try:
        holder = list()
        currentCollection = mongo.db.leave
        res = currentCollection.update_one({"Employee ID":empId,"Date":int(date)},{"$set":{"Accepeted":True}})

        return Response(
            response=json.dumps(
                {"mes":"state updated"}),
            status=200,
            mimetype="application/json"
        )
    except Exception as ex:
        print(ex)

#vehicle problem
@app.route('/vehicle/post-vehicle-monitoring',methods=["POST"])
def post_vehicle_monitoring_data():
    
    vehichle_number = request.form['vehichle_number']
    reporter_name = request.form['reporter_name']
    rep_emp_name = request.form['rep_emp_name']
    problem = request.form['problem']

    vehicle_monitoring = {
                      "vehichle_number" : vehichle_number,
                      "reporter_name" : reporter_name,
                      "rep_emp_name" : rep_emp_name,
                      "problem" : problem,
                      "state":False
    }
                      
    
    currentCollection = mongo.db.vehicle_monitoring
    res = currentCollection.insert_one(vehicle_monitoring)
    return Response(
            response=json.dumps(
                {"mes":"vehicle issue request send"}),
            status=200,
            mimetype="application/json"
        )


# admin verify the vehicle
@app.route('/verify-state/<vehicleId>/', methods = ['PATCH'])
def changeVehicleState(vehicleId):
    try:
        holder = list()
        currentCollection = mongo.db.vehicle_monitoring
        res = currentCollection.update_one({"vehichle_number":vehicleId},{"$set":{"state":True}})
        currentCollection1 = mongo.db.vehicle
        currentCollection1.delete_one({'Tuck Number' : vehicleId})

        return Response(
            response=json.dumps(
                {"mes":"state updated"}),
            status=200,
            mimetype="application/json"
        )
    except Exception as ex:
        print(ex)

@app.route('/post-carbage-collection',methods=["POST"])
def post_carbage_collection_data():
    Addresss = request.form['Addresss']
    Request_date = request.form['Request_date']
    Email_address = request.form['Email_address']
    Carbage_type = request.form['Carbage_type']
    Quantity = request.form['Quantity']
    Additional_information = request.form['Additional_information']
    holder = list()
    truckCollection = mongo.db.vehicle
    truck = truckCollection.aggregate([ { "$sample": { "size": 1 } } ])
    global truckId;
    for i in truck:
        truckId = i["Tuck Number"]
    carbage_collection = {
                      "Addresss":Addresss,
                      "Request_date":Request_date,
                      "Email_address":Email_address,
                      "Carbage_type":Carbage_type,
                      "Quantity" : Quantity,
                      "Additional_information" : Additional_information,
                      "TruckId":truckId
    }
    currentCollection = mongo.db.carbage_collection
    res = currentCollection.insert_one(carbage_collection)
    return Response(
            response=json.dumps(
                {"mes":"carbage_collection request send"}),
            status=200,
            mimetype="application/json"
        )
    


#get time table
@app.route('/getCarbageTable', methods = ['GET'])
def getCarbageTable():
    holder = list()
    currentCollection = mongo.db.carbage_collection
    detail = currentCollection.find({})
    for i in detail:
        holder.append({'Addresss':i["Addresss"],'Carbage_type':i["Carbage_type"],'Quantity':i["Quantity"],'Request_date':i["Request_date"],'TruckId':i["TruckId"]})
    
    return jsonify(holder)



#allocate event to truck
@app.route('/allocate/evant/genarate',methods = ['GET'])
def genarateEvent():
    holder = list()
    currentCollection = mongo.db.event
    truckCollection = mongo.db.vehicle
    newCollection = mongo.db.eventTruck
    details = currentCollection.find({})
    for i in details:
        truck = truckCollection.aggregate([ { "$sample": { "size": 1 } } ])
        for x in truck:
            obj = {
                "TruckId":x["Tuck Number"]
            }
            print(i)
            holder.append({"Event Name":i["Event Name"],"Event Date ":i["Event Date "],"Location":i[" Location"],"Tuck Number":obj["TruckId"]})

    table = {
        "event":holder
    }
    newCollection.insert_one(table)
    return jsonify(holder)

#get time table event
@app.route('/time-table/event/truck', methods = ['GET'])
def getEventTable():
    holder = list()
    currentCollection = mongo.db.eventTruck
    detail = currentCollection.find()
    #print(len(detail))
    for i in detail:
        holder.append({"event":i["event"]})
    print(len(holder))
    return ((holder[len(holder)-1])["event"])


#add feadback
@app.route('/feedback',methods=["POST"])
def post_feedback():
    Name = request.form['Name']
    Main_Area = request.form['Main Area']
    Lane = request.form['Lane']
    Feedback = request.form['Feedback']
    Feedback_Type  = request.form['Feedback Type']
    Rating = request.form['Rating']

    feedback = {
                      "Name" : Name,
                      "Main Area" : Main_Area,
                      "Lane" : Lane,
                      "Feedback" : Feedback,
                      "Feedback Type " : Feedback_Type,
                      "Rating":Rating
    }
                      
    
    currentCollection = mongo.db.feedback
    print(feedback)
    res = currentCollection.insert_one(feedback)
    return Response(
            response=json.dumps(
                {"mes":"feedback added....."}),
            status=200,
            mimetype="application/json"
        )

#get all feedback
@app.route('/feedback', methods = ['GET'])
def getAllFeedback():
    holder = list()
    currentCollection = mongo.db.feedback
    detail = currentCollection.find()
    for i in detail:
        holder.append({"Name":i["Name"],"Main Area":i["Main Area"],"Lane":i["Lane"],"Feedback":i["Feedback"],"Feedback Type":i["Feedback Type "],"Rating":i["Rating"]})
    return (holder)

#get all feedback by main place
@app.route('/feedback/<mainPlace>', methods = ['GET'])
def getAllPlaceFeedback(mainPlace):
    holder = list()
    currentCollection = mongo.db.feedback
    detail = currentCollection.find({"Main Area":mainPlace})
    for i in detail:
        holder.append({"Name":i["Name"],"Main Area":i["Main Area"],"Lane":i["Lane"],"Feedback":i["Feedback"],"Feedback Type":i["Feedback Type "],"Rating":i["Rating"]})
    return (holder)

@app.route('/percentage/feedback/', methods = ['GET'])
def getAllPlaceFeedbackPercentage():
    holder = list()
    currentCollection = mongo.db.feedback
    data = currentCollection.aggregate([{"$group" : { "_id" : "$Main Area", "Data": { "$push": "$$ROOT" } }}])
    for i in data:
        num = 0
        holder1 = list()
        fullCount = len(i["Data"])
        for x in i["Data"]:
            print(x)
            if x["Feedback Type "] == "Positive":
                num = num+1
        positive = ((num/fullCount)*100)
        negative = 100 - positive
        holder.append({"Place":i["_id"],"Negative":negative,"Positive":positive})
    return (holder)




if __name__ == '__main__':
    app.run(debug = True)