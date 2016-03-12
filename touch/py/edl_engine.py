#
#	edl_engine.py
#
#	Copyright 2015 Regents of the University of California
#
#	This program is free software : you can redistribute it and / or modify
#	it under the terms of the GNU Lesser General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
#	GNU Lesser General Public License for more details.
#
#	You should have received a copy of the GNU Lesser General Public License
#	along with this program.If not, see <http:#www.gnu.org/licenses/>.
# 
#	Author: Peter Gusev, peter@remap.ucla.edu

import sys
import time
import string
import json
import os
import collections
import logging
import traceback
from datetime import datetime

logger = None

from pyndn import Name
from pyndn import Face
from pyndn import Interest

### ndn helpers
def millisecondTimestamp():
	dt = datetime.now()-datetime(1970,1,1)
	milliseconds =  (dt.days*24*3600+dt.seconds)*1000 + dt.microseconds/1000
	return int(milliseconds)

def dump(*list):
    result = ""
    for element in list:
        result += (element if type(element) is str else repr(element)) + " "
    print(result.encode('cp437', errors='replace').decode('cp437'))

#####################################################################
class DataFetcher(object):
	"""
	Provides simple interface for fetching NDN data
	"""
	def __init__(self, face):
		self.face = face
	
	def expressInterest(self, interest):
		return self.face.expressInterest(interest, self.onData, self.onTimeout)
	
	def onData(self, interest, data):
		raise NotImplementedError("should be implemented")
	
	def onTimeout(self, interest):
		raise NotImplementedError("should be implemented")

#####################################################################
class Pipeliner(DataFetcher):
	"""
	Retrieves latest data which has sequential number defined 
	by the last name component.
	Last name component should be number!
	"""
	def __init__(self, face, dataPath, onNewData):
		DataFetcher.__init__(self, face)
		self.dataPath = dataPath
		self.onNewData = onNewData
		self.interestLifetimeMs = 1000
		self.windowSize = 2
		self.latestReceivedNo = None 
		self.latestExpressedNo = None
		self.bootstrap()

	def bootstrap(self):
		rightmostInterest = Interest(Name(self.dataPath))
		rightmostInterest.setChildSelector(0)
		if self.latestExpressedNo:
			rightmostInterest.getExclude().appendAny()
			rightmostInterest.getExclude().appendComponent(self.latestExpressedNo)
		self.expressInterest(rightmostInterest)

	def process(self):
		self.face.processEvents()

	def keepPipeline(self):
		if self.latestExpressedNo != None and self.latestReceivedNo != None:
			while (self.latestExpressedNo - self.latestReceivedNo) < self.windowSize:
				self.addOutstanding()

	def addOutstanding(self):
		self.latestExpressedNo += 1
		outstandingInterest = Interest(Name(self.dataPath).append(str(self.latestExpressedNo)))
		# outstandingInterest.getExclude().appendAny()
		# outstandingInterest.getExclude().appendComponent(self.latestExpressedNo)
		self.expressInterest(outstandingInterest)

	def expressInterest(self, interest):
		global logger
		logger.debug("express "+str(interest.getName().toUri()))
		interest.setInterestLifetimeMilliseconds(self.interestLifetimeMs)
		super(Pipeliner, self).expressInterest(interest)

	def onData(self, interest, data):
		global logger
		logger.debug("incoming with name %r"%(data.getName().toUri()))
		logger.info("received data %r"%(data.getName().toUri()))
		seqNoComp = data.getName().get(-1).toEscapedString() 
		if seqNoComp.isdigit():
			seqNo = int(seqNoComp)
			if not (self.latestReceivedNo or self.latestExpressedNo):
				self.latestExpressedNo = seqNo
				self.latestReceivedNo = seqNo
			else:
				if self.latestReceivedNo < seqNo:
					self.latestReceivedNo = seqNo
			self.onNewData(seqNo, data.getContent().toRawStr())
			self.keepPipeline()

	def onTimeout(self, interest):
		global logger
		logger.debug("timeout %r"%(interest.getName().toUri()))
		self.expressInterest(interest)

