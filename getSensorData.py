#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import serial
import re
import threading
import logging
import time
from datetime import datetime

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )


arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=2)

con = None


def arduinoWorker():
    while True:
        readings = arduino.readline().strip().split('\t')
        print readings
        if len(readings) == 2:
            break
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.debug("Arduino: %s: t = %s C, h= %s %%" % (time, readings[1], readings[0]))
    time.sleep(60)


def raspiPiWorker():
    while True:
        # Run the DHT program to get the humidity and temperature readings!

        output = subprocess.check_output(["./Adafruit_DHT", "11", "4"])
        #print output
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

        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #print "Temperature: %.1f C" % temp
        #print "Humidity:    %.1f %%" % humidity
        logging.debug("RaspberryPi: %s: t = %s C, h= %s %%" % (time, temp, humidity))
        time.sleep(60)


a = threading.Thread(name='arduino', target=arduinoWorker)
r = threading.Thread(name='raspberrypi', target=raspiPiWorker)
