import socketio
import eventlet
import eventlet.wsgi
import time
from flask import Flask, render_template
from flask import request
import requests
import json
import pandas
from sklearn import cross_validation
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib
import pickle
from datetime import date
import math
import urllib2
import time
from datetime import date
import math

loaded_model = pickle.load(open('/Users/hongyili/Desktop/big_Data_final/finalized_model.sav', 'rb')) #load model to predict density in certain time
sio = socketio.Server()
app = Flask(__name__)


def calculateCost(originLat,originLon,destLat,destLon):
	print originLat,originLon,destLat,destLon	
	param = str(originLat) + ',' + str(originLon) + '&destinations=' + str(destLat) + ',' + str(destLon)
	url ='https://maps.googleapis.com/maps/api/distancematrix/json?origins=' + param + '&mode=car&language=en'
	response = json.loads(urllib2.urlopen(url).read())
	element = response['rows'][0]['elements'][0]
	distance = element['distance']['text'] #in km
	duration = element['duration']['text'] #in min
	index1 = distance.find(" ")
	index2 = duration.find(" ")
	distance = distance[0 : index1]
	duration = duration[0 : index2]
	cost = 3.4056 + 2.0798 * 0.621371 * float(distance) + 0.43104 * float(duration) #this model was well trained and achieved accuracy above 95%
	return cost

def getGeo(street):
	param = street.replace(" ", "+")
	url ='https://maps.googleapis.com/maps/api/geocode/json?address=' + param + ",+NY"
	response = json.loads(urllib2.urlopen(url).read())
	result = response['results'][0]
	geometry = result['geometry']['location']
	lat = geometry['lat']
	lng = geometry['lng']
	result = []
	result += [lat]	
	result += [lng]
	return result
	
@sio.on('getCost')
def getCost(sid, param):
	departure = param['start']
	destination = param['destination']
	responDep = getGeo(departure)
	responDes = getGeo(destination)

	cost = calculateCost(responDep[0], responDep[1], responDes[0], responDes[1])
	sio.emit('respCost', cost)

@sio.on('getRecommend')
def getRecommend(sid, param):
	start = param[0]
	end = param[1]
	hours = param[2]
	result = []
	t = time.strftime("%H:%M:%S")
	curr_time_list = [int(t) for t in t.split(':')]
	for i in range(0, hours + 1):
		result += [curr_time_list[0] + i, predictDensity(street,end, i)]

	print result
	sio.emit('respDen', result)

def transormDate(date_str):
	print date_str
	minutes_per_bin = 30
	d = date_str.split()
	time_list = [int(t) for t in d[1].split(':')]
	num_minutes = time_list[0] * 60 + time_list[1]
	time_bin = num_minutes / minutes_per_bin
	hour_bin = num_minutes / 60
	min_bin = (time_bin * minutes_per_bin) % 60
	time_num = (hour_bin * 60 + min_bin + minutes_per_bin / 2.0)/(60*24)
	time_cos = math.cos(time_num * 2 * math.pi)
	time_sin = math.sin(time_num * 2 * math.pi)
	date_list = d[0].split('-')
	d_obj = date(int(date_list[0]), int(date_list[1]), int(date_list[2]))
   	day_of_week = d_obj.weekday()
   	day_num = (day_of_week + time_num) / 7.0
   	day_cos = math.cos(day_num * 2 * math.pi)
   	day_sin = math.sin(day_num * 2 * math.pi)
   	weekend = 0
   	if day_of_week in [5,6]:
   		weekend = 1
   	result = []
   	result += [time_num] + [time_cos] + [time_sin] + [day_num] + [day_cos] + [day_sin] + [weekend]
   	return result


def predictDensity(street, end, hour):
	latlon = getGeo(street)
	t = time.strftime("%H:%M:%S")
	curr_time_list = [int(t) for t in t.split(':')]
	afhour = curr_time_list[0] + hour
	currTime = str(afhour) + ":" + str(curr_time_list[1]) + ":" + str(curr_time_list[2])
	now = '2016-12-22 ' + currTime
	getDate = transormDate(now)
	time_list = [int(t) for t in currTime.split(':')]
	index = int((time_list[0] * 60 + time_list[1]) / 30)
	timeslot = []
	for i in range(1, index):
		timeslot += [0]
	timeslot += [1]
	for i in range(index + 1, 49):
		timeslot += [0]
	week = []
	week += [0] + [0] + [0] + [1] + [0] + [0] + [0] 	
	data = 	getDate + latlon + timeslot + week
	return loaded_model.predict(data)

@app.route("/")
def starter():
    return render_template('index.html')
@app.route("/cost")
def cost():
    return render_template('costPredic.html')
@app.route("/hotmap")
def hotmap():
    return render_template('hotmap.html')
@app.route("/recommend")
def recommend():
    return render_template('recommend.html')
 
if __name__ == "__main__":
	
    app = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('', 8080)), app)



