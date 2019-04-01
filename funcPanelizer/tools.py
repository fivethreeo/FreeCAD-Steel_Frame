import os
import FreeCAD, Draft

#Path to the user Interface
funcDir = os.path.dirname(__file__)
pathUI=os.path.join(funcDir, "panelizeFrameSettings.ui")


class Rectangle(object):
	def __init__(self):
		self.Length=0
		self.Height=0		
		self.vertI=FreeCAD.Vector()
		# self.listaPiezas=[]
		# self.Label=''
		# self.despArea=0
		# self.despPorc=0
		
def drawRectangle(rect,steelFrame, flip):
	"""
	Draws the rectangle rect over the steelFrame
	"""
	orienX=steelFrame.Placement.Rotation.multVec(FreeCAD.Vector(1,0,0))
	place = steelFrame.Placement.Base.add(orienX.multiply(rect.vertI.x))
	orienZ=steelFrame.Placement.Rotation.multVec(FreeCAD.Vector(0,0,1))
	place = place.add(orienZ.multiply(rect.vertI.z))
	if flip==1:
		vectorWidth=steelFrame.Placement.Rotation.multVec(FreeCAD.Vector(0,1,0))
		place=place.add(vectorWidth.multiply(steelFrame.Width))
	rotE=steelFrame.Placement.Rotation.toEuler()
	rot=FreeCAD.Rotation(rotE[0],rotE[1],rotE[2]+90)
	rect=Draft.makeRectangle(rect.Length, rect.Height, placement=FreeCAD.Placement(place, rot))
		
def divideFrame(steelFrame,offSets,flip):
	"""
	Divides the frame into rectangles 	
	"""
	frame=Rectangle() #Creates a rectangle for the frame
	offSetLeft=offSets['Left']
	offsetRight=offSets['Right']
	if flip==1:
		offSetLeft,offsetRight=offsetRight,offSetLeft
	frame.vertI=FreeCAD.Vector(-offSetLeft,0,-offSets['Bottom'])
	frame.Length=steelFrame.Length.Value+offSetLeft+offsetRight
	frame.Height=steelFrame.Height.Value+offSets['Top']+offSets['Bottom']
	print(frame.vertI)
	print(frame.Length,frame.Height)
	drawRectangle(frame,steelFrame,flip)
	if len(steelFrame.Windows)>0:
		windows=[list(map(float,w.split(','))) for w in steelFrame.Windows]
		windows=sorted(windows,key=lambda x:x[0])
	else:
		windows=[]
	
	
	#def 
		
	
