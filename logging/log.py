#!/bin/env python
# -*- coding: utf-8 -*-

import re
import json
import pickle
from pickle import PickleError, UnpicklingError

import sys
import logging
import random
import math

import time, datetime
import pytz

from flask import Flask, render_template, request, g, session, flash, \
     redirect, url_for, abort, jsonify, send_file
from flask import json

from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
import cassandra.util

# To test JSON:
# curl -H "Content-type:application/json" --data @test.json http://localhost:5000/log/insert

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

# Add cors headers for query passing
def add_cors_headers(response):
    # Allow any origin for the simple test 
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'HEAD, GET, POST, PATCH, PUT, OPTIONS, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
    return response

app.after_request(add_cors_headers)

cluster = Cluster(
  contact_points = [app.config['DATABASE_URI']],
)

db_session = cluster.connect(app.config['KEYSPACE_NAME'])

@app.route('/log/insert', methods=['POST', 'GET'])
def insert():
  if request.method == 'POST':
    data = None
    if request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
      try:
        '''
        ImmutableMultiDict([
          ('relativeCreated', u'7.21406936646'), 
          ('process', u'19436'), 
          ('args', u'()'), 
          ('module', u'test'), 
          ('funcName', u'<module>'), 
          ('exc_text', u'None'), 
          ('name', u'root'), 
          ('thread', u'140735128331008'), 
          ('created', u'1463695664.48'), 
          ('threadName', u'MainThread'), 
          ('msecs', u'481.328010559'), 
          ('filename', u'test.py'), 
          ('levelno', u'20'), 
          ('name', u'myapp.area2'),
          ('processName', u'MainProcess'), 
          ('pathname', u'test.py'), 
          ('lineno', u'20'), 
          ('msg', u'Jackdaws love my big sphinx of quartz.'), 
          ('exc_info', u'None'), 
          ('levelname', u'INFO')])
        '''
        data = dict()
        if request.form.get('created') and request.form.get('msecs'):
          data['time'] = int(math.floor(float(request.form.get('created')) * 1000 + float(request.form.get('msecs'))))
        else:
          return "Mandatory field missing: (module, time, log)"

        if request.form.get('levelno'):
          data['level'] = request.form.get('levelno')
        else:
          data['level'] = 10

        if request.form.get('user'):
          data['user'] = request.form.get('user')
        elif request.form.get('name'):
          data['user'] = request.form.get('name')
        else:
          data['user'] = ''

        if request.form.get('module'):
          data['module'] = request.form.get('module')
        else:
          return "Mandatory field missing: (module, time, log)"

        if request.form.get('msg'):
          data['log'] = request.form.get('msg')
        else:
          return "Mandatory field missing: (module, time, log)"

        if request.form.get('associated_object'):
          data['associated_object'] = request.form.get('associated_object')
        else:
          data['associated_object'] = ''

        if request.form.get('host'):
          data['host'] = request.form.get('host')
        else:
          data['host'] = ''

        if request.form.get('process'):
          data['pid'] = request.form.get('process')
        else:
          data['pid'] = 0
      except PickleError as e:
          print(str(e))
          return "PickleError:" + str(e)
      except UnpicklingError as e:
          print(str(e))
          return "UnpicklingError error:" + str(e)
    elif request.headers['Content-Type'] == 'application/json':
      try:
        data = request.json
        if 'log' not in data or 'module' not in data or 'time' not in data:
          print "Mandatory field missing: (module, time, log)"
          return "Mandatory field missing: (module, time, log)"
        if 'level' not in data:
          data['level'] = 10
        if 'user' not in data:
          data['user'] = ''
        if 'module' not in data:
          data['module'] = ''
        if 'associated_object' not in data:
          data['associated_object'] = ''
        if 'host' not in data:
          data['host'] = ''
        if 'pid' not in data:
          data['pid'] = 0
      except AttributeError as e:
        print(str(e))
        return "AttributeError:" + str(e)
      except BaseException as e:
        print(str(e))
        return "Unexpected error:" + str(e)
    else:
      print("Unrecognized Content-Type")
      return "Unrecognized Content-Type: " + request.headers['Content-Type']

    queryStr = 'insert into log \
      (event_id, time, level, user, module, log, associated_object, host, pid) values \
      (now(), ' + str(data['time']) + ', ' + str(data['level']) + ', \'' + data['user'] + '\', \'' + data['module'] + '\', \
      \'' + data['log'] + '\', \'' + data['associated_object'] + '\', \'' + data['host'] + '\', ' + str(data['pid']) + ');'
    # Check for return values!
    result = db_session.execute(queryStr)

    return "{\'status\': \'200\'}"

def json_handler(obj):
  resultStr = '{}'
  try:
    if (type(obj) is datetime.datetime):
      if hasattr(obj, 'isoformat'):
        # When we query from Cassandra, timestamp is always returned in UTC
        time = pytz.timezone('UTC').localize(obj).strftime('%Y-%m-%dT%H:%M:%SZ')
        return time
      else:
        print('datetime does not have isoformat')
        return 
    # This works for earlier versions of Cassandra Python binding (2.1.4)
    elif (type(obj) is cassandra.util.OrderedMap):
      tempDict = dict()
      # The problem here, is that obj.keys() is not hashable
      tempDict[str(obj.keys())] = obj.values()
      return json.dumps(tempDict)
    # This works for earlier versions of Cassandra Python binding (2.5.1)
    elif (type(obj) is cassandra.util.OrderedMapSerializedKey):
      tempDict = dict()
      # The problem here, is that obj.keys() is not hashable
      # Here we downgrade an OrderedMap to a json key-value pair; only first item in the key is taken care of.
      
      # TODO: check if this breaks anything...
      if (len(obj.keys()) > 0):
        for key in obj.keys():
          tempDict[str(key)] = obj[key]
      return json.dumps(tempDict)
    else: 
        resultStr = json.dumps(list(obj))
  except BaseException as e:
      print('Query result object may not be listable; type ' + str(type(obj)))
      print(str(e))
  return resultStr

@app.route('/query', methods=['POST', 'GET'])
def query():
  if request.method == 'POST':
    queryStr = request.form['query']
    if 'encoding' in request.form:
      resultEncoding = request.form['encoding']
    else:
      resultEncoding = 'json'

    try:
      # Note: json.dumps does not know how to handle timeuuid directly, nor does it seem to know how to handle set...
      if resultEncoding == 'json':
        result = json.dumps(db_session.execute(queryStr), default = json_handler)
      elif resultEncoding == 'pickle':
        # TODO: experimental pickle does not work yet...
        from cassandra.query import tuple_factory
        db_session.row_factory = tuple_factory
        result = pickle.dumps(db_session.execute(queryStr))
      else:
        result = str(db_session.execute(queryStr))
      return result
    except AttributeError as e:
      print(str(e))
      return "AttributeError:" + str(e)
    except BaseException as e:
      print(str(e))
      return "Unexpected error:" + str(e)

@app.route('/tail_log')
def tail_log():
  return redirect(url_for('static', filename='tail_log.html'))

if __name__ == '__main__':
  app.run(host='0.0.0.0',port=25000)