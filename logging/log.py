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
# curl -H "Content-type:application/json" --data @test.json http://localhost:5000/insert

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

        if request.form.get('associated_object'):
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
        if 'log' not in data or 'module' not in data or 'time' not in result:
          print "Mandatory field missing: (module, time, log)"
          return "Mandatory field missing: (module, time, log)"
        if 'level' not in result:
          data['level'] = 10
        if 'user' not in result:
          data['user'] = ''
        if 'module' not in result:
          data['module'] = ''
        if 'associated_object' not in result:
          data['associated_object'] = ''
        if 'host' not in result:
          data['host'] = ''
        if 'pid' not in result:
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

if __name__ == '__main__':
  app.run()