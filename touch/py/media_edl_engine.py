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
from edl_engine import DummyEvent

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
		startTime = self.event.videoStartTime.toSeconds()+self.event.startTimeOffset
		logger.info(str(time)+' preload operation for '+str(self.ppController.compPath)+' ('+str(self.ppController.ytController.url)+\
			') start time: '+str(startTime))
		#self.ppController.url = self.url
		self.ppController.videoUrl = self.event.videoUrl
		self.ppController.startTime = startTime
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
	def __init__(self, event, res, resMan):
		global logger
		self.event = event
		self.res = res
		self.resMan = resMan
		self.priority = self.OperationPriorityFinalize

	def __str__(self):
		return "release resource"

	def run(self, time):
		logger.info(str(time)+' release resource '+str(self.res.compPath)+' ('+str(self.res.ytController.url)+')')
		self.resMan.freeResource(self.res)
		me.mod.vars.videoEdlEngine.removeScheduledEvent(self.event)

class SwitchLiveOperation(Operation):
	def __init__(self, res, switch, event=None, onSwitch=None):
		self.res = res
		self.switch = switch
		self.priority = self.OperationPriorityTransit
		self.event = event
		self.onSwitchFunc = onSwitch

	def __str__(self):
		return "switch live"

	def run(self, time):
		if self.res.op.digits <= self.switch.nInputs:
			logger.info(str(time)+ ' switching live to pipeline'+str(self.res.op.digits)+' ('+str(self.res.ytController.url)+')')
			self.switch.blend = 0
			self.switch.blendIn1 = (self.res.op.digits-1)
			if self.onSwitchFunc and self.event:
				self.onSwitchFunc(self.event)
		else:
			logger.warning('can\'t switch live: resource index larger than the number of available switch inputs')

class BlackoutOperation(VideoOperation):
	def __init__(self, ppController):
		super(BlackoutOperation,self).__init__(ppController)
		self.priority = self.OperationPriorityInitiate

	def __str__(self):
		return "blackout"

	def run(self, time):
		global logger
		logger.info(str(time)+' set blackout on '+str(self.ppController.compPath)+' ('+str(self.ppController.ytController.url)+')')		
		self.ppController.pause = 1
		self.ppController.blackout = 1

