#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
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

arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=2)

con = None


def arduinoWorker():
    while True:
        readings = arduino.readline().strip().split('\t')
        logging.debug("%s", readings)
        if len(readings) != 2:
		time.sleep(3)
		continue
	timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    	logging.info("Arduino: %s: t = %s C, h= %s %%" % (timestamp, readings[1], readings[0]))
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


a = threading.Thread(name='arduino', target=arduinoWorker)
r = threading.Thread(name='raspberrypi', target=raspiPiWorker)

a.start()
r.start()
