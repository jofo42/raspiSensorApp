#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys
import serial
import re
from time import sleep
from datetime import datetime

arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=2)

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
                readings = arduino.readline().strip().split('\t')
            	print readings
                if len(readings) == 2:
                    break
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print "%s: t = %s C, h= %s %%" % (time, readings[1], readings[0])
            sleep(60)
            cur.execute("INSERT INTO data(date, temp, hum) VALUES(?, ?, ?)", (time, readings[1], readings[0]))
            con.commit()

except lite.Error, e:

    print "Error %s:" % e.args[0]
    sys.exit(1)

finally:

    if con:
        con.close()
