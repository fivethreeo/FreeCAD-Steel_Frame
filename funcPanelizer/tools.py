import os
from itertools import groupby

import FreeCAD, Draft, Arch


fileDir=os.path.dirname(FreeCAD.ActiveDocument.FileName)
fileName=os.path.splitext(os.path.basename(FreeCAD.ActiveDocument.FileName))[0]
#Path to the user Interface
funcDir = os.path.dirname(__file__)
pathUI=os.path.join(funcDir, "panelizeFrameSettings.ui")


class Rectangle(object):
	def __init__(self):
		self.Length=0
		self.Height=0		
		self.vertI=FreeCAD.Vector()
		self.Label=''
		
def convertToRectangle(lis):
	"""
	Convert a list with coordinates to a rectangle object
	"""
	rectList=[]
	for e in lis:
		subF=Rectangle()			
		subF.vertI=FreeCAD.Vector(tuple(e[0]))
		subF.Length=e[1][0]
		subF.Height=e[1][1]
		rectList.append(subF)
	return rectList

		
def drawPanel(rect,steelFrame,flip, thick, material=None):
	"""
	Draws the panel on the steelFrame
	"""
	orienX=steelFrame.Placement.Rotation.multVec(FreeCAD.Vector(1,0,0))
	if flip==0:
		place = steelFrame.Placement.Base.add(orienX.multiply(rect.vertI.x))
	else:
		place = steelFrame.Placement.Base.add(orienX.multiply(rect.vertI.x+rect.Length))		
	orienZ=steelFrame.Placement.Rotation.multVec(FreeCAD.Vector(0,0,1))
	place = place.add(orienZ.multiply(rect.vertI.z))
	if flip==1:
		vectorWidth=steelFrame.Placement.Rotation.multVec(FreeCAD.Vector(0,1,0))		
		place=place.add(vectorWidth.multiply(steelFrame.Width))	
	ro=FreeCAD.Rotation(0,0,90)
	if flip==1:
		ro=FreeCAD.Rotation(180,0,90)
	rot=steelFrame.Placement.Rotation.multiply(ro)	
	
	Rect=Draft.makeRectangle(rect.Length, rect.Height, placement=FreeCAD.Placement(place, rot))
	panel = Arch.makePanel(Rect, thickness=thick)
	if material:	
		panel.Material=material
	return panel
	
	
def mergeAdjacentRect(adj):
	"""
	Merges the adjacent rectangles received in the list adj
	Receives the list adj with the adjacent rectangles
	Returns one rectangle
	"""
	adj=sorted(adj,key=lambda x: x.vertI.x)
	rec=Rectangle()
	for c in ['x','y','z']:
		setattr(rec.vertI,c,getattr(adj[0].vertI,c))
		setattr(rec,'Height',adj[0].Height)
		setattr(rec,'Length',adj[-1].vertI.x+adj[-1].Length-adj[0].vertI.x)
	return rec
		
