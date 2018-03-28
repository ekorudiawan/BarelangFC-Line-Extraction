# Author : Eko Rudiawan
import time
import cv2
import numpy as np
import math
import matplotlib.pyplot as plt

IMAGE_WIDTH = 1280
HALF_IMAGE_WIDTH = IMAGE_WIDTH / 2
IMAGE_HEIGHT = 720

angleStep = 1
lengthStep = 5

iepfEnable = True
oneCylce = False
showBinary = False

# Transform scanning coordinat to camera coordinat
def transToImgFrame(x,y):
    # x = x + 160
    x = x + HALF_IMAGE_WIDTH
    y = (y-IMAGE_HEIGHT) * -1
    return (x,y)

# Polar to cartesian 
def polToCart(radius, theta):
    x = int(radius * math.cos(math.radians(theta)))
    y = int(radius * math.sin(math.radians(theta)))
    return (x,y)

def nothing(x):
	pass

def measPointToPoint(varP1, varP2):
    return math.sqrt(((varP2[0]-varP1[0])*(varP2[0]-varP1[0])) + ((varP2[1]-varP1[1])*(varP2[1]-varP1[1])))

# https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line
def measPointToLine(varPk, varPl, varP0):
    return abs((varPl[1]-varPk[1])*varP0[0] - (varPl[0]-varPk[0])*varP0[1] + varPl[0]*varPk[1] - varPl[1]*varPk[0]) / math.sqrt( math.pow((varPl[0] - varPk[0]),2) + math.pow((varPl[1] - varPk[1]),2) )

# Fungsi IEPF
# Input berupa list koordinat titik dan list endpoint dari titik 
# Ouput berupa list persamaan garis dalam bentuk Ax + By + C = 0
def iepfFunction(dThreshold, ptList, ePtList):
    maxDPtToLine = 0
    breakPointIndex = -1

    # listLineFunc = [[0,0]]
    # del listLineFunc[:]
    # listLineFunc.append([])
    # listLineFunc.append([])
    # listLineFunc.append([])

    # listLineEndPoint = [[0,0]]
    # del listLineEndPoint[:]
    # listLineEndPoint.append([])
    # listLineEndPoint.append([])
    # listLineEndPoint.append([])

    # jumlahTitik = len(ptList[0])
    jumlahEndpoint = len(ePtList[0])

    # loop sebanyak jumlah end point yang diinputkan
    for i in range(0, jumlahEndpoint-1):
        # A = y2 - y1 / x2 - x1
        # cuk = 0.000000000000000000000000001
        varA = float(ePtList[1][i+1] - ePtList[1][i]) / float(ePtList[0][i+1] - ePtList[0][i])
        # B = -1
        varB = -1.00
        # C = y - Ax
        varC = float(ePtList[1][i] - varA * ePtList[0][i])
        # print 'IEPF Line Function {}x  + {}y + {} = 0'.format(varA, varB, varC)
        # listLineFunc[0].append(varA)
        # listLineFunc[1].append(varB)
        # listLineFunc[2].append(varC)
        # loop sebanyak jumlah titik yang berada diantara endpoint
        for j in range(ePtList[2][i],ePtList[2][i+1]):
            # print 'j = {}'.format(j)
            if j == 0 or j == ePtList[2][i]:
                continue
            # Pengukuran jarak titik ke line
            # d = | ax1 + by1 + c / sqrt(a^2 + b^2) |
            dPtToLine =  float(abs((varA*ptList[0][j] + varB*ptList[1][j] + varC) / (math.sqrt(varA*varA + varB*varB))))
            # print 'D = {}'.format(dPtToLine)
            if dPtToLine > dThreshold:
                if (dPtToLine > maxDPtToLine):
                    maxDPtToLine = dPtToLine
                    breakPointIndex = j

    if(breakPointIndex != -1):
        # Cari nilai MNE        
        ePtList[0].insert(jumlahEndpoint-1, ptList[0][breakPointIndex])
        ePtList[1].insert(jumlahEndpoint-1, ptList[1][breakPointIndex])
        ePtList[2].insert(jumlahEndpoint-1, breakPointIndex)

        # pawal = [ePtList[0][jumlahEndpoint-2],ePtList[1][jumlahEndpoint-2]]
        # pakhir = [10,10]
        # pnol = [5,4]
        # varMNE0 = maxDPtToLine / measPointToLine()
        # print ePtList
        ePtList = iepfFunction(dThreshold, ptList, ePtList)
    # else:
        # plt.title("IEPF Algorithm")
        # plt.plot(ptList[0], ptList[1], 'ro')
        # plt.plot(ePtList[0], ePtList[1])
        # plt.axis([0, 1000, 0, 1000])
        # plt.show()
        # print listLineFunc
    return ePtList

