# -*- coding: utf-8 -*-


__Title__ = "Steel Frame Creator"
__Author__ = "Humberto Hassey, Beatriz Arellano"
__Version__ = "00.07"
__Date__ = "2017-12-27"
__Comment__ = "None"
__Web__ = "https://gitlab.com/Oriond/FreeCAD-Steel_Frame"
__Wiki__ = ""
__Icon__ = "/usr/lib/freecad/Mod/plugins/icons/Title_Of_macro"
__IconW__ = "C:/Documents and Settings/YourUserName/Application Data/FreeCAD"
__Help__ = "See Readme.MD on Gitlab"
__Status__ = "Experimental"
__Requires__ = "freecad 0.19"
__Communication__ = \
    "https://forum.freecadweb.org/viewtopic.php?flangeLength=23&t=26092"


import Part
import FreeCAD
App = FreeCAD

def cutStud(stud,
            opening,
            beamHeight,
            isFEMOff=True,
            isBeamOn=False,
            thickness=0.001):

    # This function takes a stud and a window and returns two
    # studs result from substracting the window to the original
    # stud or the same stud if no intersection is present

    studList = []
    if opening[1] == 0: # This is a door
        # Placement of upper opening
        posX = stud[0]
        posZ = opening[3] + thickness * isFEMOff
        posSize = stud[2] - opening[3] - 2 * thickness * isFEMOff
        studList.append((posX, posZ, posSize, stud[3]))
        return studList
    elif opening[1] >= stud[1] + stud[2]: # Stud does not reach the window height
        studList.append(stud)
        return studList
    elif stud[1] > opening[1] + opening[3]: # Stud above window and does not cross window
        studList.append(stud)
        return studList
    elif opening[1] < stud[1] + stud[2] < opening[1] + opening[3]: # Stud inside Structural beam
        hdown = opening[1] - stud[1] + 2 * thickness * (not (isFEMOff))
        posZ = stud[1] - thickness * (not (isFEMOff))
        studList.append((stud[0], posZ, hdown, stud[3]))
        return studList
    else:  # Opening[1]+opening[3] < stud[1]+stud[2]: # Stud passes the window height
        # Placement of lower opening
        hdown = opening[1] - stud[1] + 2 * thickness * (not (isFEMOff))
        posZ = stud[1] - thickness * (not (isFEMOff))
        studList.append((stud[0], posZ, hdown, stud[3]))
        #  Placement of upper opening
        posX = stud[0]
        posZ = opening[1] + opening[3] - thickness * (not (isFEMOff))
        posSize = stud[2] - opening[3] - hdown + 2 * thickness * (
            not (isFEMOff))
        studList.append((posX, posZ, posSize, stud[3]))
        return studList


