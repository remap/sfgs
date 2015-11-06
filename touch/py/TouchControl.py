#
#	TouchControl.py
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

################################################################################
class TouchController(object):
	def __init__(self, copmonentPath, opFunc, rootVar):
		self.compPath = copmonentPath
		self.op = opFunc(self.compPath)
		self.opFunc = opFunc
		self.root = rootVar
		if not self.op:
			raise NameError("couldn't find OP with path %s", self.compPath)
	
	def setAttr(self, param, value):
		setattr(self.op, param, value)

	@staticmethod
	def loadTox(opFunc, rootVar, containerPath, toxPath):
		return opFunc(containerPath).loadTox(root.mod.path.toxes+toxPath)

################################################################################
class ControllableComp(TouchController):
	"""
	Base class for touch components that have 'controls' constant CHOP
	inside for control. Class attributes' names correspond to the 
	channel names in channelNames array
	Component should also have defaults CHOP for default values
	"""
	channelNames = []
	def __init__(self, copmonentPath, opFunc, rootVar):
		TouchController.__init__(self, copmonentPath, opFunc, rootVar)
		self.op = opFunc(self.compPath)
		self.opControls = opFunc(self.compPath+'/controls')
		self.opDefaults = opFunc(self.compPath+'/defaults')
		if not self.opControls:
			raise NameError("couldn't find 'controls' CHOP inside component (%s)", self.compPath)

	def __setattr__(self, name, value):
		if name in self.channelNames:
			self.setControlsParam(name, value)
		else:
			object.__setattr__(self, name, value)

	def __getattr__(self, name):
		if name in self.channelNames:
			return self.getControlsParam(name)
		else:
			print('no such attribute '+name)
			raise AttributeError #return super().__getattr__(self, name)

	def getChopValueName(self, chop, paramName):
		try:
			controlValueName = 'value'+str(chop[paramName].index)
			return controlValueName
		except Exception as e:
			raise NameError('exception while getting value %s from chop %s: %s', paramName, chop, e)

	def setControlsParam(self, paramName, value):
		controlValueName = self.getChopValueName(self.opControls, paramName)
		getattr(self.opControls.par, controlValueName).val = value

	def getControlsParam(self, paramName):
		controlValueName = self.getChopValueName(self.opControls, paramName)
		return getattr(self.opControls.par, controlValueName).val

	def pulseControlParam(self, paramName):
		controlValueName = self.getChopValueName(self.opControls, paramName)
		getattr(self.opControls.par, controlValueName).pulse(frames=5)

	def getDefaultValue(self, paramName):
		if self.opDefaults:
			defaultValueName = self.getChopValueName(self.opDefaults, paramName)
			return getattr(self.opDefaults.par, defaultValueName).val

	def resetToDefaults(self):
		if self.opDefaults:
			for chanName in self.channelNames:
				value = self.getDefaultValue(chanName)
				self.setControlsParam(chanName, value)

	def loadParams(self, params, paramNames):
		if 'reset' in params.keys() and params['reset'] == True:
			self.resetToDefaults()
		for paramName in params:
			if paramName in paramNames:
				value = params[paramName]
				self.__setattr__(paramName, value)

