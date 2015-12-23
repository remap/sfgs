#
#	media_edl_engine.py
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

import time
import main
from edl_engine import EndEvent

logger = None
Operation = me.mod.classes.Operation

################################################
class DispatchOperation(Operation):	
	def __init__(self, func): 
		self.func = func
		self.priority = self.OperationPriorityLowest

	def __str__(self):
		return "dispatch"

	def run(self, t):
		self.func()

class VideoOperation(Operation):
	def __init__(self, ppController):
		self.priority = self.OperationPriorityHighest
		self.ppController = ppController

	def run(self):
		pass

class PreloadOperation(VideoOperation):
	def __init__(self, event, ppController):
		super(PreloadOperation,self).__init__(ppController)
		self.priority = self.OperationPriorityInitiate
		self.event = event

	def __str__(self):
		return "preload"

	def run(self, time):
		global logger
		logger.info(str(time)+' preload operation for '+str(self.ppController.compPath)+' ('+str(self.ppController.ytController.url)+\
			') start time: '+str(self.event.videoStartTime.toSeconds()))
		#self.ppController.url = self.url
		self.ppController.videoUrl = self.event.videoUrl
		self.ppController.startTime = self.event.videoStartTime.toSeconds()
		self.ppController.pause = 1
		self.ppController.blackout = 1

class StartPlaybackOperation(VideoOperation):
	def __init__(self, ppController):
		super(StartPlaybackOperation, self).__init__(ppController)
		self.priority = self.OperationPriorityInitiate

	def __str__(self):
		return "start playback"

	def run(self, time):
		global logger
		logger.info(str(time)+' start playback '+str(self.ppController.compPath)+' ('+str(self.ppController.ytController.url)+')')
		self.ppController.pause = 0
		self.ppController.blackout = 0

class StopPlaybackOperation(VideoOperation):
	def __init__(self, ppController):
		super(StopPlaybackOperation, self).__init__(ppController)
		self.priority = self.OperationPriorityFinalize

	def __str__(self):
		return "stop playback"

	def run(self, time):
		global logger
		logger.info(str(time)+' stop playback '+str(self.ppController.compPath)+' ('+str(self.ppController.ytController.url)+')')		
		self.ppController.pause = 1
		self.ppController.blackout = 1

class ReleaseResourceOperation(Operation):
	def __init__(self, res, resMan):
		global logger
		self.res = res
		self.resMan = resMan
		self.priority = self.OperationPriorityFinalize

	def __str__(self):
		return "release resource"

	def run(self, time):
		logger.info(str(time)+' release resource '+str(self.res.compPath)+' ('+str(self.res.ytController.url)+')')
		self.resMan.freeResource(self.res)

class SwitchLiveOperation(Operation):
	def __init__(self, res, switch):
		self.res = res
		self.switch = switch
		self.priority = self.OperationPriorityTransit

	def __str__(self):
		return "switch live"

	def run(self, time):
		if self.res.op.digits <= self.switch.nInputs:
			logger.info(str(time)+ ' switching live to pipeline'+str(self.res.op.digits)+' ('+str(self.res.ytController.url)+')')
			self.switch.blend = 0
			self.switch.blendIn1 = (self.res.op.digits-1)
		else:
			logger.warn('can\'t switch live: resource index larger than the number of available switch inputs')

################################################
class StreamingResourceManager(object):
	def __init__(self):
		self.resourceAllocator = me.mod.vars.streamResourceAllocator
		self.free = self.resourceAllocator.getResources()
		self.busy = []

	def getFreeResources(self):
		return self.free

	def occupyResource(self, res):
		global logger
		if not res in self.busy and res in self.free:
			self.busy.append(res)
			self.free.remove(res)
			logger.debug('resource taken: '+str(res.compPath)+' taken: '+str(len(self.busy))+' free: '+str(len(self.free)))

	def freeResource(self, res):
		if not res in self.free and res in self.busy:
			self.free.append(res)
			self.busy.remove(res)
			logger.debug('resource released: '+str(res.compPath)+' taken: '+str(len(self.busy))+' free: '+str(len(self.free)))

################################################
class VideoEdlEngine(object):
	preloadTime = 5
	clipMaxTime = 0
	def __init__(self):
		self.resMan = StreamingResourceManager()
		self.evDis = me.mod.vars.eventDispatcher
		self.timeline = me.mod.vars.mainTimeline
		self.liveSwitch = me.mod.vars.streamSwitch
		self.startTime = None

	def run(self):
		freeRes = self.resMan.getFreeResources()
		if len(freeRes) > 0:
			event = self.evDis.popUpcomingEvent()
			self.processEvent(event, freeRes[0])
			
	def processEvent(self, event, res):
		global logger
		if isinstance(event, EndEvent):
			logger.info('end event received: '+str(event))
			self.timeline.scheduleOperations(self.clipMaxTime+2, [DispatchOperation(self.cleanupCurrentRun)])
		else:
			if event:
				if event.id == 1 and self.startTime == None:
					self.startTime = time.time()+self.preloadTime
					logger.debug('first event is '+str(event.id)+'. start time is at '+str(self.startTime)+'('+str(self.startTime-time.time())+' seconds from now)')
				if self.startTime:
					if (event.channel == 'V' or event.channel == 'AA/V') \
					and (event.videoUrl != None): # and event.videoUrl != 'none'):
						logger.debug('processing event '+str(event))
						self.scheduleOnResource(event, res)
					# if self.startTime == None and event.id != 1:
					# 	logger.warn("event processing hasn't started (event #1 was never received)")
					# else:
					# 	logger.debug('event id is '+str(event.id))
					# 	if event.id == 1:
					# 		self.startTime = time.time()+self.preloadTime
					# 		logger.debug('first event. start time is at '+str(self.startTime)+'('+str(self.startTime-time.time())+' seconds from now)')
					# 	self.scheduleOnResource(event, res)

	def cleanupCurrentRun(self):
		logger.info('clip is over. cleaning up now...')
		main.reset()

	def scheduleOnResource(self, event, res):
		global logger
		logger.info("scheduling event "+str(event)+" on resource "+str(res.compPath))
		self.resMan.occupyResource(res)
		hasVideoUrl = (event.videoUrl != 'none')

		t = 0

		if hasVideoUrl:
			# schedule preloading
			self.timeline.scheduleOperationFromNow(t, PreloadOperation(event, res))

			# schedule playback start
			t += self.startTime + event.clipStartTime.toSeconds()
			# temporary workaround:
			# schedule start playback operation 10ms earlier to avoid
			# blinking when switching b/w clips
			self.timeline.scheduleOperations(t-0.01, [StartPlaybackOperation(res)])
			self.timeline.scheduleOperations(t, [SwitchLiveOperation(res, self.liveSwitch)])

			# schedule playback stop
			t += event.getClipDuration()
			self.timeline.scheduleOperations(t, [StopPlaybackOperation(res)])

			# schedule resource release
			self.timeline.scheduleOperations(t, [ReleaseResourceOperation(res, self.resMan)])
		else: # treat as blackout
			logger.debug('event has no video URL. treated as blackout.')
			t += self.startTime + event.clipStartTime.toSeconds()
			self.timeline.scheduleOperations(t, [SwitchLiveOperation(res, self.liveSwitch)])
			self.timeline.scheduleOperations(t, [StopPlaybackOperation(res)])
			self.timeline.scheduleOperations(t, [ReleaseResourceOperation(res, self.resMan)])
		
		if t > self.clipMaxTime:
			self.clipMaxTime = t