#####################################################################
class StreamTimestamp(object):
	def __init__(self, timestampStr, framerate = 23.976):
		self.str = timestampStr
		self.framerate = framerate
		self.parseStr()

	def parseStr(self):
		components = self.str.split(':')
		if len(components) == 4:
			for c in components:
				if not c.isdigit():
					raise NameError(self.str, "timestamp components should be numbers")
			if int(components[3]) > int(round(self.framerate)):
				raise NameError(self.str, "frame number exceeds allowed framerate")
			self.hour = int(components[0])
			self.min = int(components[1])
			self.sec = int(components[2])
			self.frame = int(components[3])
		else:
			raise NameError(self.str, "number of timestamp components is not 4")

	def toFrames(self):
		frameTimestamp = self.frame
		frameTimestamp += self.sec * self.framerate
		frameTimestamp += self.min * 60 * self.framerate
		frameTimestamp += self.hour * 3600 * self.framerate
		return frameTimestamp

	def toSeconds(self):
		secondTimestamp = self.frame/self.framerate
		secondTimestamp += self.sec
		secondTimestamp += self.min * 60
		secondTimestamp += self.hour * 3600
		return secondTimestamp

	def __eq__(self, other):
		if other is None or not isinstance(other, StreamTimestamp):
			return False
		return self.toFrames() == other.toFrames()

	def __le__(self, other):
		return self.toFrames() <= other.toFrames()

	def __lt__(self, other):
		return self.toFrames() < other.toFrames() 

	def __str__(self):
		return self.str

	def __repr__(self):
		return self.__str__()

#####################################################################
class EventBase(object):
	def __init__(self):
		self.id = 0
		self.videoStartTime = StreamTimestamp("00:00:00:00")
		self.videoEndTime = StreamTimestamp("00:00:00:00")
		self.clipStartTime = StreamTimestamp("00:00:00:00")
		self.clipEndTime = StreamTimestamp("00:00:00:00")
		self.videoUrl = 'none'
		self.ytUrl = 'none'
		self.clipName = 'none'
		self.reelName = 'none'
		self.trans = 'none'
		self.channel = 'none'
		self.videoFramerate = 23.976
		self.startTimeOffset = 0
		self.res = None

	def getSrcDuration(self):
		return self.videoEndTime.toSeconds()-self.videoStartTime.toSeconds()

	def getClipDuration(self):
		return self.clipEndTime.toSeconds()-self.clipStartTime.toSeconds()

	def __str__(self):
		return "["+str(self.id)+"| empty ]"

	def __repr__(self):
		return self.__str__()

	def shortStr(self):
		return self.__str__()

class DummyEvent(EventBase):
	def __init__(self, startTimestampStr, endTimestampStr):
		self.id = -1
		self.videoStartTime = StreamTimestamp("00:00:00:00")
		self.videoEndTime = StreamTimestamp("00:00:00:00")
		self.clipStartTime = StreamTimestamp(startTimestampStr)
		self.clipEndTime = StreamTimestamp(endTimestampStr)
		self.videoUrl = 'none'
		self.ytUrl = 'none'
		self.clipName = 'none'
		self.reelName = 'none'
		self.trans = 'none'
		self.channel = 'none'
		self.videoFramerate = 23.976
		self.startTimeOffset = 0
		self.res = None
		self.releaseTime = 0

	def __str__(self):
		return "[DUMM| "+str(self.clipStartTime)+"-"+str(self.clipEndTime)+"]"


class Event(EventBase):
	eventIdKey = 'event_id'

	def __init__(self, jsonData):
		super(Event, self).__init__()
		self.jsonData = jsonData
		self.id = int(jsonData[self.eventIdKey])

class EndEvent(Event):
	srcUrlKey = 'src_url'
	endToken = 'end'

	def __init__(self, jsonData):
		super(EndEvent, self).__init__(jsonData)
		if jsonData[self.srcUrlKey] != self.endToken:
			raise Exception('bad format', 'end event is not formatted correctly')
		self.clipStartTime = StreamTimestamp('23:59:59:0')

	def __str__(self):
		return "["+str(self.id)+" | end ]"

	def shortStr(self):
		return "["+str(self.id)+" | "+self.clipStartTime+" ]"

