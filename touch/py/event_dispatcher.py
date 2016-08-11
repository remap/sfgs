#
#	event_dispatcher.py
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

import logging 
import time
import main

logger = None

class EventDispatcher(object):
	def __init__(self):
		self.eventsQueue = []

	def onNewEvent(self, event):
		global logger
		logger.debug('new event received: '+str(event)+' queue len '+str(len(self.eventsQueue)))
		self.addEventToDB(event)
		self.eventsQueue.append(event)

	def addEventToDB(self, event):
		now = round(main.timeFunc()*100)/100
		dbDat = op('events_timeline')
		if dbDat:
			channel = event.channel if hasattr(event, 'channel') else 'n/a'
			vals = [now, event.id, channel, event.clipStartTime, event.clipEndTime, event.ytUrl, event.videoUrl]
			dbDat.insertRow(vals, 1)

	def popUpcomingEvent(self):
		if len(self.eventsQueue) > 0:
			eventsByStartTime = sorted(self.eventsQueue, key=lambda e: e.clipStartTime, reverse=False)
			upcoming = eventsByStartTime[0]
			del eventsByStartTime[0]
			self.eventsQueue = eventsByStartTime
			return upcoming
		return None