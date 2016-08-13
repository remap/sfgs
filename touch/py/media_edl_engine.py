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
from edl_engine import StartEvent

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
	def __init__(self, event, ppController):
		self.priority = self.OperationPriorityHighest
		self.ppController = ppController
		self.event = event

	def run(self):
		pass

class PreloadOperation(VideoOperation):
	def __init__(self, event, ppController):
		super(PreloadOperation,self).__init__(event, ppController)
		self.priority = self.OperationPriorityInitiate

	def __str__(self):
		startTime = self.event.videoStartTime.toSeconds()+self.event.startTimeOffset
		return "preload, " + self.event.shortStr() + ', ' + str(startTime) + ', ' +str(self.event.ytUrl)

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
	def __init__(self, event, ppController):
		super(StartPlaybackOperation, self).__init__(event, ppController)
		self.priority = self.OperationPriorityInitiate

	def __str__(self):
		return "start playback, " + self.event.shortStr()

	def run(self, time):
		global logger
		logger.info(str(time)+' start playback '+str(self.ppController.compPath)+' ('+str(self.ppController.ytController.url)+')')
		self.ppController.pause = 0
		self.ppController.blackout = 0

class StopPlaybackOperation(VideoOperation):
	def __init__(self, event, ppController):
		super(StopPlaybackOperation, self).__init__(event, ppController)
		self.priority = self.OperationPriorityFinalize

	def __str__(self):
		return "stop playback, " + self.event.shortStr()

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
		return "release resource, "+self.event.shortStr()+', '+str(self.res.compPath)

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
		return "switch live, "+self.event.shortStr()+', '+str(self.res.compPath)

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
	def __init__(self, event, ppController):
		super(BlackoutOperation,self).__init__(event, ppController)
		self.priority = self.OperationPriorityInitiate

	def __str__(self):
		return "blackout, "+self.event.shortStr()

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
		return "check upcoming, "+self.event.shortStr()

	def run(self, time):
		global logger
		logger.info(str(time)+' checking for upcoming events or gaps...')
		me.mod.vars.videoEdlEngine.checkForTimelineGaps(self.event)

