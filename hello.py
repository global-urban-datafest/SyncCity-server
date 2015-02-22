#! /usr/bin/env python3

import os
import sys
import flask
import math
import json
from flask import Flask, Response, request, g
from torndb import Connection
from flask.ext.restful import inputs

from tsp_greedy import solve_tsp
import db_config, data_config

app = Flask(__name__)

# Global state of the server, this is not thread safe
#smart_data = 'real' # 'fake_rainy', 'fake_sunny'
#smart_data = 'fake_rainy' # 'fake_rainy', 'fake_sunny'
smart_data = 'fake_sunny' # 'fake_rainy', 'fake_sunny'
verbose = True

# Local functions
#-------------------------------------------------------------------------------
def help_usage():
    return """\
GET /api_user/route?username=john&date=YYYY-mm-dd&time={all_day, morning, afternoon}&city=Barcelona
GET /api_admin/smart_data
PUT /api_admin/smart_data?source={real, fake_rainy, fake_sunny}
GET /api_admin/verbose
PUT /api_admin/verbose?val={true, false}
"""

def resp_plain(resp):
    return Response(resp, mimetype='text/plain; charset=utf-8')

def resp_json(resp, status):
    js = json.dumps(resp, ensure_ascii=False)
    return Response(js, status=status, mimetype='application/json; charset=utf-8')

def get_city_points(city):
    points = g.db.query("select * from points where city=%s", city)
    return points

def get_user_params(username):
    user_params = g.db.query("select * from users where username=%s", username)
    if user_params != []:
        user_params = user_params[0]
    return user_params

def norm_param(param, val, min_max):
    if val == None:
        return 0
    min = min_max[0]
    max = min_max[1]
    v = (val - data_config.min[param]) / (data_config.max[param] - data_config.min[param])
    return v * (max - min) + min

def req_sensor(coord, sens, radius):
    global smart_data
    if smart_data == 'fake_rainy':
        if sens == 'wind':
            return 50.0
        if sens == 'temp':
            return 20.0
        if sens == 'humidity':
            return 0.86
        if sens == 'pluviometer':
            return 12
        if sens == 'noise':
            return None
    if smart_data == 'fake_sunny':
        if sens == 'wind':
            return 6.0
        if sens == 'temp':
            return 27.0
        if sens == 'humidity':
            return 0.7
        if sens == 'pluviometer':
            return 0
        if sens == 'noise':
            return None
    if smart_data == 'real':
        pass

def req_forecast(coord, sens):
    if smart_data == 'fake_rainy':
        if sens == 'wind':
            return 54.0
        if sens == 'temp':
            return 18.5
        if sens == 'humidity':
            return 0.85
        if sens == 'p_rain':
            return 0.9
    if smart_data == 'fake_sunny':
        if sens == 'wind':
            return 7.0
        if sens == 'temp':
            return 26.0
        if sens == 'humidity':
            return 0.71
        if sens == 'p_rain':
            return 0.0
    if smart_data == 'real':
        pass

def rank_point(point, user, sensor, forecast):
    # Merge sensor and forecast data
    weather = { 'wind': 0, 'temp': 0, 'humidity': 0 }
    for p in weather:
        weather[p] =\
            0.3 * norm_param(p, sensor[p], (-1, 1)) +\
            0.7 * norm_param(p, forecast[p], (-1, 1))
    weather['rain'] =\
        0.3 * norm_param('pluviometer', sensor['pluviometer'], (-1, 1)) +\
        0.7 * norm_param('p_rain', forecast['p_rain'], (-1, 1))


    #if verbose:
    #    print(weather)
    #    print()

    # Merge user and sensor/weather data into semantic categories
    rank = {}
    rank['outdoor'] = -50 * weather['wind'] + 40 * weather['temp'] -\
        25 * weather['humidity'] - 200 * weather['rain'] + 10 * user['outdoor']
    rank['free'] = 10 * user['free']
    rank['crowded'] = 5 * norm_param('noise', sensor['noise'], (-1, 1)) +\
        10 * user['crowded']
    rank['traditional'] = 10 * user['traditional']

    # Normalization
    rank['outdoor'] /= 55
    rank['free'] /= 10
    rank['crowded'] /= 15
    rank['traditional'] /= 10

    # Cross data with point parameters
    for c in rank:
        rank[c] *= point[c]

    # Add point rating
    rank['rating'] = 5 * point['rating']

    # Compute final ranking
    r = 0
    for c in rank:
        r += rank[c]

    return r

