#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 12:39:21 2018

@author: orion
"""


def calculateWaste(pieceLength, pieceWidth, coverDistance):
    # Function to calculate the waste in terms of area given the
    # length of a piece in the direction analyzed, the perpendicular width
    # and the distance to cover, it Returns the waste in square units

    if pieceLength > coverDistance:
        return (pieceLength - coverDistance) * pieceWidth
    elif pieceLength == coverDistance:
        return 0
    else:
        if coverDistance % pieceLength == 0:
            return 0
        else:
            return (pieceLength - (coverDistance % pieceLength)) * pieceWidth


def reducePieceList(pieces, restriction):
    # Function that reduces the list of pieces available when certain pieces
    # can only be used with the width = restriction

    result = []
    for candidate in pieces:
        if candidate[0] == restriction:
            result.append(candidate)
    return result


def choosePiece(pieces, horizontalDistance, verticalDistance):
    # Function to find the minimum waste given the horizontal and vertical
    # distance to cover and several pieces.
    # it returns a tuple with the piece with minimum waste and the waste (Area)

    # Revise in both directions
    verticalWaste = [
        calculateWaste(x[1], x[0], verticalDistance) for x in pieces
    ]
    horizontalWaste = [
        calculateWaste(x[0], x[1], horizontalDistance) for x in pieces
    ]
    summedWaste = [sum(x) for x in zip(verticalWaste, horizontalWaste)]
    # Aggregate waste
    minIndex = summedWaste.index(min(summedWaste))
    return (minIndex, summedWaste[minIndex])


def panelize(subFrame,
             pieces,
             reuse=1,
             minimumWideSide=300,
             minimumTallSide=500):
    # Function that takes a subframe and returns a list of pieces to panelize it
    # it returns a list of tuples (coordinates, piecex or y, piece z) to fill
    # the subframe.

    waste = 0
    minimumSize = 300  # Minimum to accept surplus pieces

    pieceList = []  # Tuples of pieces to search ((x,y,z),largo,width,waste)
    reuseList = []  # Here we store pieces for reuse 
    width = subFrame[1][0]
    height = subFrame[1][1]

    horizontalCoverDistance = width
    verticalCoverDistance = height
    while horizontalCoverDistance > 0:
        firstPiece = 1
        verticalCoverDistance = height
        while verticalCoverDistance > 0:
            # Code that only runs if it is the first piece of the column
            if len(reuseList) == 0:
                # The first piece on the bottom can be of any width
                if firstPiece == 1:
                    chosenPiece = pieces[choosePiece(pieces,
                                                     horizontalCoverDistance,
                                                     verticalCoverDistance)[0]]
                    firstPiece = 0  # We have chosen the first piece
                # There is already a piece below and we can only
                # choose pieces with the same width
                else:
                    firstPieceWidth = pieceList[-1][1][0]
                    beforeChoicePiece = pieces[choosePiece(
                        pieces, horizontalCoverDistance,
                        verticalCoverDistance)[0]]
                    # We check if the pre-chosen piece can fill the
                    # missing space
                    if (beforeChoicePiece[0] >= horizontalCoverDistance and
                            firstPieceWidth >= horizontalCoverDistance):
                        # We accept this as a good piece
                        chosenPiece = beforeChoicePiece
                    # The pre-chosen piece does not fill the space and
                    # you have to limit pieces to the width
                    # of the remaining space
                    else:
                        pieceWidth = chosenPiece[0]
                        possiblePieces = reducePieceList(pieces, pieceWidth)
                        chosenPiece = possiblePieces[choosePiece(
                            possiblePieces, pieceWidth,
                            verticalCoverDistance)[0]]

            else:  # Choose a surplus piece
                chosenPiece = reuseList.pop()
                firstPiece = 0
            # piece <= than the horizontal distance
            if chosenPiece[0] < horizontalCoverDistance:
                if chosenPiece[1] < verticalCoverDistance:
                    # 1. piece < horizontal dist and piece < vertical dist
                    # You don't have to cut the piece. Calculate coordinates,
                    # place it and adjust distances
                    pieceCoordinateX = subFrame[0][0] + \
                        width - horizontalCoverDistance
                    pieceCoordinateY = subFrame[0][1]
                    pieceCoordinateZ = subFrame[0][2] + \
                        height - verticalCoverDistance
                    # Revisar que la pieza ultima en el margen derecho no sea
                    # menor que el minimo
                    if horizontalCoverDistance - \
                            chosenPiece[0] < minimumWideSide:
                        remainingDistance = horizontalCoverDistance - \
                            chosenPiece[0]
                        missingDistance = minimumWideSide - remainingDistance
                        # Agregamos waste por redefinicion
                        waste += chosenPiece[1] * missingDistance
                        spechialPiece = (chosenPiece[0] - missingDistance,
                                         chosenPiece[1])
                        # Hay ajuste en width y en height
                        if verticalCoverDistance - \
                                chosenPiece[1] < minimumTallSide:
                            remainingDistance = verticalCoverDistance - \
                                chosenPiece[1]
                            missingDistance = minimumTallSide - \
                                remainingDistance
                            # Agregamos waste por redefinicion
                            waste += spechialPiece[0] * missingDistance
                            piezaReEspecial = (
                                spechialPiece[0],
                                chosenPiece[1] - missingDistance)
                            pieceList.append(
                                ((pieceCoordinateX, pieceCoordinateY,
                                  pieceCoordinateZ), piezaReEspecial))
                            verticalCoverDistance -= piezaReEspecial[1]
                        else:  # Solo se redefinio pieza en lo width.
                            pieceList.append(
                                ((pieceCoordinateX, pieceCoordinateY,
                                  pieceCoordinateZ), spechialPiece))
                            verticalCoverDistance -= spechialPiece[1]
                    # No hay necesidad de redefinir la pieza en lo width
                    else:
                        if verticalCoverDistance - \
                                chosenPiece[1] < minimumTallSide:
                            # pero si hay ajuste en height
                            remainingDistance = verticalCoverDistance - \
                                chosenPiece[1]
                            missingDistance = minimumTallSide - \
                                remainingDistance
                            # agregamos waste por redefinicion
                            waste += chosenPiece[0] * missingDistance
                            spechialPiece = (chosenPiece[0],
                                             chosenPiece[1] - missingDistance)
                            pieceList.append(
                                ((pieceCoordinateX, pieceCoordinateY,
                                  pieceCoordinateZ), spechialPiece))
                            verticalCoverDistance -= spechialPiece[1]
                        # No hay necesidad de redefinir pieza
                        # ni en width ni height
                        else:
                            pieceList.append(
                                ((pieceCoordinateX, pieceCoordinateY,
                                  pieceCoordinateZ), chosenPiece))
                            verticalCoverDistance -= chosenPiece[1]

                elif chosenPiece[1] == verticalCoverDistance:
                    # 2 Pieza < dist horizontal y pieza = dist vertical
                    pieceCoordinateX = subFrame[0][0] + \
                        width - horizontalCoverDistance
                    pieceCoordinateY = subFrame[0][1]
                    pieceCoordinateZ = subFrame[0][2] + \
                        height - verticalCoverDistance
                    # Revisar que la pieza ultima en el margen derecho no sea
                    # menor que el minimo
                    if horizontalCoverDistance - \
                            chosenPiece[0] < minimumWideSide:
                        remainingDistance = horizontalCoverDistance - \
                            chosenPiece[0]
                        missingDistance = minimumWideSide - remainingDistance
                        # Agregamos waste por redefinicion
                        waste += chosenPiece[1] * missingDistance
                        spechialPiece = (chosenPiece[0] - missingDistance,
                                         chosenPiece[1])
                        pieceList.append(((pieceCoordinateX, pieceCoordinateY,
                                           pieceCoordinateZ), spechialPiece))
                        verticalCoverDistance = 0
                        horizontalCoverDistance -= spechialPiece[0]
                    else:  # No hay necesidad de redefinir la pieza
                        pieceList.append(((pieceCoordinateX, pieceCoordinateY,
                                           pieceCoordinateZ), chosenPiece))
                        verticalCoverDistance = 0
                        horizontalCoverDistance -= chosenPiece[
                            0]  # Actualizamos la distancia a cubrir
                        firstPiece = 1

                else:
                    # 3 pieza < dist horizontal y pieza > dist Vertical
                    # Hay que cortar la pieza horizontalmente, calcular coords
                    # e iniciar nueva columna.
                    cutPiece = (chosenPiece[0], verticalCoverDistance)

                    pieceCoordinateX = subFrame[0][0] + \
                        width - horizontalCoverDistance
                    pieceCoordinateY = subFrame[0][1]
                    pieceCoordinateZ = subFrame[0][2] + \
                        height - verticalCoverDistance
                    # Revisar que la proxima pieza ultima en el margen derecho
                    # no sea menor que el minimo
                    if horizontalCoverDistance - \
                            chosenPiece[0] < minimumWideSide:
                        remainingDistance = horizontalCoverDistance - \
                            chosenPiece[0]
                        missingDistance = minimumWideSide - remainingDistance
                        # Agregamos waste por redefinicion
                        waste += cutPiece[1] * missingDistance
                        spechialPiece = (cutPiece[0] - missingDistance,
                                         cutPiece[1])
                        pieceList.append(((pieceCoordinateX, pieceCoordinateY,
                                           pieceCoordinateZ), spechialPiece))
                        verticalCoverDistanceBefore = verticalCoverDistance
                        verticalCoverDistance = 0
                        horizontalCoverDistance -= spechialPiece[0]
                    else:  # No hay necesidad de redefinir la pieza
                        pieceList.append(((pieceCoordinateX, pieceCoordinateY,
                                           pieceCoordinateZ), cutPiece))
                        verticalCoverDistanceBefore = verticalCoverDistance
                        verticalCoverDistance = 0
                        horizontalCoverDistance -= cutPiece[
                            0]  # Actualizamos la distancia a cubrir
                        firstPiece = 1

                    if reuse == 1:  # Si se reutiliza la pieza que sobraría
                        surplusPiece = (cutPiece[0],
                                        chosenPiece[1] - cutPiece[1])
                        if surplusPiece[1] >= minimumSize:
                            reuseList.append(surplusPiece)
                        # La pieza no se utilizó por ser chica #
                        # y por lo tanto se desperdicia
                        else:
                            waste += (
                                chosenPiece[1] - verticalCoverDistanceBefore
                            ) * cutPiece[0]

                    else:
                        # Solo hay waste si la pieza que sobra no se reutiliza
                        waste += (chosenPiece[1] - verticalCoverDistanceBefore
                                  ) * chosenPiece[0]

                    verticalCoverDistance = 0  # Esto tal vez sobra

            # Agregar la pieza a la lista de pieces
            # la pieza > la distancia horizontal
            elif chosenPiece[0] == horizontalCoverDistance:
                if chosenPiece[1] < verticalCoverDistance:
                    # 4 Pieza = dist horizontal y pieza < dist vertical
                    # No hay que cortar, calcular coords y ajustar dist
                    # vertical

                    pieceCoordinateX = subFrame[0][0] + \
                        width - horizontalCoverDistance
                    pieceCoordinateY = subFrame[0][1]
                    pieceCoordinateZ = subFrame[0][2] + \
                        height - verticalCoverDistance

                    # Revisamos si hay que ajustar la pieza verticalmente para
                    # no generar una pieza < minima
                    if verticalCoverDistance - \
                            chosenPiece[1] < minimumTallSide:
                        # pero si hay ajuste en height
                        remainingDistance = verticalCoverDistance - \
                            chosenPiece[1]
                        missingDistance = minimumTallSide - remainingDistance
                        # agregamos waste por redefinicion
                        waste += chosenPiece[0] * missingDistance
                        spechialPiece = (chosenPiece[0],
                                         chosenPiece[1] - missingDistance)
                        pieceList.append(((pieceCoordinateX, pieceCoordinateY,
                                           pieceCoordinateZ), spechialPiece))
                        verticalCoverDistance -= spechialPiece[1]
                    else:  # No hay necesidad de redefinir pieza ni en height
                        pieceList.append(((pieceCoordinateX, pieceCoordinateY,
                                           pieceCoordinateZ), chosenPiece))
                        verticalCoverDistance -= chosenPiece[1]

                elif chosenPiece[1] == verticalCoverDistance:
                    # 5 pieza = dist horizontal y pieza = dist Vertical
                    # Meter pieza a la lista, calcular coords salir del
                    # programa.
                    pieceCoordinateX = subFrame[0][0] + \
                        width - horizontalCoverDistance
                    pieceCoordinateY = subFrame[0][1]
                    pieceCoordinateZ = subFrame[0][2] + \
                        height - verticalCoverDistance

                    pieceList.append(((pieceCoordinateX, pieceCoordinateY,
                                       pieceCoordinateZ), chosenPiece))

                    return pieceList, waste, waste / (width * height)
                else:
                    # 6 pieza = dist horizontal y pieza > dist Vertical
                    # Hay que cortar la pieza horizontalmente, calcular coords
                    # e iniciar nueva columna.
                    cutPiece = (horizontalCoverDistance, verticalCoverDistance)

                    pieceCoordinateX = subFrame[0][0] + width - cutPiece[0]
                    pieceCoordinateY = subFrame[0][1]
                    # HorizontalCoverDistance -= piezaMinimo[0] # Actualizamos
                    # la distancia a cubrir
                    pieceCoordinateZ = subFrame[0][2] + height - cutPiece[1]
                    pieceList.append(((pieceCoordinateX, pieceCoordinateY,
                                       pieceCoordinateZ), cutPiece))
                    horizontalCoverDistance -= cutPiece[
                        0]  # Actualizamos la distancia a cubrir

                    firstPiece = 1
                    waste += (chosenPiece[1] - verticalCoverDistance
                              ) * chosenPiece[0]
                    verticalCoverDistance = 0
                    return pieceList, waste, waste / (width * height)
            elif chosenPiece[0] > horizontalCoverDistance:

                if chosenPiece[1] < verticalCoverDistance:
                    # 7 Pieza > dist horizontal y pieza < dist vertical
                    # Hay que cortar la pieza verticalmente, calculamos
                    # coordenadas y la colocamos y ajustamos coords
                    cutPiece = (horizontalCoverDistance, chosenPiece[1])
                    waste += (chosenPiece[0] - horizontalCoverDistance
                              ) * chosenPiece[1]

                    pieceCoordinateX = subFrame[0][0] + \
                        width - horizontalCoverDistance
                    pieceCoordinateY = subFrame[0][1]

                    pieceCoordinateZ = subFrame[0][2] + \
                        height - verticalCoverDistance
                    # Revisamos si hay que ajustar la pieza verticalmente para
                    # no generar una pieza < minima
                    if verticalCoverDistance - \
                            chosenPiece[1] < minimumTallSide:
                        # Pero si hay ajuste en height
                        remainingDistance = verticalCoverDistance - \
                            chosenPiece[1]
                        missingDistance = minimumTallSide - remainingDistance
                        # Agregamos waste por redefinicion
                        waste += cutPiece[0] * missingDistance
                        spechialPiece = (cutPiece[0],
                                         cutPiece[1] - missingDistance)
                        pieceList.append(((pieceCoordinateX, pieceCoordinateY,
                                           pieceCoordinateZ), spechialPiece))
                        verticalCoverDistance -= spechialPiece[1]
                    else:  # No hay necesidad de redefinir pieza ni en height
                        pieceList.append(((pieceCoordinateX, pieceCoordinateY,
                                           pieceCoordinateZ), cutPiece))
                        verticalCoverDistance -= cutPiece[1]

                elif chosenPiece[1] == verticalCoverDistance:
                    # 8 pieza > dist horizontal y pieza = dist Vertical
                    # Hay que cortar la pieza verticalmente, calcular coords y
                    # salir
                    cutPiece = (horizontalCoverDistance, verticalCoverDistance)
                    waste += (chosenPiece[0] - horizontalCoverDistance
                              ) * chosenPiece[1]

                    pieceCoordinateX = subFrame[0][0] + width - cutPiece[0]
                    pieceCoordinateY = subFrame[0][1]
                    # HorizontalCoverDistance -= piezaMinimo[0] #actualizamos
                    # la distancia a cubrir
                    # Estaba esto subFrame[0][2]
                    pieceCoordinateZ = subFrame[0][2] + height - cutPiece[1]
                    pieceList.append(((pieceCoordinateX, pieceCoordinateY,
                                       pieceCoordinateZ), cutPiece))
                    # actualizamos la distancia a cubrir
                    horizontalCoverDistance = 0
                    verticalCoverDistance = 0
                    return pieceList, waste, waste / (width * height)
                else:
                    # 9 pieza > dist horizontal y pieza > dist Vertical
                    # Hay que cortar la pieza horizontalmente, calcular coords
                    # y salir
                    cutPiece = (horizontalCoverDistance, verticalCoverDistance)
                    desp = (chosenPiece[0] * chosenPiece[1]) - (
                        horizontalCoverDistance * verticalCoverDistance)
                    waste += desp

                    pieceCoordinateX = subFrame[0][0] + width - cutPiece[0]
                    pieceCoordinateY = subFrame[0][1]
                    # HorizontalCoverDistance -= piezaMinimo[0] #actualizamos
                    # la distancia a cubrir
                    # Estaba esto subFrame[0][2]
                    pieceCoordinateZ = subFrame[0][2] + height - cutPiece[1]
                    pieceList.append(((pieceCoordinateX, pieceCoordinateY,
                                       pieceCoordinateZ), cutPiece))
                    return pieceList, waste, waste / (width * height)

    print('error Case not contemplated')
    return pieceList, waste, waste / (width * height)


# Vector (2900.0, 0.0, 2000.0) 1000.0 1300.0
# subFrame=[(0,0,0),(2743,2438)] #punto inicio,largo,height,direccion
# pieces=[(1219,2743),(2743,1219),(1219,2438),(2438,1219)]
# tamano de los paneles que juega
# pieces=[(1000,1000)]
# s,d,p=paneliza(subFrame,pieces,1)
# print ('Desperdicio ',round(p*100,3),'%')
# print ('Desperdicio ',round(d/1e6,2),'m2')
