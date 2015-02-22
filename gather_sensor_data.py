#! /usr/bin/env python3
import urllib.request
import os

import json

import geopy
from geopy.distance import VincentyDistance


def get_data(latitude,longitude,parameter,distance):
	url = 'http://icity-gw.icityproject.com:8080/developer/api/devices/'
	apikey = '?apikey=l7xxe1d39a7eac524bd2b709c55002d702e2'
	params = '&cityID=7'

	response = urllib.request.urlopen(url + apikey + params).read()
	if response:
		res = json.loads(response.decode())

		param = "urn:" + parameter

		origin = geopy.Point(latitude, longitude)
		destination = VincentyDistance(distance).destination(origin, 0)
		latdif = destination.latitude - latitude
		destination = VincentyDistance(distance).destination(origin, 90)
		londif = destination.longitude - longitude

		url = 'http://icity-gw.icityproject.com:8080/developer/api/observations/last/'
		sensors = []
		#Barcelona parsing--------------------------------------------
		#latitude: 41.3477244-41.4536057, longitude: 2.0980604-2.2252299
		i = 0
		for i in range(len(res)):
			if(float(res[i]["latitude"]) > 41.3477244 and float(res[i]["latitude"]) < 41.4536057 and float(res[i]["longitude"]) > 2.0980604 and float(res[i]["longitude"]) < 2.2252299):
				if(float(res[i]["latitude"]) > latitude-latdif and float(res[i]["latitude"]) < latitude+latdif and float(res[i]["longitude"]) > longitude-londif and float(res[i]["longitude"]) < longitude+londif):
					if(param in res[i]["properties"]):
						params = "&id="+ res[i]["deviceID"] + "&property=" + param + "&n=1"
						response = urllib.request.urlopen(url + apikey + params).read()
						if response:
							result = json.loads(response.decode())
							#Sensors without units...
							if result[0]["units"]:		
								sensors.append(result[0])
								print(result[0]["value"],result[0]["units"])

		print(sensors)



if __name__ == "__main__":

		#parameters -> people_flowCO, NO2, battery, humidity, light, nets, noise, panel, temperature
        get_data(41.3844879,2.1662453,"temperature",0.5)


