from datetime import datetime
from time import strftime
from flask import Flask
from dotenv import dotenv_values
import pickle
from datetime import datetime
import datetime as dt
import requests
import numpy as np


# from flask_restful import Api, Resource
from flask_cors import CORS


config = dotenv_values(".env")
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

apiList = {
    'api-list': [
        'api/data',
        'api/predict/hour <predict one hour>',
        'api/predict/day <predict one day>',
        'api/predict/week <predict one week>',
    ]
}


def req():
    r = requests.get(
        config['URL']+'last?device_token='+config['DEVICE_6'])
    r = r.json()
    return r


def getData(x):
    pt, datetime = [], []
    for i in range(0, x):
        r = requests.get(
            config['URL']+'pull?device_token='+config['DEVICE_6']+f'&page={i}')
        r = r.json()
        for j in r['data']:
            pt.append(j['pt'])
            datetime.append(j['time'] + ' ' + j['date'])
    data = {
        "pt": pt,
        'datetime': datetime
    }
    return data


# print(getData(144)['pt'])
def movingAverageData(x, y):
    xx = []
    for j in range(0, len(y), x):
        _y = []
        if j+x > len(y):
            break
        for i in range(j, j+x):
            _y.append(float(y[i]))
        _x = np.average(_y)
        xx.append(_x)
    return xx


def getAverageDatetime(interval, date):
    for i in range(len(date)):
        try:
            datetime.strftime(date[i], '%H:%M:%S %Y-%m-%d')
        except:
            try:
                x = datetime.strptime(
                    date[i-1], '%H:%M:%S %Y-%m-%d')+dt.timedelta(minutes=20)
                date[i] = x.strftime('%H:%M:%S %Y-%m-%d')
            except:
                x = datetime.strptime(
                    date[i+1], '%H:%M:%S %Y-%m-%d')-dt.timedelta(minutes=20)
                date[i] = x.strftime('%H:%M:%S %Y-%m-%d')
    if interval == 'hour':
        _date = []
        for i in range(len(date)):
            if i+1 > len(date)-1:
                break
            date_object_1 = datetime.strptime(date[i], '%H:%M:%S %Y-%m-%d')
            date_object_2 = datetime.strptime(date[i+1], '%H:%M:%S %Y-%m-%d')
            x = int(date_object_2.strftime('%H'))
            _x = int(date_object_1.strftime('%H'))
            y = x - _x
            if y:
                _date.append(date_object_2.strftime('%H:%M:%S %Y-%m-%d'))
        return _date
        # return date_object_1
    elif interval == 'day':
        _date = []
        for i in range(len(date)):
            if i+1 > len(date)-1:
                break
            date_object_1 = datetime.strptime(date[i], '%H:%M:%S %Y-%m-%d')
            date_object_2 = datetime.strptime(date[i+1], '%H:%M:%S %Y-%m-%d')
            x = int(date_object_2.strftime('%d'))
            _x = int(date_object_1.strftime('%d'))
            y = x - _x
            if y:
                _date.append(date_object_2.strftime('%H:%M:%S %Y-%m-%d'))
        return _date
    elif interval == 'week':
        pass
    else:
        return "Wrong interval"


@app.route("/", methods=['GET'])
def index():
    return apiList


@app.route('/predict', methods=['GET'])
def predict():
    return {
        'predict': ['/predict/hour', '/predict/day', '/predict/week']
    }


@app.route('/predict/hour', methods=['GET'])
def predictHour():
    data = getData(6)
    y = movingAverageData(3, data['pt'][::-1])
    x = getAverageDatetime('hour', data['datetime'][::-1])
    model = pickle.load(open('models/1Jam.sav', 'rb'))
    result = model.predict([y])
    _x = datetime.strptime(
        x[len(x)-1], '%H:%M:%S %Y-%m-%d') + dt.timedelta(hours=1)
    _x = _x.strftime('%H:%M:%S %Y-%m-%d')
    return {
        'data': {
            'pt': y,
            'datetime': x
        },
        'predict': {
            'pt': result[0],
            'datetime': _x
        }
    }


@app.route('/predict/day', methods=['GET'])
def predictDay():
    data = getData(42)
    y = movingAverageData(72, data['pt'][::-1])
    x = getAverageDatetime('day', data['datetime'][::-1])
    model = pickle.load(open('models/1Hari.sav', 'rb'))
    result = model.predict([y])
    _x = datetime.strptime(
        x[len(x)-1], '%H:%M:%S %Y-%m-%d') + dt.timedelta(days=1)
    _x = _x.strftime('%H:%M:%S %Y-%m-%d')
    return {
        'data': {
            'pt': y,
            'datetime': x
        },
        'predict': {
            'pt': result[0],
            'datetime': _x
        }
    }


@app.route('/predict/week', methods=['GET'])
def predictWeek():
    data = getData(84)
    x = movingAverageData(504, data['pt'][::-1])
    model = pickle.load(open('models/1Minggu.sav', 'rb'))
    result = model.predict([x])
    return {
        'data': {
            'pt': x,
            'datetime': [
                'Minggu Lalu',
                'Minggu Ini'
            ]
        },
        'predict': {
            'pt': result[0],
            'datetime': 'Minggu Depan'
        }
    }


@app.route('/data', methods=['GET'])
def data():
    r = req()
    pt = r['data']['pt']
    datetime = r['data']['time'] + ' ' + r['data']['date']
    data = {
        'data': {
            'pt': pt,
            'datetime': datetime
        }
    }
    # data = json.dumps(data)
    return data


@app.route('/data/day', methods=['GET'])
def dataDay():
    data = getData(12)
    pt = data['pt'][::-1]
    datetime = data['datetime'][::-1]
    return{
        'data': {
            'pt': pt,
            'datetime': datetime
        }
    }


if __name__ == "__main__":
    app.run()