################################################################################
class YoutubeController(ControllableComp):
	""" 
	Represents Youtube TouchDesigner component and provides simple 
	python interface for controlling it 
	"""
	channelNames = [
		"pause",
		"loop",
		"seek",
		"switchOnCue",
		"cue",
		"playbackSpeed",
		"startTime",
		"blackout",
		"reload",
		"thumbnail"
	]
	exChannelNames = channelNames + ['url', 'videoUrl', 'thumbnailUrl']
	filePath = 'yt.tox'

	def __init__(self, componentPath, opFunc, rootVar):
		ControllableComp.__init__(self, componentPath, opFunc, rootVar)
		self.urlDatOp = opFunc(componentPath+'/serviceUrl')
		self.videoUrlDatOp = opFunc(componentPath+'/videoUrl')
		self.thumbnailUrlDatOp = opFunc(componentPath+'/thumbnailUrl')
		if not self.urlDatOp or not self.videoUrlDatOp:
			raise NameError("couldn't video URL OP inside youtube copmonent: %s",\
			 self.compPath)
		# workaround for touch failure of creating connection b/w url, videoUrl and youtube TOX
		self.fixConnections() 

	def fixConnections(self):
		youtubeTox = self.opFunc(self.compPath+'/youtube')
		if youtubeTox:
			self.urlDatOp.outputConnectors[0].connect(youtubeTox.inputConnectors[0])
			self.videoUrlDatOp.outputConnectors[0].connect(youtubeTox.inputConnectors[2])
			self.thumbnailUrlDatOp.outputConnectors[0].connect(youtubeTox.inputConnectors[3])

	def cue(self):
		self.pulseControlParam('cue')

	def reload(self):
		self.pulseControlParam('reload')

	@property
	def url(self):
		return self.urlDatOp.text
	@url.setter
	def url(self, val):
		self.urlDatOp.text = val

	@property
	def videoUrl(self):
		return self.videoUrlDatOp.text
	@videoUrl.setter
	def videoUrl(self, val):
		self.videoUrlDatOp.text = val

	def resetToDefaults(self):
		super().resetToDefaults()
		self.url = ''
		self.videoUrl = ''
		self.thumbnailUrl = ''

	@property
	def thumbnailUrl(self):
		return self.thumbnailUrlDatOp.text
	@thumbnailUrl.setter
	def thumbnailUrl(self, val):
		self.thumbnailUrlDatOp.text = val

	@staticmethod
	def instantiate(containerPath, opFunc, rootVar):
		comp = YoutubeController.loadTox(opFunc, rootVar, containerPath, YoutubeController.filePath)
		yt = YoutubeController(comp.path, opFunc, rootVar)
		return yt

################################################################################
class PostprocController(ControllableComp):
	"""
	Represents postprocessing component and provides simple pyhton interface 
	for controlling it
	"""
	channelNames = [
		"cropLeft",
		"cropRight",
		"cropTop",
		"cropBottom",
		"circleCrop",
		"scaleCrop",
		"originX",
		"originY",
		"scaleX",
		"scaleY",
		"vignetteEdge",
		"rotate",
		"invert",
		"blackLevel",
		"gamma",
		"brightness",
		"contrast",
		"opacity",
		"blackout",
		"lowRed",
		"highRed",
		"lowGreen",
		"highGreen",
		"lowBlue",
		"highBlue",
		"monochrome",
		"mirrorX",
		"mirrorY",
		"ripple"
	]
	filePath = 'pp.tox'

	def __init__(self, compPath, opFunc, rootVar):
		ControllableComp.__init__(self, compPath, opFunc, rootVar)

	@staticmethod
	def instantiate(containerPath, opFunc, rootVar):
		comp = PostprocController.loadTox(opFunc, rootVar, containerPath, PostprocController.filePath)
		pp = PostprocController(comp.path, opFunc, rootVar)
		return pp

################################################################################
class YtPipelineController(TouchController):
	channelNames = YoutubeController.channelNames + PostprocController.channelNames
	filePath = 'yt-pipeline.tox'
	ytController = None
	ppController = None

	def __init__(self, compPath, opFunc, rootVar):
		TouchController.__init__(self, compPath, opFunc, rootVar)
		self.ytController = YoutubeController(compPath+'/yt', opFunc, rootVar)
		self.ppController = PostprocController(compPath+'/pp', opFunc, rootVar)

	def __setattr__(self, name, value):
		if name in PostprocController.channelNames:
			self.ppController.__setattr__(name, value)
		elif name in YoutubeController.exChannelNames:
			self.ytController.__setattr__(name, value)
		else:
			object.__setattr__(self, name, value)

	def __getattr__(self, name):
		if name in PostprocController.channelNames:
			return self.ppController.__getattr__(name)
		elif name in YoutubeController.exChannelNames:
			return self.ytController.__getattr__(name)
		else:
			object.__getattribute__(self, name)

	def pipeline(self):
		return {'yt':self.ytController, 'pp':self.ppController}

	def loadParams(self, params):
		self.ytController.loadParams(params, YoutubeController.exChannelNames)
		self.ppController.loadParams(params, PostprocController.channelNames)

	@staticmethod
	def instantiate(containerPath, opFunc, rootVar):
		comp = YtPipelineController.loadTox(opFunc, rootVar, containerPath, YtPipelineController.filePath)
		pipeline = YtPipelineController(comp.path, opFunc, rootVar)
		return pipeline