def calcStuds(length,
              height,
              separation,
              flangeLength,
              windows,
              isFEMOff,
              initialZ=0,
              isBeamOn=False,
              beamHeight=0,
              thickness=0):
    # Function that calculates the length of studs to use for a wall
    # Gets as parameters:
    #     -length: (float) length (x) of the wall
    #     -height: (float) height (z) of the wall
    #     -separation: (float) separation between studs along axis x
    #     -flangeLength: (float) length of the  "flange" of the stud
    #     -windows: List of tuples with the information of the windows, every tupble goes like this:
    #         (position in x, position in z, length in x, height in z)        
    #     -initialZ: (float) Initial position in Z of the studs.
    #     -isBeamOn: (Boolean) If the structural option is selected or not
    #     -beamHeight: Beam height
        
    # Returns a list with tuples with the information of every steel stud:
    #     (px, pz, height, flipped):
    #         px: (float) position along axis x
    #         pz: (float) position along axis z
    #         height: (float) height in z
    #         flipped: (boolean) If the stud goes inverted

    def AddStud(studX, initialZ, height, flipped, studs):
        # Function that adds the studs that encompass windows and doors.
        # If the stud already exists in that position it does not add more.
        if studX not in [stud[0] for stud in studs]:
            studs.append((studX, initialZ, height, flipped))
            # (px,pz,height,flipped)
        return studs

    margin = 2 * flangeLength  #Minimum space between studs
    studs = []
    # Check if there is a window or door on the initial edge to rotate or not the first post.
    if 0 not in [ window[0] for window in windows ]: 
        studs.append((0, initialZ, height, False))
    for window in windows:
        studs = AddStud(window[0], initialZ, height, True, studs)
        studs = AddStud(window[0] + window[2], initialZ, height, False, studs)
        # Add extra studs if structural option is true
        if isBeamOn == True:
            if not any([
                otherWindow[0] < window[0] - 2 * flangeLength <
                otherWindow[0] + otherWindow[2] for otherWindow in windows
            ]):
                studs = AddStud(window[0] - 2 * flangeLength, initialZ, height,
                                False, studs)
            if not any([
                otherWindow[0] < window[0] + window[2] + 2 * flangeLength <
                otherWindow[0] + otherWindow[2] for otherWindow in windows
            ]):
                studs = AddStud(window[0] + window[2] + 2 * flangeLength,
                                initialZ, height, True, studs)
        # Check what happens if the stud already exists and has another orientation
        # Check what happens if that stud passes trough a door or window. Verificar qué pasa si ese poste pasa por una puerta o doors
    if length not in [window[0] + window[2] for window in windows]:
    	# Add the last stud, checking that it is already not added as frame of a door or window.
        studs.append( (length, initialZ, height, True) )  
    studs.sort(key=lambda stud: stud[0])  # Sort studs by position along axis X
    # Add intermediate studs that are not part of the frames
    notFrames = []  #List to add studs that are not frames.
    # Start iterating from the second element of the studs.
    for index, stud in enumerate(studs[1::]):  
        frameDistance = stud[0] - studs[index][0]
        extra = 0
        if frameDistance % separation >= margin and float(
                frameDistance / separation).is_integer() != True:
            extra = 1
        numberOfStuds = int(frameDistance / separation) + extra
        for studNumber in range(1, numberOfStuds):
            notFrames.append((studs[index][0] + studNumber * separation, initialZ,
                              height, False))
        lastSeparation = stud[0] - notFrames[-1][0] if numberOfStuds > 1 else frameDistance
        # If there is a space bigger than the separation between studs
        if lastSeparation > separation and lastSeparation >= margin:  
            notFrames.append((stud[0] - lastSeparation / 2, initialZ, height, False))

    studs += notFrames
    # Studs are defined like this: (px, pz, height, flipped):
    # Cut the studs that go trough windows and doors
    windowCopies = windows[:]
    if isBeamOn:  # If Structural, all Beams will be treated as windows to cut studs below them
        for window in windows:
            xmin = (window[0])
            xmax = (window[0] + window[2])
            windowCopies.append(
                (xmin, height - beamHeight - 1 * thickness, xmax - xmin,
                 2 * beamHeight + 1 * thickness * isFEMOff ))
                 # 2 because I want the window higher than the studs
    for window in windowCopies:  # Stud inside window in x
        interStuds = list(filter(lambda x: window[0] < x[0] < window[0] + window[2], studs))
        for iStu in interStuds:
            studs.remove(iStu)
            studs.extend(
                cutStud(iStu, window, beamHeight, isFEMOff, isBeamOn, thickness))

    studs.sort(key=lambda tup: tup[0])
    return studs