def divideFrame(steelFrame,offSets,flip):
	"""
	Divides the frame into rectangles 
	Parameters:
		-steelFrame: (obj) the steelFrame object
		-offsets: (dict) with the offsets
		-flip: (boolean)
	"""
	frame=Rectangle() #Creates a rectangle for the frame
	offSetLeft=offSets['Left']
	offsetRight=offSets['Right']
	if flip==1:
		offSetLeft,offsetRight=offsetRight,offSetLeft
	frame.vertI=FreeCAD.Vector(-offSetLeft,0,-offSets['Bottom'])
	frame.Length=steelFrame.Length.Value+offSetLeft+offsetRight
	frame.Height=steelFrame.Height.Value+offSets['Top']+offSets['Bottom']
	
	
	if len(steelFrame.Windows)>0:                        #Gets the information about windows and doors
		if steelFrame.Windows[0]!='':
			windows=[list(map(float,w.split(','))) for w in steelFrame.Windows]		
			windows=sorted(windows,key=lambda x:x[0])		
			for i,w in enumerate(windows):						#Adds the offsets and joints space to the windows and doors
				of=offSets['Doors'] if w[1]==0 else offSets['Windows']
				windows[i]=[w[0]+of,w[1] if w[1]==0 else w[1]+of,w[2]-2*of,w[3]-of if w[1]==0 else w[3]-2*of]
		else:
			windows=[]
	else:
		windows=[]
	
	j=offSets['Joints'] #Joints space
	rectangles=[]
	
	def createRectangles(fr):
		"""
		Recursive function that divides the received rectangle in two or more rectangles
		fr: receives an object of the class Rectangle (the frame)
		It appends the final rectangles into the list rectangles
		"""
		#windows inside the frame
		winInt=[w for w in windows if fr.vertI.x<=w[0] and fr.vertI.x+fr.Length>=w[0]+w[2] and fr.vertI.z<=w[1] and fr.vertI.z+fr.Height>=w[1]+w[3]]
		#Windows in the middle of two frames
		winRight=[w for w in windows if fr.vertI.x<=w[0] and w[0]<=fr.vertI.x+fr.Length<w[0]+w[2] and fr.vertI.z<=w[1] and fr.vertI.z+fr.Height>=w[1]+w[3]]
		for wR in winRight:
			winInt.append([wR[0],wR[1],fr.vertI.x+fr.Length-wR[0],wR[3]])
		winLeft=[w for w in windows if w[0]<fr.vertI.x<w[0]+w[2] and fr.vertI.z<=w[1] and fr.vertI.z+fr.Height>=w[1]+w[3]]
		for wL in winLeft:
			if wL[0]+wL[2]<fr.vertI.x+fr.Length:
				winInt.append([fr.vertI.x,wL[1],wL[0]+wL[2]-fr.vertI.x,wL[3]])
			else:
				winInt.append([fr.vertI.x,wL[1],fr.Length,wL[3]])
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
				if fr.Length-winInt[0][2]>0:						
					sFR=Rectangle() #Subframe on the right side
					for c in ['y','z']:
						setattr(sFR.vertI,c,getattr(fr.vertI,c))
					setattr(sFR.vertI,'x',winInt[0][0]+winInt[0][2])
					setattr(sFR,'Height',fr.Height)
					setattr(sFR,'Length',fr.Length-winInt[0][2])
					createRectangles(sFR)
				
				if fr.vertI.z+fr.Height-winInt[0][1]+winInt[0][3]>0:
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
	#Merge the adjacent rectangles with the same height
	rect=[]
	rectangles=sorted(rectangles,key=lambda x:(x.vertI.z, x.Height))
	groups = groupby(rectangles, lambda x: (x.vertI.z, x.Height))
	for key, group in groups:
		g=list(group)
		if len(g)==1:
			rect.append(g[0])
		else:
			g=sorted(g,key=lambda x: x.vertI.x)
			adjacent=[]
			for i in range(len(g)-1):
				if g[i+1].vertI.x==g[i].vertI.x+g[i].Length:
					adjacent.append(g[i+1])
					if g[i] not in adjacent:
						adjacent.append(g[i])
				else:					
					if i+2 == len(g):
						rect.append(g[i+1])			
					if len(adjacent)==0:
						rect.append(g[i])
					else:
						rect.append(mergeAdjacentRect(adjacent))
						adjacent=[]	
						
			if len(adjacent)>1:
				rect.append(mergeAdjacentRect(adjacent))
				
	return rect						
					
						
	# for r in rect:
		# drawRectangle(r,steelFrame,flip)
		
def groupPanelPieces(panelPiece, steelFrame):
	"""
	This function groups the panel pieces recently created
	It creates the group inside the parent group if it exists
	otherwise directly into the document
	"""
	doc = FreeCAD.ActiveDocument
	if len(steelFrame.InList) == 1:		
		parentGroup = steelFrame.InList[0]
		if parentGroup.Label == str(steelFrame.Label) + "Panels":
			groupPanels = parentGroup
		else:
			groupPanels = doc.addObject("App::DocumentObjectGroup","Group")
			parentGroup.addObject(groupPanels)
			groupPanels.addObject(steelFrame)
			groupPanels.Label = str(steelFrame.Label) + "Panels"
	else:
		groupPanels = doc.addObject("App::DocumentObjectGroup","Group")
		groupPanels.Label = str(steelFrame.Label) + "Panels"
		groupPanels.addObject(steelFrame)
	groupPanels.addObject(panelPiece)
	
def assemblyName(steelFrame):
	"""
	Concatenates the Frame label with the Assembly label if exists
	"""
	label=''
	sFGroup = steelFrame.InList[0]
	if len(sFGroup.InList)==1:
		label = sFGroup.InList[0].Label+'_'
	label += steelFrame.Label
	return label