def mergeLine(mneThreshold, ptList, ePtList):
    jumlahEndpoint = len(ePtList[0])
    for i in range(0, jumlahEndpoint-2):
        # print 'garis'
        varPk = [ePtList[0][i] , ePtList[1][i]]
        varPl = [ePtList[0][i+2] , ePtList[1][i+2]]
        varP0 = [ePtList[0][i+1] , ePtList[1][i+1]]
        varMaxDistance = measPointToLine(varPk,varPl,varP0)
        varPk = [ePtList[0][i] , ePtList[1][i]]
        varPl = [ePtList[0][i+1] , ePtList[1][i+1]]
        prevIndex = ePtList[2][i+1] - 1
        nextIndex = ePtList[2][i+1] + 1
        # print 'PREV {} NEXT{}'.format(prevIndex, nextIndex) 
        varP0 = [ptList[0][prevIndex], ptList[1][nextIndex]]
        # print 'K {},{} L {},{} P0 {},{}'.format(varPk[0], varPk[1], varPl[0], varPl[1], varPl[0], varPl[1])
        print varPk
        print varPl
        print varP0
        xx = measPointToLine(varPk,varPl,varP0)
        varMNEprev = varMaxDistance / xx
        # print 'MNE Prev {}'.format(varMNEprev)
        print 'Prev list'
        print ePtList
        if varMNEprev > 2:
            # remX = ePtList[0][i+1]
            # remY = ePtList[1][i+1]
            # remIndex = ePtList[2][i+1]
            # ePtList[0].remove(remX)
            ePtList[0].pop(i+1)
            ePtList[1].pop(i+1)
            ePtList[2].pop(i+1)
        # print 'K {},{} L {},{}'.format(varPk[0], varPk[1], varPl[0], varPl[1],)
        # for j in range(ePtList[2][i],ePtList[2][i+1]):
        print 'last list'
        print ePtList
    return ePtList