def Draw_Steel_Stud(depth, width, thickness, height, lipWidth=8, flipped=0):
    # Author = Humberto Hassey
    # Version=1.0
    # Draw a Steel stud
    # Width=stud width
    # Depth=stud depth
    # Height=stud height
    # Thickness=steel thickness
    # Select Gauge=0 for custom thickness

    F = 1
    if flipped == 1:
        F = -1
    # Vertices of the stud
    V1 = FreeCAD.Vector(0, 0, 0)
    V2 = FreeCAD.Vector(width * F, 0, 0)
    V3 = FreeCAD.Vector(width * F, lipWidth, 0)
    V4 = FreeCAD.Vector((width - thickness) * F, lipWidth, 0)
    V5 = FreeCAD.Vector((width - thickness) * F, thickness, 0)
    V6 = FreeCAD.Vector(thickness * F, thickness, 0)
    V7 = FreeCAD.Vector(thickness * F, depth - thickness, 0)
    V8 = FreeCAD.Vector((width - thickness) * F, depth - thickness, 0)
    V9 = FreeCAD.Vector((width - thickness) * F, depth - lipWidth, 0)
    V10 = FreeCAD.Vector(width * F, depth - lipWidth, 0)
    V11 = FreeCAD.Vector(width * F, depth, 0)
    V12 = FreeCAD.Vector(0, depth, 0)

    #Lines
    L1 = Part.makeLine(V1, V2)
    L2 = Part.makeLine(V2, V3)
    L3 = Part.makeLine(V3, V4)
    L4 = Part.makeLine(V4, V5)
    L5 = Part.makeLine(V5, V6)
    L6 = Part.makeLine(V6, V7)
    L7 = Part.makeLine(V7, V8)
    L8 = Part.makeLine(V8, V9)
    L9 = Part.makeLine(V9, V10)
    L10 = Part.makeLine(V10, V11)
    L11 = Part.makeLine(V11, V12)
    L12 = Part.makeLine(V12, V1)

    W = Part.Wire([L1, L2, L3, L4, L5, L6, L7, L8, L9, L10, L11, L12])
    F = Part.Face(W)
    P = F.extrude(FreeCAD.Vector(0, 0, height))
    return P


def Draw_Steel_Track(length, width, flangeHeight, thickness, leftCut=0, rightCut=0, flipped=0):
    # Version=2.0
    # Draw a Steel Track
    # Length=Length
    # Width=Width
    # FlangeHeight=Flange Height
    # Thickness=steel thickness
    # Flipped=[boolean] Draw flangeHeight to +z?

    F = 1
    if flipped == 0:
        F = -1
    # Vertices the track
    V1 = FreeCAD.Vector(0, 0, 0)
    V11 = FreeCAD.Vector(0, thickness, 0)
    V12 = FreeCAD.Vector(0, width - thickness, 0)
    V2 = FreeCAD.Vector(0, width, 0)
    V3 = FreeCAD.Vector(0, width, flangeHeight * F)
    V4 = FreeCAD.Vector(0, width - thickness, flangeHeight * F)
    V5 = FreeCAD.Vector(0, width - thickness, (thickness * F))
    V6 = FreeCAD.Vector(0, thickness, thickness * F)
    V7 = FreeCAD.Vector(0, thickness, flangeHeight * F)
    V8 = FreeCAD.Vector(0, 0, flangeHeight * F)

    #Lines
    L1 = Part.makeLine(V1, V11)  #changed Line to makeLine
    L2 = Part.makeLine(V11, V12)
    L3 = Part.makeLine(V12, V2)
    L4 = Part.makeLine(V2, V3)
    L5 = Part.makeLine(V3, V4)
    L6 = Part.makeLine(V4, V5)
    L7 = Part.makeLine(V5, V6)
    L8 = Part.makeLine(V6, V7)
    L9 = Part.makeLine(V7, V8)
    L10 = Part.makeLine(V8, V1)
    L11 = Part.makeLine(V6, V11)
    L12 = Part.makeLine(V12, V5)

    W1 = Part.Wire([L1, L11, L8, L9, L10])
    W2 = Part.Wire([L2, L12, L7, L11])
    W3 = Part.Wire([L3, L4, L5, L6, L12])
    F1 = Part.Face(W1)
    F2 = Part.Face(W2)
    F3 = Part.Face(W3)
    S1 = F1.extrude(FreeCAD.Vector(length, 0, 0))
    S2 = F2.extrude(FreeCAD.Vector(length - leftCut - rightCut, 0, 0))
    S2.Placement.Base = FreeCAD.Vector(leftCut, 0, 0)
    S3 = F3.extrude(FreeCAD.Vector(length, 0, 0))
    P = S1.fuse(S2)
    P = P.fuse(S3)
    P = P.removeSplitter()

    return P


