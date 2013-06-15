#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013 Alexandre Bulté <alexandre[at]bulte[dot]net>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from flask import Flask, request, render_template, jsonify
from gevent import monkey

import datetime
import json
import time

app = Flask(__name__)
app.debug = True

monkey.patch_all()

## DB STUFF ##
import sqlite3
from flask import g

DATABASE = '/home/fohring/development/raspiSensorApp/temperature.db'
#DATABASE_SALON = '../monitor_serial_git/salon.db'
#DATABASE_TOBACCO = '../monitor_serial_git/temps_w_tobacco.db'

def connect_db(database):
    return sqlite3.connect(database)

def query_db_orig(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

def date_from_timestamp(ts):
    mydate = datetime.datetime.fromtimestamp(ts)
    return mydate.strftime('%d/%m/%y - %H:%M')


def query_db(dbtouse, query, args=(), convert_date=True):
    db = connect_db(dbtouse)
    cur = db.execute(query, args)
    rv = []
    for row in cur.fetchall():
        new_row = []
        if convert_date:
            new_row.append(date_from_timestamp(row[0]))
        else:
            new_row.append(row[0])
        for item in row[1:]:
            new_row.append(item)
        rv.append(new_row)
    db.close()
    return rv

## END DB ##


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/history')
def history():
    return render_template('history.html')


# get the latest measure
@app.route('/api/live')
def api_live():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        while True:
            readings = query_db(DATABASE, 'SELECT * FROM sensor_readings ORDER BY timestamp DESC limit 1', convert_date=False)
            result = readings[2]
            result[0] = date_from_timestamp(result[0])
            if len(result) < 4:
                result.append('na')
            ws.send(json.dumps({'latest': result}))
            time.sleep(10)
    return jsonify({'status': 'ok'})


@app.route('/api')
def api():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        readings = query_db(DATABASE, 'SELECT * FROM sensor_readings ORDER BY timestamp DESC')
#        readings_salon = query_db(DATABASE_SALON, 'SELECT * FROM readings ORDER BY ts DESC')
#        readings_tobacco = query_db(DATABASE_TOBACCO, 'SELECT * FROM readings ORDER BY ts DESC')
        #ws.send(json.dumps({'en_cours': readings, 'salon': readings_salon, 'tobacco' : readings_tobacco}))
        ws.send(json.dumps({'en_cours': readings}))
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    http_server = WSGIServer(('', 80), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
