#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 12:39:21 2018

@author: orion
"""



def calculateWaste(pieceLength,pieceWidth,coverDistance):
    ''' Funtion to calculate the waste in terms of area given the
    length of a piece in the direction analyzed, the perpendicular width 
    and the distance to cover, it Returns the waste in square units'''
    
    if pieceLength > coverDistance:
        return (pieceLength-coverDistance)*pieceWidth
    elif pieceLength == coverDistance:
        return 0
    else:
        if coverDistance%pieceLength==0:
            return 0
        else:
            return (pieceLength-(coverDistance%pieceLength))*pieceWidth
    
def reducePieceList(pieces,restriction):
    '''Function that reduces the list of pieces available when certain pieces can only be 
    used with the width = restriction'''
    result=[]
    for candidate in pieces:
        if candidate[0]==restriction:
            result.append(candidate)
    return result

def choosePiece(pieces,horizontalDistance,verticalDistance): 
    ''' Function to find the minimum waste given the horizontal and vertical distance to cover and several pieces.
    it returns a tuple with the piece with minimum waste and the waste (Area)'''
        
    # revise in bothe directions
    verticalWaste= [calculateWaste(x[1],x[0],verticalDistance) for x in pieces]
    horizontalWaste= [calculateWaste(x[0],x[1],horizontalDistance) for x in pieces]
    summedWaste=[sum(x) for x in zip(verticalWaste,horizontalWaste)]
    # aggregate waste
    minIndex = summedWaste.index(min(summedWaste)) 
    return (minIndex,summedWaste[minIndex])
    
    
def panelize(subFrame,pieces,reuse=1,minimumWideSide=300,minimumTallSide=500):
    
    ''' Function that takes a subframe and returns a list of pieces to panelze it
    it returns a list of tuples (coordinates,piecex or y, piece z) to fill the subframe.
    '''
    waste=0
    minimumSize=300 #tama minimo para aceptar pieces sobrantes.
    
    pieceList=[] # tuplas de pieces a colocar ((x,y,z),largo,width,waste)
    reuseList=[] # aqui guardaremos las pieces de reuso.
    width = subFrame[1][0]
    height = subFrame[1][1]
    
    horizontalCoverDistance=width
    verticalCoverDistance=height
    while horizontalCoverDistance > 0:
        firstPiece=1
        verticalCoverDistance=height
        while verticalCoverDistance > 0:
            ##############################################
             #codigo que solo se ejecuta si es la primera pieza de la columna
            if len(reuseList)==0:
                if firstPiece==1: #podemos escoger la siguiente pieza arriba con cualquier width
                    chosenPiece=pieces[choosePiece(pieces,horizontalCoverDistance,verticalCoverDistance)[0]]
                    firstPiece=0 #elegimos pieza
                    
                else: #ya hay una pieza abajo y solo podemos escoger pieces con el mismo width.
                    firstPieceWidth=pieceList[-1][1][0]
                    beforeChoicePiece=pieces[choosePiece(pieces,horizontalCoverDistance,verticalCoverDistance)[0]]
                    if beforeChoicePiece[0]>=horizontalCoverDistance and firstPieceWidth >= horizontalCoverDistance: #revisamos si la pieza pre elegida puede llenar el espacio missingDistancente
                        chosenPiece=beforeChoicePiece #si si, tomamos esta pieza como buena
                    else: #la pieza pre elegida no llena el espacio y hay que limitar a pieces con el width de la que sobro
                        pieceWidth=chosenPiece[0]
                        possiblePieces=reducePieceList(pieces,pieceWidth)
                        chosenPiece=possiblePieces[choosePiece(possiblePieces,pieceWidth,verticalCoverDistance)[0]]
                    
            else: #tomar la pieza que sobro
                chosenPiece=reuseList.pop()
                firstPiece=0
                
                
             ###################################       
            if chosenPiece[0]< horizontalCoverDistance: #la pieza <= que la dist horizontal
                if chosenPiece[1]<verticalCoverDistance: 
                    #####################################################
                    #1 Pieza < dist horizontal y pieza < dist vertical 
                    #####################################################
                # No hay que cortar la pieza, calculamos coordenadas y la colocamos y ajusto distancias
                    pieceCoordinateX =subFrame[0][0]+width-horizontalCoverDistance
                    pieceCoordinateY =subFrame[0][1]                        
                    pieceCoordinateZ = subFrame[0][2]+height-verticalCoverDistance
                    #revisar que la pieza ultima en el margen derecho no sea menor que el minimo
                    if horizontalCoverDistance-chosenPiece[0]<minimumWideSide:
                        remainingDistance=horizontalCoverDistance-chosenPiece[0]
                        missingDistance=minimumWideSide-remainingDistance
                        waste+=chosenPiece[1]*missingDistance #agregamos waste por redefinicion
                        spechialPiece=(chosenPiece[0]-missingDistance,chosenPiece[1])
                        
                        if verticalCoverDistance-chosenPiece[1]<minimumTallSide: #hay ajuste en width y en height
                           remainingDistance=verticalCoverDistance-chosenPiece[1]
                           missingDistance=minimumTallSide-remainingDistance
                           waste+=spechialPiece[0]*missingDistance #agregamos waste por redefinicion
                           piezaReEspecial=(spechialPiece[0],chosenPiece[1]-missingDistance)
                           pieceList.append(((pieceCoordinateX,pieceCoordinateY,pieceCoordinateZ),piezaReEspecial))
                           verticalCoverDistance -= piezaReEspecial[1]
                        else: #solo se redefinio pieza en lo width.
                           pieceList.append(((pieceCoordinateX,pieceCoordinateY,pieceCoordinateZ),spechialPiece))
                           verticalCoverDistance -= spechialPiece[1] 
                    else: # no hay necesidad de redefinir la pieza en lo width
                        if verticalCoverDistance-chosenPiece[1]<minimumTallSide: #pero si hay ajuste en height
                           remainingDistance=verticalCoverDistance-chosenPiece[1]
                           missingDistance=minimumTallSide-remainingDistance
                           waste+=chosenPiece[0]*missingDistance #agregamos waste por redefinicion
                           spechialPiece=(chosenPiece[0],chosenPiece[1]-missingDistance)
                           pieceList.append(((pieceCoordinateX,pieceCoordinateY,pieceCoordinateZ),spechialPiece))
                           verticalCoverDistance -= spechialPiece[1]
                        else: #no hay necesidad de redefinir pieza ni en width ni height
                           pieceList.append(((pieceCoordinateX,pieceCoordinateY,pieceCoordinateZ),chosenPiece))
                           verticalCoverDistance -= chosenPiece[1]
                    
                    
                elif chosenPiece[1]==verticalCoverDistance:
                    #######################################################
                    #2Pieza < dist horizontal y pieza = dist vertical 
                    ######################################################
                    pieceCoordinateX =subFrame[0][0]+width-horizontalCoverDistance
                    pieceCoordinateY =subFrame[0][1]
                    pieceCoordinateZ = subFrame[0][2]+height-verticalCoverDistance
                    #revisar que la pieza ultima en el margen derecho no sea menor que el minimo
                    if horizontalCoverDistance-chosenPiece[0]<minimumWideSide:
                        remainingDistance=horizontalCoverDistance-chosenPiece[0]
                        missingDistance=minimumWideSide-remainingDistance
                        waste+=chosenPiece[1]*missingDistance #agregamos waste por redefinicion
                        spechialPiece=(chosenPiece[0]-missingDistance,chosenPiece[1])
                        pieceList.append(((pieceCoordinateX,pieceCoordinateY,pieceCoordinateZ),spechialPiece))
                        verticalCoverDistance = 0
                        horizontalCoverDistance -= spechialPiece[0]
                    else: # no hay necesidad de redefinir la pieza 
                        pieceList.append(((pieceCoordinateX,pieceCoordinateY,pieceCoordinateZ),chosenPiece))
                        verticalCoverDistance = 0
                        horizontalCoverDistance -= chosenPiece[0] #actualizamos la distancia a cubrir
                        firstPiece=1
                                    
                else: 
                    #######################################################
                    #3pieza < dist horizontal y pieza > dist Vertical
                    #######################################################
                # hay que cortar la pieza horizontalmente, calcular coords e iniciar nueva columna.
                    cutPiece=(chosenPiece[0],verticalCoverDistance)
                    
                    pieceCoordinateX =subFrame[0][0]+width-horizontalCoverDistance
                    pieceCoordinateY =subFrame[0][1]
                    pieceCoordinateZ = subFrame[0][2]+height-verticalCoverDistance
                    #revisar que la proxima pieza ultima en el margen derecho no sea menor que el minimo
                    if horizontalCoverDistance-chosenPiece[0]<minimumWideSide:
                        remainingDistance=horizontalCoverDistance-chosenPiece[0]
                        missingDistance=minimumWideSide-remainingDistance
                        waste+=cutPiece[1]*missingDistance #agregamos waste por redefinicion
                        spechialPiece=(cutPiece[0]-missingDistance,cutPiece[1])
                        pieceList.append(((pieceCoordinateX,pieceCoordinateY,pieceCoordinateZ),spechialPiece))
                        verticalCoverDistanceBefore=verticalCoverDistance
                        verticalCoverDistance = 0
                        horizontalCoverDistance -= spechialPiece[0]
                    else: # no hay necesidad de redefinir la pieza 
                        pieceList.append(((pieceCoordinateX,pieceCoordinateY,pieceCoordinateZ),cutPiece))
                        verticalCoverDistanceBefore=verticalCoverDistance
                        verticalCoverDistance = 0
                        horizontalCoverDistance -= cutPiece[0] #actualizamos la distancia a cubrir
                        firstPiece=1
                    
                    if reuse==1: # si se reutiliza la pieza que sobraría
                        surplusPiece=(cutPiece[0],chosenPiece[1]-cutPiece[1])
                        if surplusPiece[1]>=minimumSize:
                            reuseList.append(surplusPiece)
                        else: #la pieza no se utilizó por ser chica y por lo tanto se desperdicia
                            waste += (chosenPiece[1]-verticalCoverDistanceBefore)*cutPiece[0]
                                            
                    else:
                        #solo hay waste si la pieza que sobra no se reutiliza
                        waste += (chosenPiece[1]-verticalCoverDistanceBefore)*chosenPiece[0]
                        
                        
                    verticalCoverDistance =0 #esto tal vez sobra
                    
                
            #agregar la pieza a la lista de pieces
            elif chosenPiece[0]== horizontalCoverDistance: #la pieza > la distancia horizontal
                if chosenPiece[1]< verticalCoverDistance: 
                    #####################################################
                    #4Pieza = dist horizontal y pieza < dist vertical
                    #####################################################
                    # No hay que cortar, calcular coords y ajustar dist vertical
                    
                    pieceCoordinateX =subFrame[0][0]+width-horizontalCoverDistance
                    pieceCoordinateY =subFrame[0][1]
                    pieceCoordinateZ = subFrame[0][2]+height-verticalCoverDistance
                    
                    #revisamos si hay que ajustar la pieza verticalmente para no generar una pieza < minima 
                    if verticalCoverDistance-chosenPiece[1]<minimumTallSide: #pero si hay ajuste en height
                           remainingDistance=verticalCoverDistance-chosenPiece[1]
                           missingDistance=minimumTallSide-remainingDistance
                           waste+=chosenPiece[0]*missingDistance #agregamos waste por redefinicion
                           spechialPiece=(chosenPiece[0],chosenPiece[1]-missingDistance)
                           pieceList.append(((pieceCoordinateX,pieceCoordinateY,pieceCoordinateZ),spechialPiece))
                           verticalCoverDistance -= spechialPiece[1]
                    else: #no hay necesidad de redefinir pieza ni en height
                           pieceList.append(((pieceCoordinateX,pieceCoordinateY,pieceCoordinateZ),chosenPiece))
                           verticalCoverDistance -= chosenPiece[1]
                                                       
                elif chosenPiece[1]== verticalCoverDistance: 
                    #######################################################
                    #5pieza = dist horizontal y pieza = dist Vertical
                    #######################################################
                    # meter pieza a la lista, calcular coords salir del programa.
                    pieceCoordinateX =subFrame[0][0]+width-horizontalCoverDistance
                    pieceCoordinateY =subFrame[0][1]
                    pieceCoordinateZ = subFrame[0][2]+height-verticalCoverDistance
                    
                    pieceList.append(((pieceCoordinateX,pieceCoordinateY,pieceCoordinateZ),chosenPiece))
                    
                    return pieceList,waste,waste/(width*height)
                else:
                    #######################################################
                    #6pieza = dist horizontal y pieza > dist Vertical
                    #######################################################
                    # hay que cortar la pieza horizontalmente, calcular coords e iniciar nueva columna.
                    cutPiece=(horizontalCoverDistance,verticalCoverDistance)
                    
                    pieceCoordinateX =subFrame[0][0]+width-cutPiece[0]
                    pieceCoordinateY =subFrame[0][1]
                        #horizontalCoverDistance -= piezaMinimo[0] #actualizamos la distancia a cubrir
                    pieceCoordinateZ = subFrame[0][2]+height-cutPiece[1]
                    pieceList.append(((pieceCoordinateX,pieceCoordinateY,pieceCoordinateZ),cutPiece))
                    horizontalCoverDistance -= cutPiece[0] #actualizamos la distancia a cubrir
                    
                    firstPiece=1
                    waste += (chosenPiece[1]-verticalCoverDistance)*chosenPiece[0]
                    verticalCoverDistance =0
                    return pieceList,waste,waste/(width*height)          
            elif chosenPiece[0]> horizontalCoverDistance:
                
                if chosenPiece[1]< verticalCoverDistance: 
                    #####################################################
                    #7Pieza > dist horizontal y pieza < dist vertical
                    #####################################################
                    # hay que cortar la pieza verticalmente, calculamos coordenadas y la colocamos y ajustamos coords
                    cutPiece=(horizontalCoverDistance,chosenPiece[1])
                    waste += (chosenPiece[0]-horizontalCoverDistance)*chosenPiece[1]
                    
                    pieceCoordinateX =subFrame[0][0]+width-horizontalCoverDistance
                    pieceCoordinateY =subFrame[0][1]
                        
                    pieceCoordinateZ = subFrame[0][2]+height-verticalCoverDistance
                    #revisamos si hay que ajustar la pieza verticalmente para no generar una pieza < minima 
                    if verticalCoverDistance-chosenPiece[1]<minimumTallSide: #pero si hay ajuste en height
                           remainingDistance=verticalCoverDistance-chosenPiece[1]
                           missingDistance=minimumTallSide-remainingDistance
                           waste+=cutPiece[0]*missingDistance #agregamos waste por redefinicion
                           spechialPiece=(cutPiece[0],cutPiece[1]-missingDistance)
                           pieceList.append(((pieceCoordinateX,pieceCoordinateY,pieceCoordinateZ),spechialPiece))
                           verticalCoverDistance -= spechialPiece[1]
                    else: #no hay necesidad de redefinir pieza ni en height
                           pieceList.append(((pieceCoordinateX,pieceCoordinateY,pieceCoordinateZ),cutPiece))
                           verticalCoverDistance -= cutPiece[1]
                    
                                                                    
                elif chosenPiece[1]== verticalCoverDistance: 
                    #######################################################
                    #8pieza > dist horizontal y pieza = dist Vertical
                    #######################################################
                    # hay que cortar la pieza verticalmente, calcular coords y salir
                    cutPiece=(horizontalCoverDistance,verticalCoverDistance)
                    waste += (chosenPiece[0]-horizontalCoverDistance)*chosenPiece[1]
                    
                    pieceCoordinateX =subFrame[0][0]+width-cutPiece[0]
                    pieceCoordinateY =subFrame[0][1]
                        #horizontalCoverDistance -= piezaMinimo[0] #actualizamos la distancia a cubrir
                    pieceCoordinateZ = subFrame[0][2]+height-cutPiece[1]# estaba esto subFrame[0][2]
                    pieceList.append(((pieceCoordinateX,pieceCoordinateY,pieceCoordinateZ),cutPiece))
                    horizontalCoverDistance =0 #actualizamos la distancia a cubrir
                    verticalCoverDistance =0
                    return pieceList,waste,waste/(width*height)
                else:
                    #######################################################
                    #9pieza > dist horizontal y pieza > dist Vertical
                    #######################################################
                    # hay que cortar la pieza horizontalmente, calcular coords y salir
                    cutPiece=(horizontalCoverDistance,verticalCoverDistance)
                    desp=(chosenPiece[0]*chosenPiece[1])-(horizontalCoverDistance*verticalCoverDistance)
                    waste += desp
                    
                    pieceCoordinateX =subFrame[0][0]+width-cutPiece[0]
                    pieceCoordinateY =subFrame[0][1]
                        #horizontalCoverDistance -= piezaMinimo[0] #actualizamos la distancia a cubrir
                    pieceCoordinateZ = subFrame[0][2]+height-cutPiece[1]# estaba esto subFrame[0][2]
                    pieceList.append(((pieceCoordinateX,pieceCoordinateY,pieceCoordinateZ),cutPiece))
                    return pieceList,waste,waste/(width*height)
 
    print('error Case not contemplated')
    return pieceList,waste,waste/(width*height)
#Vector (2900.0, 0.0, 2000.0) 1000.0 1300.0
#subFrame=[(0,0,0),(2743,2438)] #punto inicio,largo,height,direccion
#pieces=[(1219,2743),(2743,1219),(1219,2438),(2438,1219)] #tamano de los paneles que juega
#pieces=[(1000,1000)]
#s,d,p=paneliza(subFrame,pieces,1)
#print ('Desperdicio ',round(p*100,3),'%')
#print ('Desperdicio ',round(d/1e6,2),'m2')