class EditEvent(Event):
	eventIdKey = 'event_id'
	reelNameKey = 'reel_name'
	srcStartTimeKey = 'src_start_time'
	srcEndTimeKey = 'src_end_time'
	srcUrlKey = 'src_url'
	dstEndTimeKey = 'dst_end_time'
	dstStartTimeKey = 'dst_start_time'
	transKey = 'trans'
	channelKey = 'channel'
	startTimeOffset = 0
	clipNameKey = 'clip_name'
	framerateKey = 'frame_rate'
	ytUrlKey = 'ori_url'

	def __init__(self, jsonData):
		super(EditEvent, self).__init__(jsonData)
		self.videoUrl = jsonData[self.srcUrlKey]
		if jsonData[self.framerateKey] != 'none':
			self.videoFramerate = float(jsonData[self.framerateKey])
		self.videoStartTime = StreamTimestamp(jsonData[self.srcStartTimeKey], framerate = self.videoFramerate)
		self.videoEndTime = StreamTimestamp(jsonData[self.srcEndTimeKey], framerate = self.videoFramerate)
		self.clipStartTime = StreamTimestamp(jsonData[self.dstStartTimeKey], framerate = self.videoFramerate)
		self.clipEndTime = StreamTimestamp(jsonData[self.dstEndTimeKey], framerate = self.videoFramerate)
		if self.ytUrlKey in jsonData.keys(): self.ytUrl = jsonData[self.ytUrlKey]
		if self.clipNameKey in jsonData.keys(): self.clipName = jsonData[self.clipNameKey]
		if self.reelNameKey in jsonData.keys(): self.reelName = jsonData[self.reelNameKey]
		if self.transKey in jsonData.keys(): self.trans = jsonData[self.transKey]
		if self.channelKey in jsonData.keys(): self.channel = jsonData[self.channelKey]

	def __str__(self):
		return "[" + str(self.id)+"-"+str(self.channel)+"|"+str(self.videoUrl[:77])+"... "+\
		str(self.videoStartTime)+"-"+str(self.videoEndTime)+"==>"+\
		str(self.clipStartTime)+"-"+str(self.clipEndTime)+\
		"("+"{0:.2f}".format(self.videoStartTime.toSeconds())+"-"+"{0:.2f}".format(self.videoEndTime.toSeconds())+"==>"+\
		"{0:.2f}".format(self.clipStartTime.toSeconds())+"-"+"{0:.2f}".format(self.clipEndTime.toSeconds())+")"+"]"

	def shortStr(self):
		return "[" + str(self.id)+"-"+str(self.channel)+"|"+\
		str(self.videoStartTime)+"-"+str(self.videoEndTime)+"==>"+\
		str(self.clipStartTime)+"-"+str(self.clipEndTime)+"]"

#####################################################################
class EventPoller(Pipeliner):
	def __init__(self, face, ndnPath, onNewEvent):
		super(EventPoller, self).__init__(face, ndnPath, self.onNewData)
		self.onNewEvent = onNewEvent

	def onNewData(self, seqNo, data):
		global logger
		eventData = None
		try:
			eventData = json.loads(str(data))
			logger.debug('parsed event data: %r'%eventData)
		except Exception as e:
			logger.error('error parsing json data (%r): %r'%(str(data), e))
		event = None
		try:
			event = EditEvent(eventData)
		except Exception as e:
			logger.error('error creating EditEvent (%r) from data: %r, trying EndEvent...'%(e, str(eventData)))
		if event == None:
			try:
				event = EndEvent(eventData)
				logger.info('end event created '+str(event))
			except Exception as e:
				logger.error('error creating EndEvent: %r\ndata: %r'%(e, eventData))
		if event != None:
			self.onNewEvent(event)

#####################################################################
if __name__ == '__main__':
	face = Face("localhost")
	p = Pipeliner(face, "/test/edl", onNewEvent)
	logger = logging.Logger('main')
	h = logging.StreamHandler(sys.stdout)
	h.setLevel(logging.INFO)
	h.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))	
	logger.addHandler(h)
	logger.setLevel(logging.DEBUG)
	while True:
		p.process()
		time.sleep(0.01)
	face.shutdown()
