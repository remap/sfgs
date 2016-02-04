#
#	timeline.py
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
from collections import OrderedDict

logger = None

#####################################################################
class Timeline(object):
	operationsQueue = None

	def __init__(self):
		self.operationsQueue = {} #OrderedDict()

	def scheduleOperations(self, absTimeSec, operations):
		global logger
		now = main.timeFunc()
		logger.debug('for '+str(absTimeSec)+' ('+str(absTimeSec-now)+' sec from now) scheduled ops: '+str(operations))
		if (absTimeSec in self.operationsQueue.keys()):
			self.operationsQueue[absTimeSec].extend(operations)
		else:
			self.operationsQueue[absTimeSec] = operations

	def scheduleOperationFromNow(self, seconds, operation):
		global logger
		nowSec = main.timeFunc()
		self.scheduleOperations(nowSec+seconds, [operation])
		return nowSec

	def removeOperations(self, absTimeSec):
		if absTimeSec in self.operationsQueue.keys():
			del self.operationsQueue[absTimeSec]

	def runOperations(self, operations):
		operationsByPriority = sorted(operations, key=lambda o: o.priority, reverse=False)
		for o in operationsByPriority:
			o.run(main.timeFunc())

	def run(self):
		if len(self.operationsQueue) > 0:
			nowSec = main.timeFunc()
			timePoints = sorted(self.operationsQueue)
			while len(timePoints) > 0 and nowSec >= timePoints[0]:
				t = timePoints[0]
				logger.debug('executing operation'+str(nowSec-t)+' sec later')
				operations = self.operationsQueue[t]
				self.runOperations(operations)
				del self.operationsQueue[t]
				del timePoints[0]
				