################################################################################
class SwitchController(ControllableComp):
	"""
	Represents switch component TOX
	"""
	channelNames = [
		"nInputs",
		"blendIn1",
		"blendIn2",
		"blend"
	]
	filePath = 'switch.tox'

	def __init__(self, componentPath, opFunc, rootVar):
		ControllableComp.__init__(self, componentPath, opFunc, rootVar)

	@staticmethod
	def instantiate(containerPath, opFunc, rootVar):
		comp = SwitchController.loadTox(opFunc, rootVar, containerPath, SwitchController.filePath)
		s = SwitchController(comp.path, opFunc, rootVar)
		return s

################################################################################
class StreamingResourceAllocator(ControllableComp):
	"""
	Represents resource allocator component TOX
	"""
	channelNames = [
		"nResources"
	]
	filePath = 'resource-allocator.tox'

	def __init__(self, componentPath, opFunc, rootVar):
		ControllableComp.__init__(self, componentPath, opFunc, rootVar)

	def getResources(self):
		resources = []
		pipelines = ops(self.compPath+'/pipeline*')
		for pp in pipelines:
			p = YtPipelineController(pp.path, op, root)
			resources.append(p)
		return resources

	@staticmethod
	def instantiate(containerPath, opFunc, rootVar):
		comp = StreamingResourceAllocator.loadTox(opFunc, rootVar, containerPath, StreamingResourceAllocator.filePath)
		s = StreamingResourceAllocator(comp.path, opFunc, rootVar)
		return s

################################################################################
# NOT USED IN SFGS
################################################################################
class GenericController(ControllableComp):
	"""
	Represents generic patch wich has two pipelines - active and preview and 
	implements switching logic between these pipelines
	"""
	filePath = '/TOXes/generic.tox'
	activeStorage = 'active_pipeline'
	previewStorage = 'preview_pipeline'
	outSwitchComp = '/outSwitch'

	def __init__(self, compPath, opFunc, rootVar):
		ControllableComp.__init__(self, compPath, opFunc, rootVar)
		self.outSwitch = opFunc(compPath+'/outSwitch')
		self.feedPipeline = opFunc(self.compPath+'/feedPipeline')
		self.yt1 = YoutubeController(compPath+'/pipeline1/yt', opFunc, self.root)
		self.yt2 = YoutubeController(compPath+'/pipeline2/yt', opFunc, self.root)
		self.pp1 = PostprocController(compPath+'/pipeline1/pp', opFunc, self.root)
		self.pp2 = PostprocController(compPath+'/pipeline2/pp', opFunc, self.root)
		if not (self.yt1 or self.yt2 or self.pp1 or self.pp2):
			raise Exception("coudln't initialize generic controller. check generic.tox")
		#self.outSwitch.par.index.val = 1
		#self.feedPipeline.allowCooking = 0
		self.defaultActive = {'yt':self.yt1, 'pp':self.pp1, 'idx':0}
		self.defaultPreview = {'yt':self.yt2, 'pp':self.pp2, 'idx':1}

	def getStoredController(self, storageName, controllerKey, default):
		controllers = self.op.fetch(storageName, default)
		if controllerKey in controllers.keys():
			return controllers[controllerKey]
		else:
			return None

	def getActivePipeline(self):
		return self.op.fetch(self.activeStorage, self.defaultActive)

	def getPreviewPipeline(self):
		return self.op.fetch(self.previewStorage, self.defaultPreview)

	def activeYt(self):
		return self.getStoredController(self.activeStorage, 'yt', self.defaultActive)

	def activePp(self):
		return self.getStoredController(self.activeStorage, 'pp', self.defaultActive)

	def previewYt(self):
		return self.getStoredController(self.previewStorage, 'yt', self.defaultPreview)

	def previewPp(self):
		return self.getStoredController(self.previewStorage, 'pp', self.defaultPreview)

	def switch(self, val = 1):
		"""
		If value is present, blends active and preview. 
		If value is 1, switches active and preivew controllers
		"""
		activePipeline = self.getActivePipeline()
		previewPipeline = self.getPreviewPipeline()
		if val >= 1:
			self.op.store(self.activeStorage, previewPipeline)
			self.op.store(self.previewStorage, activePipeline)
		switchValue = val if activePipeline['idx'] == 0 else 1-val
		self.setControlsParam('switch', switchValue)

	@staticmethod
	def instantiate(containerPath, opFunc, rootVar):
		comp = GenericController.loadTox(opFunc, rootVar, containerPath, GenericController.filePath)
		generic = GenericController(comp.path, opFunc, rootVar)
		return generic

