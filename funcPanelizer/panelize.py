#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 12:39:21 2018

@author: orion
"""



def calculaDesperdicio(longitudPieza,anchoDePieza,distanciaCubrir):
    ''' Funcion que calcula el desperdicio en terminos de area de acuerdo al 
    la longitud de una pieza en el sentido que se estudia y el ancho perpendicular
    y la distancia a cubrir, regresa el desperdicio en unidades cuadradas'''
    if longitudPieza > distanciaCubrir:
        return (longitudPieza-distanciaCubrir)*anchoDePieza
    elif longitudPieza == distanciaCubrir:
        return 0
    else:
        return (longitudPieza-(distanciaCubrir%longitudPieza))*anchoDePieza
    
def reduceListaPiezas(piezas,restriccion):
    '''Funcion que reduce la lista de piezas a usar cuando solo pueden ser utilizadas
    ciertas piezas con el ancho = restriccion'''
    resultado=[]
    for candidato in piezas:
        if candidato[0]==restriccion:
            resultado.append(candidato)
    return resultado

def eligePieza(piezas,distanciaH,distanciaV): 
    ''' Funcion para encontrar el desperdicion minimo dadas distancias a cubrir
    horizontal y vertical y varias piezas regresa una tupla con la pieza con desperdicio minimo
    y el desperdicio (Area)'''
    
    #revisamos en ambas direcciones
    desperdiciosV= [calculaDesperdicio(x[1],x[0],distanciaV) for x in piezas]
    desperdiciosH= [calculaDesperdicio(x[0],x[1],distanciaH) for x in piezas]
    sumaDesperdicios=[sum(x) for x in zip(desperdiciosV,desperdiciosH)]
    #funcion agregadora de desperdicio.
    minpos = sumaDesperdicios.index(min(sumaDesperdicios)) 
    return (minpos,sumaDesperdicios[minpos])
    
    
def paneliza(subFrame,piezas,reutilizar=1,anchoMinimoLado=300,anchoMinimoAlto=500):
    
    '''Funcion que toma un subframe y regresa una lista de piezas para panelizarlo
    regresa una lista de tuplas (coordenadas,(piezax o y,piezaz)) para llenarlo'''
    desperdicio=0
    tamanoMinimo=300 #tama minimo para aceptar piezas sobrantes.

    listaPiezas=[] #tuplas de piezas a colocar ((x,y,z),largo,ancho,desperdicio)
    listaReuso=[] #aqui guardaremos las piezas de reuso.
    ancho = subFrame[1][0]
    alto = subFrame[1][1]
        
    distanciaCubrirH=ancho
    distanciaCubrirV=alto
    while distanciaCubrirH > 0:
        primeraPieza=1
        distanciaCubrirV=alto
        while distanciaCubrirV > 0:
            ##############################################
             #codigo que solo se ejecuta si es la primera pieza de la columna
            if len(listaReuso)==0:
                if primeraPieza==1: #podemos escoger la siguiente pieza arriba con cualquier ancho
                    piezaElegida=piezas[eligePieza(piezas,distanciaCubrirH,distanciaCubrirV)[0]]
                    primeraPieza=0 #elegimos pieza
                    
                else: #ya hay una pieza abajo y solo podemos escoger piezas con el mismo ancho.
                    primeraPiezaAncho=listaPiezas[-1][1][0]
                    piezaPreElegida=piezas[eligePieza(piezas,distanciaCubrirH,distanciaCubrirV)[0]]
                    if piezaPreElegida[0]>=distanciaCubrirH and primeraPiezaAncho >= distanciaCubrirH: #revisamos si la pieza pre elegida puede llenar el espacio faltante
                        piezaElegida=piezaPreElegida #si si, tomamos esta pieza como buena
                    else: #la pieza pre elegida no llena el espacio y hay que limitar a piezas con el ancho de la que sobro
                        anchoPieza=piezaElegida[0]
                        piezasPosibles=reduceListaPiezas(piezas,anchoPieza)
                        piezaElegida=piezasPosibles[eligePieza(piezasPosibles,anchoPieza,distanciaCubrirV)[0]]
                    
            else: #tomar la pieza que sobro
                piezaElegida=listaReuso.pop()
                primeraPieza=0
                
                
             ###################################       
            if piezaElegida[0]< distanciaCubrirH: #la pieza <= que la dist horizontal
                if piezaElegida[1]<distanciaCubrirV: 
                    #####################################################
                    #1 Pieza < dist horizontal y pieza < dist vertical 
                    #####################################################
                # No hay que cortar la pieza, calculamos coordenadas y la colocamos y ajusto distancias
                    coordenadaPiezaX =subFrame[0][0]+ancho-distanciaCubrirH
                    coordenadaPiezaY =subFrame[0][1]                        
                    coordenadaPiezaZ = subFrame[0][2]+alto-distanciaCubrirV
                    #revisar que la pieza ultima en el margen derecho no sea menor que el minimo
                    if distanciaCubrirH-piezaElegida[0]<anchoMinimoLado:
                        distQueda=distanciaCubrirH-piezaElegida[0]
                        falta=anchoMinimoLado-distQueda
                        desperdicio+=piezaElegida[1]*falta #agregamos desperdicio por redefinicion
                        piezaEspecial=(piezaElegida[0]-falta,piezaElegida[1])
                        
                        if distanciaCubrirV-piezaElegida[1]<anchoMinimoAlto: #hay ajuste en ancho y en alto
                           distQueda=distanciaCubrirV-piezaElegida[1]
                           falta=anchoMinimoAlto-distQueda
                           desperdicio+=piezaEspecial[0]*falta #agregamos desperdicio por redefinicion
                           piezaReEspecial=(piezaEspecial[0],piezaElegida[1]-falta)
                           listaPiezas.append(((coordenadaPiezaX,coordenadaPiezaY,coordenadaPiezaZ),piezaReEspecial))
                           distanciaCubrirV -= piezaReEspecial[1]
                        else: #solo se redefinio pieza en lo ancho.
                           listaPiezas.append(((coordenadaPiezaX,coordenadaPiezaY,coordenadaPiezaZ),piezaEspecial))
                           distanciaCubrirV -= piezaEspecial[1] 
                    else: # no hay necesidad de redefinir la pieza en lo ancho
                        if distanciaCubrirV-piezaElegida[1]<anchoMinimoAlto: #pero si hay ajuste en alto
                           distQueda=distanciaCubrirV-piezaElegida[1]
                           falta=anchoMinimoAlto-distQueda
                           desperdicio+=piezaElegida[0]*falta #agregamos desperdicio por redefinicion
                           piezaEspecial=(piezaElegida[0],piezaElegida[1]-falta)
                           listaPiezas.append(((coordenadaPiezaX,coordenadaPiezaY,coordenadaPiezaZ),piezaEspecial))
                           distanciaCubrirV -= piezaReEspecial[1]
                        else: #no hay necesidad de redefinir pieza ni en ancho ni alto
                           listaPiezas.append(((coordenadaPiezaX,coordenadaPiezaY,coordenadaPiezaZ),piezaElegida))
                           distanciaCubrirV -= piezaElegida[1]
                    
                    
                elif piezaElegida[1]==distanciaCubrirV:
                    #######################################################
                    #2Pieza < dist horizontal y pieza = dist vertical 
                    ######################################################
                    coordenadaPiezaX =subFrame[0][0]+ancho-distanciaCubrirH
                    coordenadaPiezaY =subFrame[0][1]
                    coordenadaPiezaZ = subFrame[0][2]+alto-distanciaCubrirV
                    #revisar que la pieza ultima en el margen derecho no sea menor que el minimo
                    if distanciaCubrirH-piezaElegida[0]<anchoMinimoLado:
                        distQueda=distanciaCubrirH-piezaElegida[0]
                        falta=anchoMinimoLado-distQueda
                        desperdicio+=piezaElegida[1]*falta #agregamos desperdicio por redefinicion
                        piezaEspecial=(piezaElegida[0]-falta,piezaElegida[1])
                        listaPiezas.append(((coordenadaPiezaX,coordenadaPiezaY,coordenadaPiezaZ),piezaEspecial))
                        distanciaCubrirV = 0
                        distanciaCubrirH -= piezaEspecial[0]
                    else: # no hay necesidad de redefinir la pieza 
                        listaPiezas.append(((coordenadaPiezaX,coordenadaPiezaY,coordenadaPiezaZ),piezaElegida))
                        distanciaCubrirV = 0
                        distanciaCubrirH -= piezaElegida[0] #actualizamos la distancia a cubrir
                        primeraPieza=1
                                    
                else: 
                    #######################################################
                    #3pieza < dist horizontal y pieza > dist Vertical
                    #######################################################
                # hay que cortar la pieza horizontalmente, calcular coords e iniciar nueva columna.
                    piezaCortada=(piezaElegida[0],distanciaCubrirV)
                    
                    coordenadaPiezaX =subFrame[0][0]+ancho-distanciaCubrirH
                    coordenadaPiezaY =subFrame[0][1]
                    coordenadaPiezaZ = subFrame[0][2]+alto-distanciaCubrirV
                    #revisar que la proxima pieza ultima en el margen derecho no sea menor que el minimo
                    if distanciaCubrirH-piezaElegida[0]<anchoMinimoLado:
                        distQueda=distanciaCubrirH-piezaElegida[0]
                        falta=anchoMinimoLado-distQueda
                        desperdicio+=piezaCortada[1]*falta #agregamos desperdicio por redefinicion
                        piezaEspecial=(piezaCortada[0]-falta,piezaCortada[1])
                        listaPiezas.append(((coordenadaPiezaX,coordenadaPiezaY,coordenadaPiezaZ),piezaEspecial))
                        distanciaAntesCubrirV=distanciaCubrirV
                        distanciaCubrirV = 0
                        distanciaCubrirH -= piezaEspecial[0]
                    else: # no hay necesidad de redefinir la pieza 
                        listaPiezas.append(((coordenadaPiezaX,coordenadaPiezaY,coordenadaPiezaZ),piezaCortada))
                        distanciaAntesCubrirV=distanciaCubrirV
                        distanciaCubrirV = 0
                        distanciaCubrirH -= piezaCortada[0] #actualizamos la distancia a cubrir
                        primeraPieza=1
                    
                    if reutilizar==1: # si se reutiliza la pieza que sobraría
                        piezaSobrante=(piezaCortada[0],piezaElegida[1]-piezaCortada[1])
                        if piezaSobrante[1]>=tamanoMinimo:
                            listaReuso.append(piezaSobrante)
                        else: #la pieza no se utilizó por ser chica y por lo tanto se desperdicia
                            desperdicio += (piezaElegida[1]-distanciaAntesCubrirV)*piezaCortada[0]
                                            
                    else:
                        #solo hay desperdicio si la pieza que sobra no se reutiliza
                        desperdicio += (piezaElegida[1]-distanciaAntesCubrirV)*piezaElegida[0]
                        
                        
                    distanciaCubrirV =0 #esto tal vez sobra
                    
                
                 #agregar la pieza a la lista de piezas
            elif piezaElegida[0]== distanciaCubrirH: #la pieza > la distancia horizontal
                if piezaElegida[1]< distanciaCubrirV: 
                    #####################################################
                    #4Pieza = dist horizontal y pieza < dist vertical
                    #####################################################
                    # No hay que cortar, calcular coords y ajustar dist vertical
                    
                    coordenadaPiezaX =subFrame[0][0]+ancho-distanciaCubrirH
                    coordenadaPiezaY =subFrame[0][1]
                    coordenadaPiezaZ = subFrame[0][2]+alto-distanciaCubrirV
                    
                    #revisamos si hay que ajustar la pieza verticalmente para no generar una pieza < minima 
                    if distanciaCubrirV-piezaElegida[1]<anchoMinimoAlto: #pero si hay ajuste en alto
                           distQueda=distanciaCubrirV-piezaElegida[1]
                           falta=anchoMinimoAlto-distQueda
                           desperdicio+=piezaElegida[0]*falta #agregamos desperdicio por redefinicion
                           piezaEspecial=(piezaElegida[0],piezaElegida[1]-falta)
                           listaPiezas.append(((coordenadaPiezaX,coordenadaPiezaY,coordenadaPiezaZ),piezaEspecial))
                           distanciaCubrirV -= piezaEspecial[1]
                    else: #no hay necesidad de redefinir pieza ni en alto
                           listaPiezas.append(((coordenadaPiezaX,coordenadaPiezaY,coordenadaPiezaZ),piezaElegida))
                           distanciaCubrirV -= piezaElegida[1]
                                                       
                elif piezaElegida[1]== distanciaCubrirV: 
                    #######################################################
                    #5pieza = dist horizontal y pieza = dist Vertical
                    #######################################################
                    # meter pieza a la lista, calcular coords salir del programa.
                    coordenadaPiezaX =subFrame[0][0]+ancho-distanciaCubrirH
                    coordenadaPiezaY =subFrame[0][1]
                    coordenadaPiezaZ = subFrame[0][2]+alto-distanciaCubrirV
                    
                    listaPiezas.append(((coordenadaPiezaX,coordenadaPiezaY,coordenadaPiezaZ),piezaElegida))
                    
                    return listaPiezas,desperdicio,desperdicio/(ancho*alto)
                else:
                    #######################################################
                    #6pieza = dist horizontal y pieza > dist Vertical
                    #######################################################
                    # hay que cortar la pieza horizontalmente, calcular coords e iniciar nueva columna.
                    piezaCortada=(distanciaCubrirH,distanciaCubrirV)
                    
                    coordenadaPiezaX =subFrame[0][0]+ancho-piezaCortada[0]
                    coordenadaPiezaY =subFrame[0][1]
                        #distanciaCubrirH -= piezaMinimo[0] #actualizamos la distancia a cubrir
                    coordenadaPiezaZ = subFrame[0][2]+alto-piezaCortada[1]
                    listaPiezas.append(((coordenadaPiezaX,coordenadaPiezaY,coordenadaPiezaZ),piezaCortada))
                    distanciaCubrirH -= piezaCortada[0] #actualizamos la distancia a cubrir
                    
                    primeraPieza=1
                    desperdicio += (piezaElegida[1]-distanciaCubrirV)*piezaElegida[0]
                    distanciaCubrirV =0
                    return listaPiezas,desperdicio,desperdicio/(ancho*alto)          
            elif piezaElegida[0]> distanciaCubrirH:
                
                if piezaElegida[1]< distanciaCubrirV: 
                    #####################################################
                    #7Pieza > dist horizontal y pieza < dist vertical
                    #####################################################
                    # hay que cortar la pieza verticalmente, calculamos coordenadas y la colocamos y ajustamos coords
                    piezaCortada=(distanciaCubrirH,piezaElegida[1])
                    desperdicio += (piezaElegida[0]-distanciaCubrirH)*piezaElegida[1]
                    
                    coordenadaPiezaX =subFrame[0][0]+ancho-distanciaCubrirH
                    coordenadaPiezaY =subFrame[0][1]
                        
                    coordenadaPiezaZ = subFrame[0][2]+alto-distanciaCubrirV
                    #revisamos si hay que ajustar la pieza verticalmente para no generar una pieza < minima 
                    if distanciaCubrirV-piezaElegida[1]<anchoMinimoAlto: #pero si hay ajuste en alto
                           distQueda=distanciaCubrirV-piezaElegida[1]
                           falta=anchoMinimoAlto-distQueda
                           desperdicio+=piezaCortada[0]*falta #agregamos desperdicio por redefinicion
                           piezaEspecial=(piezaCortada[0],piezaCortada[1]-falta)
                           listaPiezas.append(((coordenadaPiezaX,coordenadaPiezaY,coordenadaPiezaZ),piezaEspecial))
                           distanciaCubrirV -= piezaEspecial[1]
                    else: #no hay necesidad de redefinir pieza ni en alto
                           listaPiezas.append(((coordenadaPiezaX,coordenadaPiezaY,coordenadaPiezaZ),piezaCortada))
                           distanciaCubrirV -= piezaCortada[1]
                    
                                                                    
                elif piezaElegida[1]== distanciaCubrirV: 
                    #######################################################
                    #8pieza > dist horizontal y pieza = dist Vertical
                    #######################################################
                    # hay que cortar la pieza verticalmente, calcular coords y salir
                    piezaCortada=(distanciaCubrirH,distanciaCubrirV)
                    desperdicio += (piezaElegida[0]-distanciaCubrirH)*piezaElegida[1]
                    
                    coordenadaPiezaX =subFrame[0][0]+ancho-piezaCortada[0]
                    coordenadaPiezaY =subFrame[0][1]
                        #distanciaCubrirH -= piezaMinimo[0] #actualizamos la distancia a cubrir
                    coordenadaPiezaZ = subFrame[0][2]+alto-piezaCortada[1]# estaba esto subFrame[0][2]
                    listaPiezas.append(((coordenadaPiezaX,coordenadaPiezaY,coordenadaPiezaZ),piezaCortada))
                    distanciaCubrirH =0 #actualizamos la distancia a cubrir
                    distanciaCubrirV =0
                    return listaPiezas,desperdicio,desperdicio/(ancho*alto)
                else:
                    #######################################################
                    #9pieza > dist horizontal y pieza > dist Vertical
                    #######################################################
                    # hay que cortar la pieza horizontalmente, calcular coords y salir
                    piezaCortada=(distanciaCubrirH,distanciaCubrirV)
                    desp=(piezaElegida[0]*piezaElegida[1])-(distanciaCubrirH*distanciaCubrirV)
                    desperdicio += desp
                    
                    coordenadaPiezaX =subFrame[0][0]+ancho-piezaCortada[0]
                    coordenadaPiezaY =subFrame[0][1]
                        #distanciaCubrirH -= piezaMinimo[0] #actualizamos la distancia a cubrir
                    coordenadaPiezaZ = subFrame[0][2]+alto-piezaCortada[1]# estaba esto subFrame[0][2]
                    listaPiezas.append(((coordenadaPiezaX,coordenadaPiezaY,coordenadaPiezaZ),piezaCortada))
                    return listaPiezas,desperdicio,desperdicio/(ancho*alto)
 
    print('error Caso no contemplado')
    return listaPiezas,desperdicio,desperdicio/(ancho*alto)
#Vector (2900.0, 0.0, 2000.0) 1000.0 1300.0
subFrame=[(2900,0,2000),(1000,1300)] #punto inicio,largo,alto,direccion
#piezas=[(1219,2438),(2438,1219),(2743,1219),(1219,2743)] #tamano de los paneles que juega
piezas=[(1000,1000)]
s,d,p=paneliza(subFrame,piezas,1)
print ('Desperdicio ',round(p*100,3),'%')
print ('Desperdicio ',round(d/1e6,2),'m2')
