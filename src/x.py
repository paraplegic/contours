#!/usr/bin/env python
 
import cv2
import time

# Start default camera
video = cv2.VideoCapture(2);

def getFrame( stream ):
  rv, frame = stream.read()
  if rv:
    return frame
  return None

def getContours( image ):
  # threshold image
  ret, threshed_img = cv2.threshold(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), 127, 255, cv2.THRESH_BINARY)
  # find contours and get the external one
  contours, hier = cv2.findContours(threshed_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
  return contours


frame = None
while frame is None:
  frame = getFrame( video )

## gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
## contours,hierarchy = cv2.findContours(gray,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
contours = getContours( frame )
idx =0 
for cnt in contours:
    idx += 1
    x,y,w,h = cv2.boundingRect(cnt)
    if w > 20 and w < 300:
      print idx, ") ", x, y, w, h
      ## roi=frame[y:y+h,x:x+w]
      ## cv2.imwrite(str(idx) + '.jpg', roi)
      cv2.rectangle(frame,(x,y),(x+w,y+h),(200,0,0),2)

cv2.imshow('img',frame)
cv2.waitKey(0)   


