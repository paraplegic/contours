#!/usr/bin/env python

import time as time
import numpy as np
import cv2

display = True
stopMotion = False
height = 480
width = 640

CV_CAP_PROP_FRAME_WIDTH = 3
CV_CAP_PROP_FRAME_HEIGHT = 4

jitter = 400
if stopMotion:
  jitter = 10000

def getContours( image ):
  blur = cv2.pyrMeanShiftFiltering( image, 21, 31 )
  gray = cv2.cvtColor( blur, cv2.COLOR_BGR2GRAY )
  ret, threshold = cv2.threshold( gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU )
  rv,z = cv2.findContours( threshold, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE )
  return rv

def showContours( image, lst ):
  if not display:
    return
  return cv2.drawContours( image, lst, -1, (0,255,0), 2 )

def writeText( image, at, txt, colour ):
  if colour == None:
    colour = (0,0,0)
  font = cv2.FONT_HERSHEY_SIMPLEX
  cv2.putText( image, txt, at, font, 0.4, colour, 2 )

def boundingCircles( image, clist ):
  ix = 0
  for c in clist:
    (x,y),rad = cv2.minEnclosingCircle( c )
    centre = (int(x),int(y))
    radius = int( rad )
    if radius > 20 and radius < 200:
      cv2.circle( image, centre, radius, (0,255,0), 2 )
      txt = "R=%s" % radius
      writeText( image, centre, txt, (0,255,0) )
    ix += 1

def boundingBoxes( image, clist ):
  rv = []
  for c in clist:
    T = cv2.minAreaRect( c )
    x = int( round( T[0][0] ) )
    y = int( round( T[0][1] ) ) 
    w = int( round( T[1][0] ) ) 
    h = int( round( T[1][1] ) ) 
    t = int( round( T[2] ) ) 
    x += -w/2
    y += -h/2
    area = w * h
    ## x,y,w,h = cv2.boundingRect(c)
    if display and w > 10 and w < 90:
      cv2.rectangle( image, (x,y), (x+w,y+h), (223,223,223), 2 )
      txt = "(%d x %d)" % (w, h)
      writeText( image, (x,y), txt, (0,0,0) )
      rv.append( (w,h) )
    return rv

def webCam( num ):

  stream = cv2.VideoCapture( num )
  if stream.isOpened() == False:
    print "Cannot open input video stream!"
    exit()

  ht = stream.get( CV_CAP_PROP_FRAME_HEIGHT )
  wd = stream.get( CV_CAP_PROP_FRAME_WIDTH )
  print "camera opened: image size ", wd, "x", ht
  return stream

def getFrame( stream ):
  rv, frame = stream.read()
  if rv:
    return frame

  return None

def show( image ):

  if not display:
    return False

  cv2.imshow( 'Display',image )
  if cv2.waitKey(jitter) & 0xff == 'q':
    return True
  return False

def save( image, file ):
  cv2.imwrite( file, image )


def main():
  
  cam = webCam( 0 )
  for ix in range( 30 ):
    frame = getFrame( cam )

  ## cv2.namedWindow( 'Display', cv2.WINDOW_NORMAL )
  while True:
    if display:
      time.sleep(0.05)
    else:
      time.sleep(1.0)
    frame = None
    start = time.time()
    while frame is None:
      frame = getFrame( cam )
    contours = getContours( frame )
    ## showContours( frame, contours )
    bb = boundingBoxes( frame, contours )
    bbx = time.time()
    box = None
    if len( bb ) > 0:
      box = bb[0]
    print "bbx calc: %s %s" % ( str( bbx - start ), box )
    ## boundingCircles( frame, contours )
    if show( frame ):
      break

  save( frame, 'save.jpg' )
  cv2.destroyAllWindows()

if __name__ == "__main__":
  main()
