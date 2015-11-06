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

logger = None
Operation = me.mod.classes.Operation

################################################
class DispatchOperation(Operation):
	def __init__(self, func):
		self.func = func

	def run(self, t):
		self.func()

class VideoOperation(Operation):
	def __init__(self, ppController):
		self.ppController = ppController

	def run(self):
		pass

class PreloadOperation(VideoOperation):
	def __init__(self, url, ppController):
		super(PreloadOperation,self).__init__(ppController)
		self.url = url		

	def run(self, time):
		global logger
		logger.info(str(time)+' preload operation for '+str(self.ppController.compPath)+' ('+str(self.ppController.ytController.url)+')')
		self.ppController.url = self.url
		self.ppController.pause = 1
		self.ppController.blackout = 1

class StartPlaybackOperation(VideoOperation):
	def run(self, time):
		global logger
		logger.info(str(time)+' start playback '+str(self.ppController.compPath)+' ('+str(self.ppController.ytController.url)+')')
		self.ppController.pause = 0
		self.ppController.blackout = 0

class StopPlaybackOperation(VideoOperation):
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

	def run(self, time):
		logger.info(str(time)+' release resource '+str(self.res.compPath)+' ('+str(self.res.ytController.url)+')')
		self.resMan.freeResource(self.res)

class SwitchLiveOperation(Operation):
	def __init__(self, res, switch):
		self.res = res
		self.switch = switch

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
		if event and (event.channel == 'V' or event.channel == 'AA/V') \
		and (event.videoUrl != None and event.videoUrl != 'none'):
			logger.debug('processing event '+str(event))
			if self.startTime == None and event.id != 1:
				logger.warn("event processing hasn't started (event #1 was never received)")
			else:
				if event.id == 1:
					self.startTime = time.time()
				self.scheduleOnResource(event, res)

	def scheduleOnResource(self, event, res):
		global logger
		logger.info("scheduling event "+str(event)+" on resource "+str(res.compPath))
		self.resMan.occupyResource(res)

		t = 0
		# schedule preloading
		# hack for starttime
		videoUrl = event.videoUrl+"?t={0:.1f}".format(event.clipStartTime.toSeconds())
		self.timeline.scheduleOperationFromNow(t, PreloadOperation(videoUrl, res))

		# schedule playback start
		if event.id == 1:
			t = self.preloadTime
		else:
			t += self.startTime + event.clipStartTime.toSeconds()
		self.timeline.scheduleOperations(t, [StartPlaybackOperation(res)])
		self.timeline.scheduleOperations(t, [SwitchLiveOperation(res, self.liveSwitch)])

		# schedule playback stop
		t += event.getClipDuration()
		self.timeline.scheduleOperations(t, [StopPlaybackOperation(res)])

		# schedule resource release
		self.timeline.scheduleOperations(t, [ReleaseResourceOperation(res, self.resMan)])