################################################################################
class ComposerController(ControllableComp):
	compositeComp = '/composite'

	def __init__(self, compPath, opFunc, rootVar):
		ControllableComp.__init__(self, compPath, opFunc, rootVar)
		self.pipeline1 = YtPipelineController(compPath+'/pipeline1/pipeline', opFunc, rootVar)
		self.pipeline2 = YtPipelineController(compPath+'/pipeline2/pipeline', opFunc, rootVar)
		self.compositeOp = opFunc(self.compPath+self.compositeComp)
		if not (self.pipeline1 and self.pipeline2 and self.compositeOp):
			raise Exception("coudln't initialize composer controller")

	def setComposite(self, composite):
		self.compositeOp.par.operand = composite

	@property 
	def comp(self):
		return self.compositeOp.par.operand.val
	@comp.setter
	def comp(self, value):
		self.compositeOp.par.operand = value

	def loadParams(self, params):
		print('loading composer params: '+str(params))
		composite = params['comp'] if 'comp' in params.keys() else None
		ppParams1 = params['pipeline1'] if 'pipeline1' in params.keys() else {}
		ppParams2 = params['pipeline2'] if 'pipeline2' in params.keys() else {}
		if composite:
			self.comp = composite
		self.pipeline1.loadParams(ppParams1)
		self.pipeline2.loadParams(ppParams2)


################################################################################
class FeedController(GenericController):
	"""
	Represents patch wich has two pipelines - yt-pipeline and video feed pipeline
	which are composited using comp TOP
	"""
	filePath = '/TOXes/polaroids.tox'
	compositeComp = '/composite'

	def __init__(self, compPath, opFunc, rootVar):
		GenericController.__init__(self, compPath, opFunc, rootVar)
		self.compOp = opFunc(self.compPath+self.compositeComp)
		self.feedPp = PostprocController(compPath+'/feedPipeline/pp', opFunc, rootVar)
		self.cameraInOp = opFunc(self.compPath+'/feedPipeline/cameraIn')
		if not (self.feedPp and self.compOp):
			raise Exception("couldn't initialize feed controller. check polaroids tox")
		self.feedOn = 1
		self.feedPipeline.allowCooking = 1

	@property 
	def comp(self):
		return self.compOp.par.operand.val
	@comp.setter
	def comp(self, value):
		self.compOp.par.operand = value

	@property
	def feedOn(self):
		return (self.outSwitch.par.index == 1)

	@feedOn.setter
	def feedOn(self, value):
		if value:
			self.outSwitch.par.index.val = 1
			self.feedPipeline.allowCooking = 1
		else:
			self.outSwitch.par.index.val = 0
			self.feedPipeline.allowCooking = 0

	@property 
	def cameraInput(self):
		return self.cameraInOp.par.library.val

	@cameraInput.setter
	def cameraInput(self, value):
		self.cameraInOp.par.library.val = value

