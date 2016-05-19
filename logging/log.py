#!/bin/env python
# -*- coding: utf-8 -*-

import re
import json
import pickle

import sys
import logging
import random

import time, datetime
import pytz

from flask import Flask, render_template, request, g, session, flash, \
     redirect, url_for, abort, jsonify, send_file
from flask import json

from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
import cassandra.util

# curl -H "Content-type:application/json" --data @test.json http://localhost:5000

'''
Python logging level definitions:

Level Numeric value
CRITICAL  50
ERROR 40
WARNING 30
INFO  20
DEBUG 10
NOTSET  0
'''

app = Flask(__name__)
app.config.update(
  SECRET_KEY = 'development key',
  DEBUG = True,
    
  # Database configuration
  DATABASE_URI = 'localhost',
  KEYSPACE_NAME = 's4gs',
)

cluster = Cluster(
  contact_points = [app.config['DATABASE_URI']],
)

db_session = cluster.connect(app.config['KEYSPACE_NAME'])

@app.route('/insert', methods=['POST', 'GET'])
def query():
  if request.method == 'POST':
    if request.headers['Content-Type'] == 'application/json':
      try:
        result = request.json
        if 'log' not in result or 'module' not in result or 'time' not in result:
          print "Mandatory field missing: (module, time, log)"
          return "Mandatory field missing: (module, time, log)"
        if 'level' not in result:
          result['level'] = 10
        if 'user' not in result:
          result['user'] = 'not-set'
        if 'module' not in result:
          result['module'] = ''
        if 'associated_object' not in result:
          result['associated_object'] = ''
        if 'host' not in result:
          result['host'] = ''
        if 'pid' not in result:
          result['pid'] = 0

        queryStr = 'insert into log \
          (event_id, time, level, user, module, log, associated_object, host, pid) values \
          (now(), ' + str(result['time']) + ', ' + str(result['level']) + ', \'' + result['user'] + '\', \'' + result['module'] + '\', \
          \'' + result['log'] + '\', \'' + result['associated_object'] + '\', \'' + result['host'] + '\', ' + str(result['pid']) + ');'
        # Check for return values!
        results = db_session.execute(queryStr)

        return "{\'status\': \'200\'}"
      except AttributeError as e:
          print(str(e))
          return "AttributeError:" + str(e)
      except BaseException as e:
          print(str(e))
          return "Unexpected error:" + str(e)

if __name__ == '__main__':
  app.run()