class TitleOperation(Operation):
	def __init__(self, title):
		self.title = title
		self.priority = self.OperationPriorityHighest

	def __str__(self):
		return "set title '"+self.title+"'"

	def run(self, time):
		global logger
		logger.info(str(time)+ ' set title: '+self.title)
		op('/project/title/text').text = self.title

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
	gapDeadline = 0.1
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
		return "{:02}:{:02}:{:02}.{:02} ({:.3f})".format(hr, min, sec, frac, main.timeFunc())

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
		gapStartTime, gapEndTime = self.hasTimelineGap(event)
		#if self.hasTimelineGap(event):
		if gapStartTime:
			logger.warning('inserting dummy event')
			dummyEvent = self.getDummyEvent(gapStartTime, gapEndTime)
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

	def getPrevScheduledEvent(self, event):
		if len(self.scheduledEvents) > 0:
			eventsByStartTime = sorted(self.scheduledEvents, key=lambda e: e.clipStartTime, reverse=True)
			for ev in eventsByStartTime:
				if event.clipStartTime > ev.clipStartTime:
					return ev
		return None

	def hasTimelineGap(self, event):
		logger.debug('checking for timeline gap...')
		nextEvent = self.getNextScheduledEvent(event)
		if not nextEvent:
			logger.warning('no new scheduled event after '+str(event)+'. need a dummy.')
			return (event.clipEndTime, None) #True
		else:
			gap = nextEvent.clipStartTime.toFrames() - event.clipEndTime.toFrames()
			if gap > 1:
				logger.warning('timeline gap detected: '+str(gap)+' frames (between events '+str(event.id)+' and '+str(nextEvent.id)+')')
				return (event.clipEndTime, nextEvent.clipStartTime) # True
		return (None, None) # False

	def getDummyEvent(self, startTime, endTime):
		startTimeStr = str(startTime) if startTime else "00:00:00:00"
		endTimeStr = str(endTime) if endTime else "23:59:59:00"
		dummyEvent = DummyEvent(startTimeStr, endTimeStr)
		dummyEvent.openEnded = (endTime == None)
		return dummyEvent

	def processEvent(self, event, res):
		global logger
		if isinstance(event, EndEvent):
			if self.startTime:
				logger.info('end event received: '+str(event))
				self.timeline.scheduleOperations(self.clipMaxTime+2, [DispatchOperation(self.cleanupCurrentRun)])
		else:
			if event:
				if isinstance(event, StartEvent):
					secondsFromNow = event.startTime - int(time.time())
					if secondsFromNow <= 0:
						logger.warning('received start time is in the past (bad NTP sync?)')
						return
					self.startTime = main.timeFunc()+secondsFromNow
					logger.info('received start event. start time is at '+str(self.startTime)+'('+str(self.startTime-main.timeFunc())+' seconds from now)')
				# if event.id == 1 and self.startTime == None:
					# self.startTime = main.timeFunc()+self.preloadTime
					# logger.debug('first event is '+str(event.id)+'. start time is at '+str(self.startTime)+'('+str(self.startTime-main.timeFunc())+' seconds from now)')
				if self.startTime:
					if (event.channel == 'V' or event.channel == 'AA/V') \
					and (event.videoUrl != None):
						logger.debug('processing event '+str(event))
						self.scheduleOnResource(event, res)
						self.lastEventClipEndTime = event.clipEndTime
					else:
						self.dispatchEvent(event)
				else:
					logger.warning('received event, but it\'s is not 1. processing starts with event ID 1. sorry. received: '+str(event))

	def scheduleOnResource(self, event, res):
		global logger
		nowSec = main.timeFunc()
		logger.info(str(nowSec)+" scheduling event "+str(event)+" on resource "+str(res.compPath))

		prevEvent = self.getPrevScheduledEvent(event)
		lastDummy = prevEvent if isinstance(prevEvent, DummyEvent) else None #self.scheduledEvents[0] if len(self.scheduledEvents) > 0 and isinstance(self.scheduledEvents[0], DummyEvent) else None
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
			# but check that it's not earlier than preload operation
			logger.info(str(nowSec)+" playback start at "+str(t+playbackOffset)+". event will be activated at "+str(t))
			if t+playbackOffset < nowSec:
				logger.info("playback start time ("+str(t+playbackOffset)+") is "+str(nowSec-t-playbackOffset)+" earlier than preload ("+str(nowSec)+"). adjusted to "+str(nowSec))
				self.timeline.scheduleOperationFromNow(0, StartPlaybackOperation(event, res))
			else:
				self.timeline.scheduleOperations(t+playbackOffset, [StartPlaybackOperation(event, res)])
			self.timeline.scheduleOperations(t, [SwitchLiveOperation(res, self.liveSwitch, event, main.onStreamSwitched)])

			# check if the last event was a dummy and release it's resource if it was
			if lastDummy and lastDummy.openEnded:
				logger.info('previous event was open-ended dummy. updating it...')
				self.timeline.scheduleOperations(t, [ReleaseResourceOperation(event, lastDummy.res, self.resMan)])
				self.timeline.removeOperations(lastDummy.releaseTime)
				lastDummy.clipEndTime = event.clipStartTime
				lastDummy.openEnded = False
				main.onDummyUpdate(lastDummy)

			# schedule playback stop - StopPlaybackOperation
			t += event.getClipDuration()
			self.timeline.scheduleOperations(t, [StopPlaybackOperation(event, res)])

			# schedule resource release
			self.timeline.scheduleOperations(t, [ReleaseResourceOperation(event, res, self.resMan)])
		else: # treat as blackout
			t += event.clipStartTime.toSeconds()
			self.timeline.scheduleOperations(t, [SwitchLiveOperation(res, self.liveSwitch, event, main.onStreamSwitched),\
				StopPlaybackOperation(event, res)])
			t += event.getClipDuration()
			self.timeline.scheduleOperations(t, [ReleaseResourceOperation(event, res, self.resMan)])

			if not isinstance(event, DummyEvent):
				logger.debug('event has no video URL. treated as blackout.')
			else:
				event.releaseTime = t
		
		# setup check for upcoming events and timeline gaps for all scheduled events except dummies
		# the reason why we need to actively check for upcoming events is that at this point, there could
		# no subsequent events, but they may be received in the future. thus, we setup a check in the 
		# future gapDeadline seconds before this event releases
		if not isinstance(event, DummyEvent):
			schedTime = (t-self.gapDeadline) if event.getClipDuration() > self.gapDeadline else (t-event.getClipDuration()/2.)
			self.timeline.scheduleOperations(schedTime, [CheckUpcomingEvent(event)])

		# track overall clip time
		if t > self.clipMaxTime:
			self.clipMaxTime = t

	def dispatchEvent(self, event):
		if isinstance(event, TextEvent):
			self.timeline.scheduleOperations(self.startTime+event.titleStartTime.toSeconds(),\
					[TitleOperation(event.title)])
			self.timeline.scheduleOperations(self.startTime+event.titleEndTime.toSeconds(),\
					[TitleOperation("")])