def dist(n1, n2):
    return math.sqrt((n1[0] - n2[0])**2 + (n1[1] - n2[1])**2)

def gen_mat(ns):
    m = []
    for i in range(len(ns)):
        m.append([])
        for j in range(len(ns)):
            m[i].append(dist(ns[i], ns[j]))
    return m

def route(coords):
    m = gen_mat(coords)
    p = solve_tsp(m)
    return p

# sensors is a pair of sensor names and tolerance radius
# coord is a pair of longitude and latitude
def req_sensor_data(coord, sensors):
    res = {}
    for (sens, radius) in sensors:
        res[sens] = req_sensor(coord, sens, radius)

    return res

# params is the names of values we want to get
# coord is a pair of longitude and latitude
def req_forecast_data(coord, params):
    res = {}
    for param in params:
        res[param] = req_forecast(coord, param)

    return res

# Database connection
#-------------------------------------------------------------------------------
@app.before_request
def connect_db():
    g.db = Connection(db_config.DB_HOST,
                      db_config.DB_NAME,
                      db_config.DB_USER,
                      db_config.DB_PASSWD)

@app.after_request
def close_connection(response):
    g.db.close()
    return response

@app.route('/')
def index():
    return resp_plain(help_usage())

# API routes
#-------------------------------------------------------------------------------
@app.route('/api_admin/smart_data', methods = ['PUT', 'GET'])
def api_admin_smart_data():
    global smart_data
    if request.method == 'PUT' or 'source' in request.args:
        val = request.args['source']
        if val == 'real':
            smart_data = 'real'
        elif val == 'fake_rainy':
            smart_data = 'fake_rainy'
        elif val == 'fake_sunny':
            smart_data = 'fake_sunny'
        return resp_plain("OK\n")

    elif request.method == 'GET':
        resp = "Smart data source: " + smart_data + "\n"
        return resp_plain(resp)

@app.route('/api_admin/verbose', methods = ['PUT', 'GET'])
def api_verbose_data():
    global verbose
    if request.method == 'PUT':
        val = request.args['val']
        if val == 'true':
            verbose = True
        elif val == 'false':
            verbose = False
        return resp_plain("OK\n")

    elif request.method == 'GET':
        resp = "Verbose: " + str(verbose) + "\n"
        return resp_plain(resp)

@app.route('/api_user/route')
def api_user_route():
    # Parsing input arguments
    username = request.args['username']
    date = request.args['date']
    time = request.args['time']
    city = request.args['city']

    date = flask.ext.restful.inputs.date(date)

    # Sensor names and radius acceptance
    sens_conf = [('wind', 1000), ('temp', 1000), ('humidity', 1000),
            ('pluviometer', 1000), ('noise', 200)]
    fore_param = ['wind', 'temp', 'humidity', 'p_rain']

    user_params = get_user_params(username)
    if user_params == []:
        return resp_json({'status': 'error', 'error': "No such username"}, 400)
    city_points = get_city_points(city)
    if city_points == []:
        return resp_json({'status': 'error', 'error': "No such city"}, 400)

    for point in city_points:
        coord = (point['longitude'], point['latitude'])
        sensors = req_sensor_data(coord, sens_conf)
        forecast = req_forecast_data(coord, fore_param)
        point['rank'] = rank_point(point, user_params, sensors, forecast)

    num_points = 5
    if time == 'all_day':
        num_points = 10

    points = []
    coords = []
    res_str = ""
    for point in sorted(city_points, key=lambda k: k['rank'], reverse=True):
        points.append(point)
        coords.append((float(point['longitude']), float(point['latitude'])))
        res_str += str(point) + "\n"
        if len(points) >= num_points:
            break

    order = route(coords)
    for i in order:
        points[i]['num'] = i

    #return 'NOT YET IMPLEMENTED'
    if verbose:
        print(res_str)

    return resp_json({'status': 'ok', 'points': points}, 200)
    #return resp_plain(res)

@app.route('/db_test')
def db_test():
    points = g.db.query("select * from points where city=%s", "barcelona")
    return resp_plain(str(points[1:]))

#-------------------------------------------------------------------------------
port = os.getenv('VCAP_APP_PORT', '5000')
if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=int(port))
