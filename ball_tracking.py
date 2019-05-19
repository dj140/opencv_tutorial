# USAGE
# python ball_tracking.py

# import the necessary packages
from collections import deque
#from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import serial

#连接串口
serial = serial.Serial('COM10',115200,timeout=2)  #连接COM7，波特率位115200
if serial.isOpen():
	print ('串口已打开')
else:
	print ('串口未打开')

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()

ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
greenLower = (29, 86, 6)
greenUpper = (60, 255, 255)
pts = deque(maxlen=args["buffer"])

video = cv2.VideoCapture(0)
video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

uposx = 6660;
uposy = 6660;
while True:
	# grab the current frame
	ret, frame = video.read()
	#print(frame.shape)
	#frame = imutils.resize(frame, width=600)
	#中点（240，320）
	blurred = cv2.GaussianBlur(frame, (51, 51), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, greenLower, greenUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	# find contours in the mask and initialize the current
	# (x, y) center of the ball
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	center = None

	# only proceed if at least one contour was found
	if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)

		posx = int(x)
		posy = int(y)
		posz = int(radius)
		uposx = int(6660+(posx-320-int(radius))*1.125)
		uposy = int(6660+(posy-240-int(radius))*1.5)
		uposz = 6630
		#uposy = str(int(6660+(240-posy-int(radius))*1.5))
		if uposy <= 6650: uposy=6650
		if uposy >= 6900: uposy=6850
		if posz >=100: uposz = 6900
		xy = str(uposx)+str(uposy)+str(uposz)
		#print(uposx+uposy)
		#d=bytes.fromhex(uposx)
		#print(xy)
		serial.write(xy.encode())
		serial.write("\x0d\x0a".encode('utf-8'))
		#print(uposx,uposy)
		#print(int(x),int(y),radius)
		print ('球的位置为x：{}，y: {}'.format(int(x),int(y)))
		print ('半径为:',int(radius))
		M = cv2.moments(c)
		#print(M)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		#print(center)
		# only proceed if the radius meets a minimum size
		if radius > 8:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),
				(0, 255, 255), 2)
			cv2.circle(frame, center, 5, (0, 0, 255), -1)

	# update the points queue
	pts.appendleft(center)

	# loop over the set of tracked points
	for i in range(1, len(pts)):
		# if either of the tracked points are None, ignore
		# them
		if pts[i - 1] is None or pts[i] is None:
			continue

		# otherwise, compute the thickness of the line and
		# draw the connecting lines
		thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
		cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

	# show the frame to our screen
	cv2.imshow("image", frame)
	cv2.imshow("mask", mask)
	cv2.imshow("blurred", blurred)
	cv2.imshow("hsv", hsv)
	key = cv2.waitKey(1) & 0xFF

	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		video.release()
		cv2.destroyAllWindows()
		break