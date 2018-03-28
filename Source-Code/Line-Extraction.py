# Author : Eko Rudiawan
import time
import cv2
import numpy as np
import math

IMAGE_WIDTH = 1280
HALF_IMAGE_WIDTH = IMAGE_WIDTH / 2
IMAGE_HEIGHT = 720

angleStep = 1
lengthStep = 10

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
    cv2.setTrackbarPos('gVMin','Green',0)
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
        frame = cv2.imread("d:\Research\BarelangFC-Line-Extraction\Source-Code\image2.jpg")
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

        # Rotation Scanning
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
                        foundGreen = True
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

        cv2.imshow("frame",frame)
        cv2.imshow("New Image",modifiedFrame)
        end = time.time()
        miliseconds = end - start
        print miliseconds
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()