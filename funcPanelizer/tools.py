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
		
def drawRectangle(rect,steelFrame,flip):
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
	#drawRectangle(frame,steelFrame,flip)
	
	if len(steelFrame.Windows)>0:                           #Gets the information about windows and doors
		windows=[list(map(float,w.split(','))) for w in steelFrame.Windows]		
		windows=sorted(windows,key=lambda x:x[0])		
		for i,w in enumerate(windows):						#Adds the offsets and joints space to the windows and doors
			of=offSets['Doors'] if w[1]==0 else offSets['Windows']
			windows[i]=[w[0]+of,w[1] if w[1]==0 else w[1]+of,w[2]-2*of,w[3]-of if w[1]==0 else w[3]-2*of]
	else:
		windows=[]
	
	j=offSets['Joints'] #Joints space
	rectangles=[]
	
	def createRectangles(fr):
		"""
		Recursive function that divides the received rectangle in two rectangles
		fr: receives an object of the class Rectangle (the frame)
		"""
		#windows inside the frame
		winInt=[w for w in windows if fr.vertI.x<=w[0] and fr.vertI.x+fr.Length>=w[0]+w[2] and fr.vertI.z<=w[1] and fr.vertI.z+fr.Height>=w[1]+w[3]]	
		winInt=sorted(winInt,key=lambda x:x[0])
				
		if len(winInt)>0: #If the frame contains windows
			if fr.vertI.x<winInt[0][0]: #If there is no window on the left side
				sFL=Rectangle()  #Subframe on the left side
				for c in ['x','y','z']:
					setattr(sFL.vertI,c,getattr(fr.vertI,c))
				setattr(sFL,'Height',fr.Height)
				setattr(sFL,'Length',winInt[0][0]-sFL.vertI.x)
				
				sFR=Rectangle() #Subframe on the right side
				for c in ['y','z']:
					setattr(sFR.vertI,c,getattr(fr.vertI,c))
				setattr(sFR.vertI,'x',winInt[0][0])
				setattr(sFR,'Height',fr.Height)
				setattr(sFR,'Length',fr.Length-sFL.Length)
				
				rectangles.append(sFL)
				createRectangles(sFR)				
			
							
			elif fr.vertI.x==winInt[0][0]: #If there is a window on the left side				
				sFR=Rectangle() #Subframe on the right side
				for c in ['y','z']:
					setattr(sFR.vertI,c,getattr(fr.vertI,c))
				setattr(sFR.vertI,'x',winInt[0][0]+winInt[0][2])
				setattr(sFR,'Height',fr.Height)
				setattr(sFR,'Length',fr.Length-winInt[0][2])
				createRectangles(sFR)
				
				sFT=Rectangle()  #Subframe on the top side
				for c in ['x','y']:
					setattr(sFT.vertI,c,getattr(fr.vertI,c))
				setattr(sFT.vertI,'z',winInt[0][1]+winInt[0][3])
				setattr(sFT,'Height',fr.vertI.z+fr.Height-sFT.vertI.z)
				setattr(sFT,'Length',winInt[0][2])
				createRectangles(sFT)
				
				if winInt[0][1]>0:
					sFB=Rectangle()  #Subframe on the bottom side
					for c in ['x','y','z']:
						setattr(sFB.vertI,c,getattr(fr.vertI,c))
					setattr(sFB,'Height',winInt[0][1]-fr.vertI.z)
					setattr(sFB,'Length',winInt[0][2])
					createRectangles(sFB)
		else:
			rectangles.append(fr)
			
			
		
	
	createRectangles(frame)
	for r in rectangles:
		drawRectangle(r,steelFrame,flip)