class CheckUpcomingEvent(Operation):
	def __init__(self, event):
		self.event = event
		self.priority = self.OperationPriorityLowest

	def __str__(self):
		return "check upcoming"

	def run(self, time):
		global logger
		logger.info(str(time)+' checking for upcoming events or gaps...')
		me.mod.vars.videoEdlEngine.checkForTimelineGaps(self.event)

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
	gapDeadline = 1
	clipMaxTime = 0
	lastEventClipEndTime = None
	scheduledEvents = None
	def __init__(self):
		self.resMan = StreamingResourceManager()
		self.evDis = me.mod.vars.eventDispatcher
		self.timeline = me.mod.vars.mainTimeline
		self.liveSwitch = me.mod.vars.streamSwitch
		self.startTime = None
		self.scheduledEvents = []
		me.mod.vars.videoEdlEngine = self

	def timeSinceStart(self):
		delta = main.timeFunc() - self.startTime if not self.startTime == None else -1
		if self.startTime == 0 or delta < 0:
			return 0
		else:
			return delta

	def clipTime(self):
		timeSinceStart = self.timeSinceStart()
		hr = int(timeSinceStart/3600)
		timeSinceStart -= hr*3600
		min = int(timeSinceStart/60)
		timeSinceStart -= min*60
		sec = int(timeSinceStart)
		frac = int((timeSinceStart - sec)*100)
		return "{:02}:{:02}:{:02}:{:02}".format(hr, min, sec, frac)

	def run(self):
		freeRes = self.resMan.getFreeResources()
		if len(freeRes) > 0:
			event = self.evDis.popUpcomingEvent()
			self.processEvent(event, freeRes[0])

	def cleanupCurrentRun(self):
		logger.info('clip is over. cleaning up now...')
		main.reset()

	def checkForTimelineGaps(self, event):
		# check for timeline gaps
		# incoming video events should not have them, as they 
		# were sorted by clip start time
		if self.hasTimelineGap(event):
			logger.warning('inserting dummy event')
			dummyEvent = self.getDummyEvent(event)
			freeRes = self.resMan.getFreeResources()
			if len(freeRes) > 0:
				self.scheduleOnResource(dummyEvent, freeRes[0])

	def removeScheduledEvent(self, event):
		i = 0
		for ev in self.scheduledEvents:
			if event.id == ev.id:
				del self.scheduledEvents[i]
				break
			i += 1

	def getNextScheduledEvent(self, event):
		if len(self.scheduledEvents) > 0:
			eventsByStartTime = sorted(self.scheduledEvents, key=lambda e: e.clipStartTime, reverse=False)
			for ev in eventsByStartTime:
				if (ev.clipStartTime <= event.clipEndTime and ev.clipEndTime > event.clipEndTime) or ev.clipStartTime > event.clipEndTime:
					return ev
		return None

	def hasTimelineGap(self, event):
		logger.debug('checking for timeline gap...')
		nextEvent = self.getNextScheduledEvent(event)
		if not nextEvent:
			logger.warning('no new scheduled event. need a dummy.')
			return True
		else:
			gap = nextEvent.clipStartTime.toFrames() - event.clipEndTime.toFrames()
			if gap > 1:
				logger.warning('timeline gap detected: '+str(gap)+' frames (between events '+str(event.id)+' and '+str(nextEvent.id)+')')
				return True
		return False
		# lastEvent = self.scheduledEvents[0]
		# if event.id == lastEvent.id:
		# 	logger.warning('no new scheduled events. need a dummy.')
		# 	return True
		# else:
		# 	gap = lastEvent.clipStartTime.toFrames() - event.clipEndTime.toFrames()
		# 	if abs(gap) > 1:
		# 		logger.warning('timeline gap detected: '+str(gap)+' frames (between events '+str(event.id)+' and '+str(lastEvent.id)+')')
		# 		return True
		# return False

	def getDummyEvent(self, lastEvent):
		dummyEvent = DummyEvent(str(lastEvent.clipEndTime), "23:59:59:00")
		return dummyEvent

	def processEvent(self, event, res):
		global logger
		if isinstance(event, EndEvent):
			if self.startTime:
				logger.info('end event received: '+str(event))
				self.timeline.scheduleOperations(self.clipMaxTime+2, [DispatchOperation(self.cleanupCurrentRun)])
		else:
			if event:
				if event.id == 1 and self.startTime == None:
					self.startTime = main.timeFunc()+self.preloadTime
					logger.debug('first event is '+str(event.id)+'. start time is at '+str(self.startTime)+'('+str(self.startTime-main.timeFunc())+' seconds from now)')
				if self.startTime:
					if (event.channel == 'V' or event.channel == 'AA/V') \
					and (event.videoUrl != None):
						# check for timeline gaps
						# incoming video events should not have them, as they 
						# were sorted by clip start time
						# if self.hasTimelineGap(event):
						# 	logger.warning('inserting dummy event')
						# 	dummyEvent = self.getDummyEvent(event)
						# 	self.scheduleOnResource(dummyEvent, res)
						# check whether we had dummy events before
						logger.debug('processing event '+str(event))
						self.scheduleOnResource(event, res)
						self.lastEventClipEndTime = event.clipEndTime
				else:
					logger.warning('received event, but it\'s is not 1. processing starts with event ID 1. sorry.')

	def scheduleOnResource(self, event, res):
		global logger
		logger.info("scheduling event "+str(event)+" on resource "+str(res.compPath))

		lastDummy = self.scheduledEvents[0] if len(self.scheduledEvents) > 0 and isinstance(self.scheduledEvents[0], DummyEvent) else None
		self.scheduledEvents.insert(0, event)
		self.resMan.occupyResource(res)
		hasVideoUrl = (event.videoUrl != 'none')
		t = self.startTime
		event.res = res

		if hasVideoUrl:
			# this is the offset in seconds used to adjust video start time
			# in order to start video playback earlier to avoid intercut blackouts
			playbackOffset = -1 # absolute value should not be larger than preloadTime
			event.startTimeOffset = playbackOffset if event.videoStartTime.toSeconds() > 1 else -event.videoStartTime.toSeconds()
			playbackOffset = event.startTimeOffset

			# schedule preloading - PreloadOperation
			self.timeline.scheduleOperationFromNow(0, PreloadOperation(event, res))

			# schedule playback start - StartPlaybackOperation + SwitchLiveOperation
			t += event.clipStartTime.toSeconds()
			# blinking workaround:
			# schedule start playback operation 1s earlier to avoid
			# blinking when switching b/w clips
			self.timeline.scheduleOperations(t+playbackOffset, [StartPlaybackOperation(res)])
			self.timeline.scheduleOperations(t, [SwitchLiveOperation(res, self.liveSwitch, event, main.onStreamSwitched)])

			# check if the last event was a dummy and release it's resource if it was
			if lastDummy:
				self.timeline.scheduleOperations(t, [ReleaseResourceOperation(event, lastDummy.res, self.resMan)])
				self.timeline.removeOperations(lastDummy.releaseTime)
				lastDummy.clipEndTime = event.clipStartTime
				main.onDummyUpdate(lastDummy)

			# schedule playback stop - StopPlaybackOperation
			t += event.getClipDuration()
			self.timeline.scheduleOperations(t, [StopPlaybackOperation(res)])

			# schedule resource release
			self.timeline.scheduleOperations(t, [ReleaseResourceOperation(event, res, self.resMan)])
		else: # treat as blackout
			t += event.clipStartTime.toSeconds()
			self.timeline.scheduleOperations(t, [SwitchLiveOperation(res, self.liveSwitch, event, main.onStreamSwitched),\
				StopPlaybackOperation(res)])
			t += event.getClipDuration()
			self.timeline.scheduleOperations(t, [ReleaseResourceOperation(event, res, self.resMan)])

			if not isinstance(event, DummyEvent):
				logger.debug('event has no video URL. treated as blackout.')
			else:
				event.releaseTime = t
		
		# setup check for upcoming events and timeline gaps for all scheduled events except dummies
		if not isinstance(event, DummyEvent):
			schedTime = t-self.gapDeadline if event.getClipDuration() > self.gapDeadline else event.getClipDuration()/2.
			self.timeline.scheduleOperations(schedTime, [CheckUpcomingEvent(event)])

		# track overall clip time
		if t > self.clipMaxTime:
			self.clipMaxTime = t
