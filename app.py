from flask import Flask, jsonify, request
import requests
import json
import config

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


"""
 Query Parameters:
  lat
  lon
 Returns city and temperature in Kelvin
"""
@app.route('/weather')
def get_weather():
    try:
        arg_dict = jsonify(request.args.lists())
        r = requests.get('api.openweathermap.org/data/2.5/weather?lat=' + arg_dict['lat'] + '&lon=' +
                         arg_dict['lon'] + '&APPID=' + config.weather_api_key)
        data = json.loads(r.text)
        temp = data['main']['temp']
        city = data['name']
        return temp, city
    except:
        raise Exception("Unable to get current weather information")


"""
 Query Parameters:
  lat
  lon
 Returns the closest landmarks nearby the current latitude and longitude
"""
@app.route('/fact')
def get_landmark():
    try:
        arg_dict = jsonify(request.args.lists())
        r = requests.get(
            'https://reverse.geocoder.api.here.com/6.2/reversegeocode.json?app_id=' + config.landmark_app_id +
            '&app_code=-' + config.landmark_app_code +
            '&mode=retrieveLandmarks&prox=' + arg_dict['lat'] + ',' + arg_dict['lon'] + ',1000')
        data = json.loads(r.text)

        result = data['Response']['View'][0]['Result']
        li = []
        for i in range(len(result)):
            li.append(result[i]['Location']['Name'])
    except:
        return "No landmarks found :'("

    return jsonify(li)


"""
Query Paramaters:
 departCode
 arriveCode
 flightCode
 flightNum
"""
@app.route('/info')
def get_flight_info():
    try:
        arg_dict = jsonify(request.args.lists())
        r = requests.get('http://aviation-edge.com/v2/public/flights?key=' + config.flight_key + '&depIata=' +
                         arg_dict['departCode'] + '&arrIata=' + arg_dict['arriveCode'] + '&flightNum=' +
                         arg_dict['flightNum'] + '&airlineIata=' + arg_dict['flightCode'] + '&limit=1')
        data = json.loads(r.text)
        latitude = data[0]["geography"]["latitude"]
        longitude = data[0]["geography"]["longitude"]
        altitude = data[0]["geography"]["altitude"]
        speed = data[0]["speed"]["horizontal"]
        return jsonify(latitude, longitude, altitude, speed)
    except:
        raise Exception("Can't find location :(")


@app.route('/airports')
def get_airports():
    try:
        r = requests.get(config.heroku_server)
        data = json.loads(r.text)

        li = []
        for key in data:
            # print(str(key['name']) + ' ' + str(key['code']))
            li.append(str(key['code']) + ' - ' + str(key['name']))
        return jsonify(li)
    except:
        raise Exception("Can't get list of airports :'(")


if __name__ == '__main__':
    app.run()