################################################################################
class DoorController(ControllableComp):
	channelNames = [
		"x",
		"y",
		"width",
		"height",
		"rotate",
		"textSize",
		"scale"
	]
	exChannelNames = channelNames + ["tagText"]
	def __init__(self, componentPath, opFunc, rootVar):
		ControllableComp.__init__(self, componentPath, opFunc, rootVar)
		self.tagTextOp = opFunc(componentPath+'/tagText')
		if not self.tagTextOp:
			raise NameError("couldn't find tag text OP inside door copmonent: %s",\
			 self.compPath)

	@property
	def tagText(self):
		return self.tagTextOp.text
	@tagText.setter
	def tagText(self, val):
		self.tagTextOp.text = val

	def loadParams(self, params):
		super().loadParams(params, self.exChannelNames)

################################################################################
class ThumbGeneratorController(ControllableComp):
	channelNames = [
		"x",
		"y",
		"width",
		"height",
		"rotate",
		"textSize",
		"scale",
		"gridWidth",
		"gridHeight",
		"gridRows",
		"gridCols",
		"birthRate",
		"life",
		"velocity",
		"reset",
		"turbulence"
	]
	exChannelNames = channelNames + ['thumbUrls']

	def __init__(self, componentPath, opFunc, rootVar):
		ControllableComp.__init__(self, componentPath, opFunc, rootVar)
		self.urlsTableOp = opFunc(componentPath+'/texArrayUrls')
		if not self.urlsTableOp:
			raise NameError("couldn't find urls table OP inside thumb generator controller")

	@property
	def thumbUrls(self):
		return self.urlsTableOp.text
	@thumbUrls.setter
	def thumbUrls(self, value):
		self.urlsTableOp.text = value

################################################################################
class QueensGuardController(ControllableComp):
	channelNames = [
		"birth_rate",
		"life",
		"displace",
		"scale",
		"zero_doors",
		"doors",
		"16_9",
		"instance",
		"ndoors",
		"thumbsActive",
		"gridRows",
		"gridCols",
		"gridWidth",
		"gridHeight",
		"velocity",
		"trubulence"
	]
	exChannelNames = channelNames + ["urlsTable"]
	def __init__(self, componentPath, opFunc, opsFunc, rootVar):
		ControllableComp.__init__(self, componentPath, opFunc, rootVar)
		self.opsFunc = opsFunc
		self.urlsTableOp = opFunc(componentPath+'/urlsTable')
		self.particlesControls = opFunc(componentPath+'/pgControls')
		self.thumbGenerator = ThumbGeneratorController(componentPath+'/thumbGenerator', opFunc, rootVar)
		self.thumbControls = opFunc()
		self.composerControllers = []
		self.doorControllers = []
		self.loadComposers()
		self.loadDoors()
		# if not self.urlsTableOp:
		# 	raise NameError("couldn't find urls table OP inside queens guard copmonent: %s",\
		# 	 self.compPath)

	def loadComposers(self):
		self.composerControllers = []
		composerOps = self.opsFunc(self.compPath+'/doorUi/py_composer*')
		if len(composerOps):
			for cOp in composerOps:
				composer = ComposerController(cOp.path, self.opFunc, self.root)
				if composer:
					self.composerControllers.append(composer)
				else:
					print('no composer at path '+cOp.path)

	def loadDoors(self):
		self.doorControllers = []
		doorOps = self.opsFunc(self.compPath+'/doorUi/py_door*')
		if len(doorOps):
			for doorOp in doorOps:
				door = DoorController(doorOp.path, self.opFunc, self.root)
				if door:
					self.doorControllers.append(door)
				else:
					print('no door at path '+doorOp.path)

	@property
	def ndoors(self):
		return self.getControlsParam('ndoors')
	@ndoors.setter
	def ndoors(self, val):
		self.setControlsParam('ndoors', val)
		self.loadComposers()
		self.loadDoors()

	@property
	def urlsTable(self):
		return self.urlsTableOp.text
	@urlsTable.setter
	def url(self, val):
		self.urlsTableOp.text = val