def Draw_Box_Beam(length, boxWidth, studWidth, height, thickness, lipWidth=8, box=1, FEM=True):
    # Author = Humberto Hassey
    # Version=1.0
    # Draw a Steel stud
    # Length=Length
    # BoxWidth=Width of the whole box
    # StudWidth=width of the individual stud
    # Height=height
    # Thickness=steel thickness'
    
    def Draw_half(length, studWidth, height, thickness, lipWidth=8, flipped=0, FEM=True):
        boxWidth = studWidth
        F = 1
        if flipped == 1:
            F = -1
        # Vertices del stud
        V1 = FreeCAD.Vector(0, 0, 0)
        V2 = FreeCAD.Vector(0, boxWidth * F, 0)
        V3 = FreeCAD.Vector(0, boxWidth * F, lipWidth)
        V4 = FreeCAD.Vector(0, (boxWidth - thickness) * F, lipWidth)
        V5 = FreeCAD.Vector(0, (boxWidth - thickness) * F, thickness)
        V6 = FreeCAD.Vector(0, thickness * F, thickness)
        V7 = FreeCAD.Vector(0, thickness * F, height - thickness)  #length por height
        V8 = FreeCAD.Vector(0, (boxWidth - thickness) * F, height - thickness)
        V9 = FreeCAD.Vector(0, (boxWidth - thickness) * F, height - lipWidth)
        V10 = FreeCAD.Vector(0, boxWidth * F, height - lipWidth)
        V11 = FreeCAD.Vector(0, boxWidth * F, height)
        V12 = FreeCAD.Vector(0, 0, height)

        #Lines
        L1 = Part.makeLine(V1, V2)
        L2 = Part.makeLine(V2, V3)
        L3 = Part.makeLine(V3, V4)
        L4 = Part.makeLine(V4, V5)
        L5 = Part.makeLine(V5, V6)
        L6 = Part.makeLine(V6, V7)
        L7 = Part.makeLine(V7, V8)
        L8 = Part.makeLine(V8, V9)
        L9 = Part.makeLine(V9, V10)
        L10 = Part.makeLine(V10, V11)
        L11 = Part.makeLine(V11, V12)
        L12 = Part.makeLine(V12, V1)

        W = Part.Wire([L1, L2, L3, L4, L5, L6, L7, L8, L9, L10, L11, L12])
        F = Part.Face(W)
        P = F.extrude(FreeCAD.Vector(length, 0, 0))
        return P

    p1 = Draw_half(length, studWidth, height, thickness, lipWidth, 0)
    p2 = Draw_half(length, studWidth, height, thickness, lipWidth, 1)
    if box == 1:
        v1 = FreeCAD.Vector(0, -boxWidth / 2.0 + ((thickness + 1.7272) * FEM),
                            0)  #1.72=ga14 of the clips to mount the piece
        v2 = FreeCAD.Vector(0, boxWidth / 2.0 - ((thickness + 1.7272) * FEM), 0)
        p1.Placement.Base = v1
        p2.Placement.Base = v2
    P = p1.fuse(p2)
    #comp=Part.makeCompound([p1,p2])

    return P  # Comp


def cutBeams(beams):
    # Function that substitutes a list of beams=[(pos x,length)] and returns an
    # enhanced list where the overlaps are counted as only one beam
    # to place only one beam over doors / windows that overlap

    def isin(x1, x2, xt1, xt2):
        if (x1 <= xt1) and (xt1 <= x2):
          # Beams overlap and must be changed for one.
            return True
        else:
            return False

    beams.sort(key=lambda beam: beam[0])
    for indice, beam in enumerate(beams[:-1]):
        x1_initial = beam[0]
        x1_final = x1_initial + beam[1]
        x2_initial = beams[indice + 1][0]
        x2_final = x2_initial + beams[indice + 1][1]
        if isin(x1_initial, x1_final, x2_initial, x2_final):  # Overlapped beams
            beams.pop(indice)
            beams.pop(indice)
            beams.insert(0, (x1_initial, max(x2_final, x1_final) - x1_initial))
            return cutBeams(beams)  # Repeat until there are no overlaping beams
    return beams


