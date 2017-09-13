#!/usr/bin/env python

import time as time
import numpy as np
import cv2

from pkg_resources import parse_version

display = True
width = 640
height = 480
ntries = 20
jitter = 1

OPCV3 = parse_version(cv2.__version__) >= parse_version('3')


# returns OpenCV VideoCapture property id given, e.g., "FPS"
def vidProperty(prop):
  return getattr(cv2 if OPCV3 else cv2.cv, ("" if OPCV3 else "CV_") + "CAP_PROP_" + prop)

def XXXgetContours( image ):
  ## blur = cv2.pyrMeanShiftFiltering( image, 21, 36 )
  blur = cv2.GaussianBlur(image, (5, 5), 0)
  gray = cv2.cvtColor( blur, cv2.COLOR_BGR2GRAY )
  ret, threshold = cv2.threshold( gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU )
  rv,z = cv2.findContours( threshold, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE )
  return rv

def getContours( image ):
  # threshold image
  ret, threshed_img = cv2.threshold(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), 127, 255, cv2.THRESH_BINARY)
  # find contours and get the external one
  contours, hier = cv2.findContours(threshed_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
  return contours


def showContours( image, lst ):

	if display:
		return cv2.drawContours( image, lst, -1, (0,255,0), 2 )

	return None

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
		x,y,w,h = cv2.boundingRect(c)
		if h > (int(0.8*height)) or w > int(width/2):
			continue

		if w > 40 and h > 80:
			rv.append( (x,y,w,h) )

	return rv

def webCam( num ):

  stream = cv2.VideoCapture( num )
  if stream.isOpened() == False:
    print "Cannot open input video stream!"
    exit()

  height = stream.get( vidProperty( 'FRAME_HEIGHT' ) )
  width = stream.get( vidProperty( 'FRAME_WIDTH' ) )
  sat = stream.get( vidProperty( 'SATURATION' ) )
  con = stream.get( vidProperty( 'CONTRAST' ) )
  fps = stream.get( vidProperty( 'FPS' ) )
  print "camera opened: image size ", width, "x", height
  print "sat: %s con: %s fps: %s" % ( sat, con, fps ) 
  ## stream.set( vidProperty( 'FRAME_HEIGHT' ), int( height/2 ) )
  ## stream.set( vidProperty( 'FRAME_WIDTH' ), int( width/2 ) )
  stream.set( vidProperty( 'FPS' ), 27 )
  stream.set( vidProperty( 'SATURATION' ), sat/2 )
  stream.set( vidProperty( 'CONTRAST' ), con*2 )
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

def obatts( bx ):
	x = bx[0]
	y = bx[1]
	w = bx[2]
	h = bx[3]
	return ( x, y, w, h )

def getObjects( cam ):
	frame = None
	while frame is None:
		frame = getFrame( cam )

	contours = None
	while contours is None:
		contours = getContours( frame )

	bbxs = boundingBoxes( frame, contours )

	rv = []
	for bx in bbxs:
		x,y,w,h = obatts( bx )
		rv.append( (w,h) )
		if display:
			txt = "(%d x %d)" % (w,h)
			cv2.rectangle( frame, (x,y), (x+w,y+h), (0,223,0), 2 )
			writeText( frame, (int(x+(w/4)),int(y+(h/2))), txt, (0,223,0) )

	if show( frame ):
		exit( 0 )

	return rv

def deJitter( cam, n ):
	x = {}
	y = {}
	ix = n 
	while ix > 0:
		ix -= 1
		ob = getObjects( cam )
		i = 0 
		while i < len( ob ):
			if i in x:
				x[i] += ob[i][0]
				y[i] += ob[i][1]
			else:
				x[i] = ob[i][0]
				y[i] = ob[i][1]
			i += 1

	i = 0 
	rv = []
	while i < len( x ):
		t = ( int( x[i]/n ), int( y[i]/n ) )
		rv.append( t )
		i += 1

	return rv
	


def getSize( cam, n ):
	x = 0
	y = 0
	ix = n 
	rv = []
	while ix > 0:
		frame = None
		while frame is None:
			frame = getFrame( cam )

		contours = None
		while contours is None:
			contours = getContours( frame )

		bb = boundingBoxes( frame, contours )
		if len( bb ) > 0:
			x += bb[0][0]
			y += bb[0][1]
			ix -= 1
			if show( frame ):
				exit( 0 )
			rv.append( ( int(x/n), int(y/n) ) )

	return rv

def main():
  
  cam = webCam( 2 )
  start = time.time()
  for ix in range( 30 ):
    frame = getFrame( cam )
  end = time.time()
  print "30 frames in %s seconds." % str( end - start )

  while True:
    start = time.time()
    ## box = getSize( cam, ntries )
    ob = deJitter( cam, ntries )
    bbx = time.time()
    print "%d objects sampled %s times %s %s." % ( len( ob ), ntries, ob, str( bbx - start ) )
    ## print "bbx calc: %s %s" % ( str( bbx - start ), box )
    ## boundingCircles( frame, contours )

  save( frame, 'save.jpg' )
  cv2.destroyAllWindows()

if __name__ == "__main__":
  main()
