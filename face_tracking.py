import numpy as np
import cv2
import serial
# multiple cascades: https://github.com/Itseez/opencv/tree/master/data/haarcascades

#https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_eye.xml
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
#smile_cascade = cv2.CascadeClassifier('haarcascade_smile.xml')
#upperbody_cascade = cv2.CascadeClassifier('haarcascade_upperbody.xml')
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

#连接串口
serial = serial.Serial('/dev/ttyUSB0',115200,timeout=2)  #连接COM7，波特率位115200
if serial.isOpen():
	print ('串口已打开')
else:
	print ('串口未打开')

while 1:
    ret, img = cap.read()
    blurred = cv2.GaussianBlur(img, (11, 11), 0)
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    #smile = smile_cascade.detectMultiScale(gray, 1.3, 11)
    #upperbody = upperbody_cascade.detectMultiScale(gray)
    #for (x,y,w,h) in smile:
    #    cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
    #for (x,y,w,h) in upperbody:
    #    cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),5)
    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,255,0),8)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        cv2.imshow('roi_color',roi_color)
        posx = int(x)
        posy = int(y)
        uposx = int(6660+(posx-320)*1.125)
        uposy = int(6660+(posy-240)*1.5)
        #uposy = str(int(6660+(240-posy-int(radius))*1.5))
        if uposy <= 6700: uposy=6700
        if uposy >= 6900: uposy=6900
        xy = str(uposx)+str(uposy)
        #print(uposx+uposy)
        #d=bytes.fromhex(uposx)
        #print(xy)
        print ('脸的位置为x：{}，y: {}'.format(int(x),int(y)))
        serial.write(xy.encode())
        serial.write("\x0d\x0a".encode('utf-8'))
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex,ey,ew,eh) in eyes:
            cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
            roi_eye = roi_color[ey:ey+eh, ex:ex+ew]
            cv2.imshow('roi_eye',roi_eye)
    cv2.imshow('img',img)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
