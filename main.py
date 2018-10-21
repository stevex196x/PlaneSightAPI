
# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START app]
import logging

from flask import Flask, jsonify, request
import requests
import json
import config

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)


# [START metadata]
METADATA_NETWORK_INTERFACE_URL = \
    ('http://metadata/computeMetadata/v1/instance/network-interfaces/0/'
     'access-configs/0/external-ip')


def get_external_ip():
    """Gets the instance's external IP address from the Compute Engine metadata
    server. If the metadata server is unavailable, it assumes that the
    application is running locally.
    """
    try:
        r = requests.get(
            METADATA_NETWORK_INTERFACE_URL,
            headers={'Metadata-Flavor': 'Google'},
            timeout=2)
        return r.text
    except requests.RequestException:
        logging.info('Metadata server could not be reached, assuming local.')
        return 'localhost'
# [END metadata]


@app.route('/')
def index():
    # Websocket connections must be made directly to this instance, so the
    # external IP address of this instance is needed.
    external_ip = get_external_ip()
    return 'External IP: {}'.format(external_ip)
# [END app]


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500

"""
 Query Parameters:
  lat
  lon
 Returns city and temperature in Kelvin
"""
@app.route('/weather')
def get_weather():
    try:
        arg_dict = request.args
        r = requests.get('http://api.openweathermap.org/data/2.5/weather?lat=' + arg_dict['lat'] + '&lon=' +
                         arg_dict['lon'] + '&APPID=' + config.weather_api_key)
        data = json.loads(r.text)
        temp = data['main']['temp']
        city = data['name']
        return jsonify(temp, city)
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
        arg_dict = request.args
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

@app.route('/wiki')
def get_wiki():
    try:
        arg_dict = request.args
        r = requests.get('https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles=' + arg_dict['title'])
        data = json.loads(r.text)
        page_id = next(iter(data['query']['pages']))
        return data['query']['pages'][page_id]['extract']
    except:
        raise Exception("Unable to fetch wiki page")



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
        arg_dict = request.args
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
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)