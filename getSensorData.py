#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys
import serial
import re
import subprocess
from time import sleep
from datetime import datetime

#arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=2)

con = None

try:
    con = lite.connect('sensordata.db')

    with con:

        cur = con.cursor()

        cur.execute('SELECT SQLITE_VERSION()')

        data = cur.fetchone()

        print "SQLite version: %s" % data

        #cur.execute("CREATE TABLE data(date TEXT, temp INTEGER, hum INTEGER)")

        while True:
            while True:
                # Run the DHT program to get the humidity and temperature readings!

                output = subprocess.check_output(["./Adafruit_DHT", "11", "4"])
                print output
                matches = re.search("Temp =\s+([0-9.]+)", output)
                if (not matches):
                  sleep(3)
                  continue
                temp = float(matches.group(1))

                # search for humidity printout
                matches = re.search("Hum =\s+([0-9.]+)", output)
                if (not matches):
                  sleep(3)
                  continue
                humidity = float(matches.group(1))

                print "Temperature: %.1f C" % temp
                print "Humidity:    %.1f %%" % humidity

#            while True:
#                readings = arduino.readline().strip().split('\t')
#            	print readings
#                if len(readings) == 2:
#                    break
#            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#            print "%s: t = %s C, h= %s %%" % (time, readings[1], readings[0])
#            sleep(60)
            #cur.execute("INSERT INTO data(date, temp, hum) VALUES(?, ?, ?)", (time, readings[1], readings[0]))
            #con.commit()

except lite.Error, e:

    print "Error %s:" % e.args[0]
    sys.exit(1)

finally:

    if con:
        con.close()
