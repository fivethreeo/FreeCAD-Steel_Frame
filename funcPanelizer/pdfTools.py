import os
import os.path as oP

import matplotlib.pyplot as plt
import matplotlib.patches as patches

import FreeCAD
from .tools import fileDir, fileName

def createPdf(steelFrame, panelPieces, flip, projectName, version, directory, assemblyName, thickness=0, material=None):
	"""
	"""
	fig = plt.figure()
	
	xMin = min([pP.vertI.x for pP in panelPieces])
	xMin = xMin if xMin <= 0 else 0
	xMax = max([pP.vertI.x + pP.Length for pP in panelPieces])
	xMax = xMax if xMax > steelFrame.Length.Value else steelFrame.Length.Value
	yMin = min([pP.vertI.z for pP in panelPieces])
	yMin = yMin if yMin <= 0 else 0
	yMax = max([pP.vertI.z + pP.Height for pP in panelPieces])
	yMax = yMax if yMax > steelFrame.Height.Value else steelFrame.Height.Value
	
	ax1 = fig.add_subplot(111, aspect='equal')
	ax1.set_ylim(yMin,yMax)
	ax1.set_xlim(xMin if flip==0 else xMax, xMax if flip==0 else xMin)
	ax1.tick_params(axis = 'both', which = 'minor', labelsize = 0)
	
	for pP in panelPieces:
		p=patches.Rectangle((pP.vertI.x, pP.vertI.z), pP.Length, pP.Height,facecolor="grey",edgecolor='black',linewidth=1,alpha=0.2)
		ax1.add_patch(p)
		
		### Panel piece Label
		rx, ry = p.get_xy()
		cx = rx + p.get_width()/2.0 #Busca el centro de cada pieza para colocar la etiqueta
		cy = ry + p.get_height()/2.0
		rot=90 if pP.Length<600 and pP.Height>450 else 0
		ax1.annotate(pP.Label, (cx, cy), color='black', fontsize=7, ha='center', va='center', rotation=rot)
		
	#Draws windows
	windows=[list(map(float,w.split(','))) for w in steelFrame.Windows]
	for w in windows:
		if w != '':
			p=patches.Rectangle((w[0], w[1]), w[2], w[3],edgecolor='black',linestyle=':',linewidth=0.5, fill=False)
			ax1.add_patch(p)
			
	# Draws frame if needed
	if any([xMin!=0,xMax != steelFrame.Length.Value,yMin !=0 ,yMax != steelFrame.Height.Value]):
		p=patches.Rectangle((0, 0), steelFrame.Length.Value, steelFrame.Height.Value,edgecolor='black',linestyle=':',linewidth=0.5, fill=False)
		ax1.add_patch(p)
	
	### Adds a legend with the steel Frame information
	legend = r"$\bf{Project: }$"
	legend += projectName if projectName != "" else fileName
	legend += '\n' + r"$\bf{Version: }$" + version
	legend += '\n' + r"$\bf{Assembly: }$" + assemblyName
	
	fig.text(0.1, 0.86, legend, fontsize=8)
	legend = '\t'.expandtabs() + r"$\bf{Panels }$"
	if thickness != 0:
		legend += '\n' + r"$\bf{Thickness: }$" + str(thickness) + " mm"
	if material:
		legend += '\n' + r"$\bf{Material: }$" + material
	fig.text(0.6, 0.86, legend, fontsize=8)
	fig.subplots_adjust(top=0.82)
	##Prefix
	prefix = projectName if projectName != '' else fileName
	prefix += "_v" + version if version != '' else ''	
	##Directory
	if directory == "" or directory == fileDir:		
		newDir = oP.join(fileDir,"sF_Drawings_" + prefix)
		if not os.path.exists(newDir):
			os.makedirs(newDir)			
		directory = newDir
	###Pdf name
	pdfName = oP.join(directory,prefix+"_" + assemblyName + ".pdf")
	FreeCAD.Console.PrintMessage("Saving pdf file...")
	fig.savefig(pdfName, orientation='portrait', papertype='letter')
	FreeCAD.Console.PrintMessage("Pdf file saved as: " + pdfName)
	plt.close()
		
	