class Steel_Frame:
    def __init__(self, obj):
        self.Object = obj  # Line not neccesary this was to try to keep the object after copying
        doc = App.ActiveDocument
        obj.Proxy = self
        obj.addProperty("App::PropertyBool", "FEM", "Frame").FEM = False
        obj.addProperty("App::PropertyStringList", "Windows",
                        "Frame").Windows = ['1200,900,1000,1000']
        obj.addProperty("App::PropertyLength", "Length", "Frame").Length = 3500
        obj.addProperty("App::PropertyLength", "Height", "Frame").Height = 3000
        obj.addProperty("App::PropertyLength", "Width", "Frame").Width = 152.4
        obj.addProperty("App::PropertyLength", "Separation",
                        "Frame").Separation = 304.8
        obj.addProperty("App::PropertyLength", "Flange",
                        "Stud").Flange = 41.275
        obj.addProperty("App::PropertyLength", "Lip", "Stud").Lip = 8
        obj.addProperty("App::PropertyLength", "Thickness",
                        "Steel").Thickness = 0.8382
        obj.addProperty("App::PropertyQuantity", "Gauge", "Steel").Gauge = 22
        obj.addProperty("App::PropertyQuantity", "Weight",
                        "Take Off").Weight = 0
        obj.addProperty("App::PropertyLength", "Stud_L", "Take Off").Stud_L = 0
        obj.addProperty("App::PropertyLength", "Track_L",
                        "Take Off").Track_L = 0
        obj.addProperty("App::PropertyBool", "Structural",
                        "Structural").Structural = False
        obj.addProperty("App::PropertyLength", "Beam_Height",
                        "Structural").Beam_Height = 150
        obj.addProperty("App::PropertyLength", "Stud_Width",
                        "Structural").Stud_Width = 41.275
        obj.addProperty("App::PropertyBool", "Box", "Structural").Box = True

    #def onChanged(self, fp, prop):
    #FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")

    #def onChanged(self, obj, prop):
    #   App.activeDocument().recompute()

    def onDocumentRestored(self, obj):
        # Restore object references on reload
        print('Document Restored')
        self.Object = obj

    def execute(self, obj):
        openings = []
        beams = [] # Structural beams
        if obj.Windows[0] != '': # If There are windows in this frame
            for index in range(len(obj.Windows)):
                openings.append(eval(
                    obj.Windows[index])) # Create list of windows
                beams.append((eval(obj.Windows[index])[0],
                              eval(obj.Windows[index])[2]))
        # Get all doors to be able to cut the track below.
        doors = [door for door in openings if door[1] == 0]
        doors.sort(key=lambda door: door[0]) # Sort doors by x coordinate
        currentTracX = 0 # Varaiable to keep track of position of tracks along the length
        currentStudZ = 0 # Varaiable to keep track of position of studs along the height
        #post_W=0
        FEM = not (obj.FEM) # FEM = Make studs and tracks the same width.

        gauges = {
            25: 0.4572,
            22: 0.6858,
            20: 0.8382,
            18: 1.0922,
            16: 1.3716,
            14: 1.7272,
            12: 2.4638,
            10: 2.9972
        }
        if obj.Gauge.Value in gauges and obj.Gauge.Value != 0:
            obj.Thickness.Value = gauges[obj.Gauge.Value]
        else:
            obj.Gauge.Value = 0
        if obj.Thickness.Value not in gauges.values() and obj.Gauge.Value != 0:
            obj.Gauge.Value = 0

        flangeLength = obj.Flange.Value
        frameWidth = obj.Width.Value
        frameHeight = obj.Height.Value
        frameLength = obj.Length.Value
        thickness = obj.Thickness.Value
        lipWidth = obj.Lip.Value

        Flip = 0

        studs = calcStuds(
            frameLength,
            frameHeight,
            obj.Separation.Value,
            flangeLength,
            openings,
            FEM,
            0,
            obj.Structural,
            obj.Beam_Height.Value,
            thickness=thickness) # 0 decia thickness

        parts = [] # List of parts that will make the frame
        # Draw Studs
        for indice, stud in enumerate(studs):
            # -1 so it will not draw the last stud since that one goes flipped
            parts.append(
                Draw_Steel_Stud(frameWidth - 2 * thickness * FEM, flangeLength, thickness,
                                stud[2] - 2 * thickness * FEM, lipWidth,
                                stud[3])) # Draw stud
            parts[indice].Placement.Base = FreeCAD.Vector(
                stud[0], thickness * FEM,
                stud[1] + thickness * FEM) # Place stud #correct Z for FEM
            currentStudZ += stud[2] - 2 * thickness * FEM

		# Draw Tracks

		## Lower Track
        if len(doors) == 0: # If no doors, the track goes uninterrupted
            trackLength = frameLength
            lowerTrack = Draw_Steel_Track(
                trackLength, frameWidth, flangeLength, thickness, flipped=1)
            lowerTrack.Placement.Base = FreeCAD.Vector(0, 0, 0)
            currentTracX += trackLength
            parts.append(lowerTrack)
        else:
            # Draw track from 0 to the first door
            trackLength = doors[0][0]
            lowerTrack = Draw_Steel_Track(
                trackLength, frameWidth, flangeLength, thickness, flipped=1)
            lowerTrack.Placement.Base = FreeCAD.Vector(0, 0, 0)
            currentTracX += trackLength
            parts.append(lowerTrack)
            # Draw track from door n to door n+1
            doors_Completed = 1
            while len(doors) > doors_Completed:
                trackLength = doors[doors_Completed][0] - doors[doors_Completed - 1][0] \
                  - doors[doors_Completed - 1][2]
                lowerTrack = Draw_Steel_Track(
                    trackLength, frameWidth, flangeLength, thickness, flipped=1)
                # Calculate the position of the segment
                pos = doors[doors_Completed - 1][0] \
                    + doors[doors_Completed - 1][2]
                lowerTrack.Placement.Base = FreeCAD.Vector(pos, 0, 0)
                currentTracX += trackLength
                parts.append(lowerTrack)
                doors_Completed += 1
            # Draw segment from last door to end
            trackLength = frameLength - (doors[-1][0] + doors[-1][2])
            lowerTrack = Draw_Steel_Track(
                trackLength, frameWidth, flangeLength, thickness, flipped=1)
            lowerTrack.Placement.Base = FreeCAD.Vector(doors[-1][0] \
            	+ doors[-1][2], 0, 0)
            currentTracX += trackLength
            parts.append(lowerTrack)
        # Draw upper track
        trackLength = frameLength
        upperTrack = Draw_Steel_Track(
            trackLength, frameWidth, flangeLength, thickness, flipped=0)  # Top Track
        upperTrack.Placement.Base = FreeCAD.Vector(0, 0, frameHeight)
        currentTracX += trackLength
        parts.append(upperTrack)
        for opening in openings: # Draw tracks for doors and windows
            upperOpeningTrack = Draw_Steel_Track(opening[2] + 2 * flangeLength, frameWidth, flangeLength,
            	                 thickness, flangeLength, flangeLength, 1)  # Top piece flangeLength=flange
            upperOpeningTrack.Placement.Base = FreeCAD.Vector(opening[0] - flangeLength, 0,
                                              opening[1] + opening[3])
            currentTracX += opening[2] + 2 * flangeLength
            parts.append(upperOpeningTrack)
            if opening[1] != 0:  # If it is a door, don't draw the lower track
                lowerOpeningTrack = Draw_Steel_Track(opening[2] + 2 * flangeLength, frameWidth, flangeLength, thickness,
                	                  flangeLength, flangeLength, 0)  # Bottom piece flangeLength=flange
                lowerOpeningTrack.Placement.Base = FreeCAD.Vector(opening[0] - flangeLength, 0, opening[1])
                currentTracX += opening[2] + 2 * flangeLength
                parts.append(lowerOpeningTrack)
        # Draw Structural Box Beams
        if obj.Structural == True:
            beams = cutBeams(beams)
            for beam in beams:
                beamLength = beam[1]  # Length of the beam
                studWidth = obj.Stud_Width.Value
                boxWidth = obj.Width.Value
                beamHeight = obj.Beam_Height.Value
                structuralBeam = Draw_Box_Beam(beamLength, boxWidth, studWidth, beamHeight, thickness, lipWidth,
                                    obj.Box, FEM)
                structuralBeam.Placement.Base = FreeCAD.Vector(
                    beam[0], frameWidth / 2, frameHeight - beamHeight -
                    (thickness * FEM))
                parts.append(structuralBeam)
                # Draw Track Below beam...
                belowBeamTrack = Draw_Steel_Track(
                    beamLength,
                    frameWidth,
                    flangeLength,
                    thickness,
                    leftCut=0,
                    rightCut=0,
                    flipped=0)
                belowBeamTrack.Placement.Base = FreeCAD.Vector(
                    beam[0], 0, frameHeight - beamHeight -
                    (thickness * FEM))
                currentTracX += beamLength
                parts.append(belowBeamTrack)
                # Here we are missing to add the lengths of the sections!!!

                # Draw special clips to mount the beam
                if obj.Box:
                    e1 = Draw_Steel_Track(
                        beamHeight,
                        boxWidth - (2 * thickness * FEM),
                        flangeLength,
                        1.7272,
                        leftCut=0,
                        rightCut=0,
                        flipped=0)  # Ga14
                    e1.Placement.Rotation = App.Rotation(
                        App.Vector(0, 1, 0), -90)
                    e1.Placement.Base = FreeCAD.Vector(
                        beam[0], thickness * FEM,
                        frameHeight - beamHeight -
                        (thickness * FEM))
                    e2 = Draw_Steel_Track(
                        beamHeight,
                        boxWidth - (2 * thickness * FEM),
                        flangeLength,
                        1.7272,
                        leftCut=0,
                        rightCut=0,
                        flipped=1)
                    e2.Placement.Rotation = App.Rotation(
                        App.Vector(0, 1, 0), -90)
                    e2.Placement.Base = FreeCAD.Vector(
                        beam[0] + beam[1], thickness * FEM,
                        frameHeight - beamHeight -
                        (thickness * FEM))
                    parts.append(e1)
                    parts.append(e2)
        comp = Part.makeCompound(parts)
        if obj.FEM:  # Make one solid for FEM analysis
            comp = Part.makeSolid(comp)
            comp2 = comp.removeSplitter()
            obj.Shape = comp2
            print('Center of Mass', obj.Shape.CenterOfMass)
        obj.Shape = comp
        obj.Weight = comp.Volume * 7850 / 1e9
        obj.Stud_L = FreeCAD.Units.Metre * currentStudZ / 1e3
        obj.Track_L = FreeCAD.Units.Metre * currentTracX / 1e3

        # Calculate Center of mass
        if not (obj.FEM):
            v = FreeCAD.Vector(0, 0, 0)
            solids = obj.Shape.Solids
            for solid in solids:
                v2 = solid.CenterOfMass * solid.Volume
                v = v.add(v2)
            vt = obj.Shape.Volume
            print('Center of Mass', v * (1 / vt))


#a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Steel_Frame")
#Steel_Frame(a)
#a.ViewObject.Proxy    =    0

#App.ActiveDocument.recompute()