def main():
    # Green Color Default Parameter
    cv2.namedWindow('Green')
    cv2.namedWindow('White')
    cv2.createTrackbar('gHMin','Green',0,255,nothing)
    cv2.createTrackbar('gHMax','Green',0,255,nothing)
    cv2.createTrackbar('gSMin','Green',0,255,nothing)
    cv2.createTrackbar('gSMax','Green',0,255,nothing)
    cv2.createTrackbar('gVMin','Green',0,255,nothing)
    cv2.createTrackbar('gVMax','Green',0,255,nothing)
    
    cv2.setTrackbarPos('gHMin','Green',40)
    cv2.setTrackbarPos('gHMax','Green',60)
    cv2.setTrackbarPos('gSMin','Green',50)
    cv2.setTrackbarPos('gSMax','Green',255)
    cv2.setTrackbarPos('gVMin','Green',55)
    cv2.setTrackbarPos('gVMax','Green',255)
    
    # White Color Default Parameter
    cv2.createTrackbar('wHMin','White',0,255,nothing)
    cv2.createTrackbar('wHMax','White',0,255,nothing)
    cv2.createTrackbar('wSMin','White',0,255,nothing)
    cv2.createTrackbar('wSMax','White',0,255,nothing)
    cv2.createTrackbar('wVMin','White',0,255,nothing)
    cv2.createTrackbar('wVMax','White',0,255,nothing)
   
    cv2.setTrackbarPos('wHMin','White',65)
    cv2.setTrackbarPos('wHMax','White',255)
    cv2.setTrackbarPos('wSMin','White',0)
    cv2.setTrackbarPos('wSMax','White',255)
    cv2.setTrackbarPos('wVMin','White',0)
    cv2.setTrackbarPos('wVMax','White',255)

    # Calculating maximum length
    maxL = math.sqrt(HALF_IMAGE_WIDTH*HALF_IMAGE_WIDTH+IMAGE_HEIGHT*IMAGE_HEIGHT)
    maxL = int(maxL)
    # print maxL
    
    while(1):
        start = time.time()
        # Load image from file
        frame = cv2.imread("d:\Research\BarelangFC-Line-Extraction\Source-Code\image4.jpg")
        print frame.shape[:2]
        modifiedFrame = frame.copy()

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        gHMax = cv2.getTrackbarPos('gHMax','Green')
        gHMin = cv2.getTrackbarPos('gHMin','Green')
        gSMax = cv2.getTrackbarPos('gSMax','Green')
        gSMin = cv2.getTrackbarPos('gSMin','Green')
        gVMax = cv2.getTrackbarPos('gVMax','Green')
        gVMin = cv2.getTrackbarPos('gVMin','Green')

        wHMax = cv2.getTrackbarPos('wHMax','White')
        wHMin = cv2.getTrackbarPos('wHMin','White')
        wSMax = cv2.getTrackbarPos('wSMax','White')
        wSMin = cv2.getTrackbarPos('wSMin','White')
        wVMax = cv2.getTrackbarPos('wVMax','White')
        wVMin = cv2.getTrackbarPos('wVMin','White')

        lowerGreen = np.array([gHMin,gSMin,gVMin])
        upperGreen = np.array([gHMax,gSMax,gVMax])

        lowerWhite = np.array([wHMin,wSMin,wVMin])
        upperWhite = np.array([wHMax,wSMax,wVMax])

        # Binary filtering
        gBinary = cv2.inRange(hsv, lowerGreen, upperGreen)
        wBinary = cv2.inRange(hsv, lowerWhite, upperWhite)

        listPointP = [[0,0]]
        del listPointP[:]
        listPointP.append([])
        listPointP.append([])

        # Rotation Scanning
        dBetweenP = 0
        for i in range(180,0-angleStep,angleStep*-1):
            foundGreen = False
            lastFoundGreen = False
            lastFoundWhite = False
            foundWhite = False
            
            for j in range(maxL,0,lengthStep*-1):
                # print 'Polar {},{}'.format(j, i)
                x,y =  polToCart(j,i)
                # print 'Car {},{}'.format(x, y)
                x,y =  transToImgFrame(x,y)
                # print 'CV{},{}'.format(x, y)
                if x >= 0 and x < IMAGE_WIDTH and y >= 0 and y < IMAGE_HEIGHT:          
                    # print gBinary        
                    #  kolom x baris 
                    if foundGreen == False:
                        warna = gBinary.item(y,x)   
                    else:
                        warna = wBinary.item(y,x) 
                else:
                    warna = 0

                # Jika belum ketemu hijau
                if foundGreen == False:
                    if warna == 255:
                        dBetweenP = 0
                        foundGreen = True
                        # Cek jarak dulu sebelum dimasukkan ke list
                        listIndex = len(listPointP[0])-1
                        print 'Index '
                        print listIndex
                        if listIndex != -1:
                            varP1 = [0,0]
                            varP1[0] = x
                            varP1[1] = y
                            varP2 = [0,0]
                            varP2[0] = listPointP[0][listIndex] 
                            varP2[1] = listPointP[1][listIndex]
                            print 'P1 '
                            print varP1
                            print 'P2 '
                            print varP2
                            dBetweenP = measPointToPoint(varP1,varP2)
                        # else:
                        # dBetweenP = 0
                        print 'Jarak '
                        print dBetweenP
                        # Masukkan koordinat ke dalam list
                        if dBetweenP < 50:
                            listPointP[0].append(x)
                            listPointP[1].append(y)
                        # if listIndex != -1:
                            # print listPointP
                        color = (0,0,255)
                        # print 'merahhhhhhh'
                        # cv2.circle(frame,(x,y), 2, (0,0,255), -1)
                    elif warna == 0:
                        color = (255,0,0)
                        # print 'bitu'

                # Jika sudah ketemu hijau cek warna putih
                else:
                    if warna == 255:
                        foundWhite = True                        
                        color = (0,255,255)
                        # print 'merahhhhhhh'
                        # cv2.circle(frame,(x,y), 2, (0,0,255), -1)
                    elif warna == 0:
                        color = (255,255,0)
                        # print 'bitu'
                if lastFoundGreen == False and foundGreen == True:
                    cv2.circle(modifiedFrame,(x,y), 2, color, -1)
                if lastFoundWhite == False and foundWhite == True:
                    cv2.circle(modifiedFrame,(x,y), 2, color, -1)
                # Update parameter
                lastFoundGreen = foundGreen
                lastFoundWhite = foundWhite
                if foundWhite:
                    break

        
        end = time.time()
        miliseconds = end - start
        print miliseconds
        # print listPointP

        # Input 2 buah endpoint untuk masukan awal
        if iepfEnable == True:
            endPoint0 = 0
            endPointN = len(listPointP[0])-1

            listEndPoint = [[0,0]]
            del listEndPoint[:]
            listEndPoint.append([])
            listEndPoint.append([])
            listEndPoint.append([])

            # endPoint0 x,y coordinat dan index
            listEndPoint[0].append(listPointP[0][endPoint0])
            listEndPoint[1].append(listPointP[1][endPoint0])
            listEndPoint[2].append(endPoint0)

            # endPointN x,y coordinat dan index
            listEndPoint[0].append(listPointP[0][endPointN])
            listEndPoint[1].append(listPointP[1][endPointN])
            listEndPoint[2].append(endPointN+1)

            listPredLine = iepfFunction(50, listPointP, listEndPoint)

            plt.title("IEPF Algorithm")
            plt.plot(listPointP[0], listPointP[1], 'ro')
            plt.plot(listPredLine[0], listPredLine[1])
            plt.axis([0, IMAGE_WIDTH, 0,IMAGE_HEIGHT])
            plt.show()

            print 'Predicted Line'
            print listPredLine
            for i in range(0,len(listPredLine[0])-1):
                cv2.line(modifiedFrame,(listPredLine[0][i],listPredLine[1][i]),(listPredLine[0][i+1],listPredLine[1][i+1]),(255,0,0),5)
        
        cv2.imshow("frame",frame)
        cv2.imshow("New Image",modifiedFrame)
        if showBinary == True:
            cv2.imshow("Binary",gBinary)
        # Plot list of point


        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            break
        if oneCylce == True:
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()