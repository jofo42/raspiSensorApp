#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sqlite3
import serial
import re
import subprocess
import threading
import logging
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

db_filename = 'temperature.db'
schema_filename = 'readingpoints.sql'
isolation_level = None  # autocommit mode

db_is_new = not os.path.exists(db_filename)

arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=2)


def arduinoWorker():
    while True:
        readings = arduino.readline().strip().split('\t')
        logging.debug("%s", readings)
        if len(readings) != 2:
            time.sleep(3)
            continue
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info("Arduino: %s: t = %s C, h= %s %%" % (timestamp, readings[1], readings[0]))
        with sqlite3.connect(db_filename, isolation_level=isolation_level) as conn:
            cursor = conn.cursor()
            #logging.debug('connected')
            #cursor.execute('update task set priority = priority + 1')
            cursor.execute('insert into sensor_readings (sensorid,timestamp,sensorvalue) values(?, ?, ?)', [(1), (timestamp), (readings[1])])
            #logging.debug('changes made')
            #logging.debug('waiting to synchronize')
            ready.wait()  # synchronize
        time.sleep(60)


def raspiPiWorker():
    while True:
        # Run the DHT program to get the humidity and temperature readings!

        output = subprocess.check_output(["./Adafruit_DHT", "11", "4"])
        #print output
        logging.debug("%s", output)
        matches = re.search("Temp =\s+([0-9.]+)", output)
        if (not matches):
            time.sleep(3)
            continue
        temp = float(matches.group(1))

        # search for humidity printout
        matches = re.search("Hum =\s+([0-9.]+)", output)
        if (not matches):
            time.sleep(3)
            continue
        humidity = float(matches.group(1))

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #print "Temperature: %.1f C" % temp
        #print "Humidity:    %.1f %%" % humidity
        logging.info("RaspberryPi: %s: t = %s C, h= %s %%" % (timestamp, temp, humidity))
        time.sleep(60)

if __name__ == '__main__':
    with sqlite3.connect(db_filename) as conn:
        if db_is_new:
            print 'Creating schema'
            with open(schema_filename, 'rt') as f:
                schema = f.read()
            conn.executescript(schema)
        else:
            logging.info('Database exists, assume schema does, too.')

    ready = threading.Event()

    threads = [
        threading.Thread(name='arduino1', target=arduinoWorker),
        threading.Thread(name='raspi1', target=raspiPiWorker),
    ]

    [ t.start() for t in threads ]

    time.sleep(1)
    logging.debug('setting ready')
    ready.set()

    [ t.join() for t in threads ]
