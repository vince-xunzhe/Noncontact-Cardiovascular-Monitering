from time import sleep
from picamera.array import PiRGBArray
from picamera import PiCamera
from PIL import Image
import cv2
import time
import numpy as np
import math
import matplotlib.pyplot as plt

camera = PiCamera()
camera.resolution = (640,480)
camera.framerate = 60
camera.iso = 400
camera.brightness = 70
camera.shutter_speed = 10000 # micro seconds
rawCapture = PiRGBArray(camera,size=(640,480))

def get_mean(vec):
    total=sum(vec)
    mean=math.ceil(total/len(vec))
    return mean

def find_centroid(image,threshold):
    [col,row]=image.shape
    xvect=[]
    yvect=[]
    for i in range(col):
        for j in range(row):
            if (image[i,j] > threshold):
                xvect.append(i)
                yvect.append(j)
    x0=get_mean(xvect)
    y0=get_mean(yvect)
    return x0,y0

def opt_radius(img,hor,ver,Inten):
    I_temper=1
    r=10
    while(1):
        r=r+10
        p=img[(hor-r):(hor+r),(ver-r):(ver+r)]
        I_temper=p.sum()
        if ((I_temper/Inten)>0.8):
            break
    return r

def get_ROI(img):
    [m,n]=img.shape
    I=img.sum()
    a=(np.linspace(1,m,m))
    b=(np.linspace(1,n,n))
    x=a*img
    y=b*(np.transpose(img))
    xs=x.sum()
    ys=y.sum()
    xin=int(xs/I)
    yin=int(ys/I)
    radius=opt_radius(img,xin,yin,I)
    bound=int((radius/2)+10)
    return xin,yin,bound
                

print "[Info] warming up..."
time.sleep(1) # 0.1 by default

cont=0
pixel=[]
print "[Info] recording..."
for frame in camera.capture_continuous(rawCapture,format='bgr',use_video_port=True):
    image = frame.array
    cont=cont+1
    gray_image=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    #former_image=gray_image.copy()

    if cont==1:
        [m,n]=find_centroid(gray_image,30)
        chopped_image=gray_image[(m-159):(m+160),(n-159):(n+160)]
        [x,y,r]=get_ROI(chopped_image)
        x_G=m-160+x
        y_G=n-160+y
        refer=gray_image[(x_G-r+1):(x_G+r),(y_G-r+1):(y_G+r)]
    else:
        current=gray_image[(x_G-r+1):(x_G+r),(y_G-r+1):(y_G+r)]
        f_current=np.float32(current)
        f_refer=np.float32(refer)
        [fa,fb]=cv2.phaseCorrelate(f_current,f_refer)
        px=math.sqrt(math.pow(fa,2)+math.pow(fb,2))
        pixel.append(px)
        refer=current.copy()
        cv2.imshow("Frame",gray_image)
        plt.plot(pixel)
        plt.show()
        

    key=cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)

    if key==ord("q"):
        break
