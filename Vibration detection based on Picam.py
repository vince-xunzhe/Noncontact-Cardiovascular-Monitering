from time import sleep
from picamera.array import PiRGBArray
from picamera import PiCamera
from PIL import Image
import cv2
import time
import numpy as np
import math
import matplotlib.pyplot as plt
from math import ceil
from .. utils import logger, verbose


# initializing the camera optical configurations
camera = PiCamera()
camera.resolution = (1296,730)
camera.framerate = 49
camera.iso = 400
camera.brightness = 30
camera.shutter_speed = 10000
rawCapture = PiRGBArray(camera,size=(1296,730))

def focus(image):
    bound=200
    [hor,ver]=image.shape
    seg=np.zeros((hor,ver))
    threshold=0.5*image.max()
    
    ivec=[]
    jvec=[]
    
    for i in range(hor):
        for j in range(ver):
            if (image[i,j] > threshold):
                ivec.append(i)
                jvec.append(j)
                
    ipos=math.ceil(np.mean(ivec))
    jpos=math.ceil(np.mean(jvec))
    
    data=image[(ipos-bound+1):(ipos+bound),(jpos-bound+1):(jpos+bound)]
    
    [hor,ver]=data.shape
    
    I=data.sum()
    
    a=(np.linspace(1,hor,hor))
    b=(np.linspace(1,ver,ver))
    
    ix=math.ceil(((a*data).sum())/I)
    iy=math.ceil(((b*(np.transpose(data))).sum())/I)
    I_av=1
    r=10
    
    while(1):
        r=r+3
        I_av=(data[(ix-r):(ix+r),(iy-r):(iy+r)]).sum()
        if (I_av/I>0.8):
            break
            
    x=math.ceil(ipos-bound+ix)
    y=math.ceil(jpos-bound+iy)
    r=math.ceil(r/2+10)
    
    return x,y,r


def peak_finder(x0, thresh=None, extrema=1, verbose=None):
    x0 = np.asanyarray(x0)

    if x0.ndim >= 2:
        raise ValueError('One-dimentional signals required.')

    s = x0.size

    if thresh is None:
        thresh = (np.max(x0) - np.min(x0)) / 4

    assert extrema in [-1, 1]

    if extrema == -1:
        x0 = extrema * x0

    dx0 = np.diff(x0)
    dx0[dx0 == 0] = -np.finfo(float).eps
    ind = np.where(dx0[:-1:] * dx0[1::] < 0)[0] + 1
    x = np.concatenate((x0[:1], x0[ind], x0[-1:]))
    ind = np.concatenate(([0], ind, [s - 1]))

    length = x.size
    min_mag = np.min(x)

    if length > 2:
        temp_mag = min_mag
        found_peak = False
        left_min = min_mag
        signDx = np.sign(np.diff(x[:3]))

        if signDx[0] <= 0:
            ii = -1

            if signDx[0] == signDx[1]:
                x = np.concatenate((x[:1], x[2:]))
                ind = np.concatenate((ind[:1], ind[2:]))
                length -= 1

        else:
            ii = 0
            if signDx[0] == signDx[1]:
                x = x[1:]
                ind = ind[1:]
                length -= 1

        maxPeaks = int(ceil(length / 2.0))
        peak_loc = np.zeros(maxPeaks, dtype=np.int)
        peak_mag = np.zeros(maxPeaks)
        c_ind = 0

        while ii < (length - 1):
            ii += 1

            if found_peak and ((x[ii] > peak_mag[-1]) or
                                   (left_min < peak_mag[-1] - thresh)):
                temp_mag = min_mag
                found_peak = False

            if ii == length - 1:
                break

            if (x[ii] > temp_mag) and (x[ii] > left_min + thresh):
                temp_loc = ii
                temp_mag = x[ii]

            ii += 1

            if not found_peak and (temp_mag > (thresh + x[ii])):
                found_peak = True
                left_min = x[ii]
                peak_loc[c_ind] = temp_loc
                peak_mag[c_ind] = temp_mag
                c_ind += 1
            elif x[ii] < left_min:
                left_min = x[ii]

        if (x[-1] > temp_mag) and (x[-1] > (left_min + thresh)):
            peak_loc[c_ind] = length - 1
            peak_mag[c_ind] = x[-1]
            c_ind += 1

        elif not found_peak and temp_mag > min_mag:
            peak_loc[c_ind] = temp_loc
            peak_mag[c_ind] = temp_mag
            c_ind += 1

        peak_inds = ind[peak_loc[:c_ind]]
        peak_mags = peak_mag[:c_ind]
    else:
        x_ind = np.argmax(x)
        peak_mags = x[x_ind]
        if peak_mags > (min_mag + thresh):
            peak_inds = ind[x_ind]
        else:
            peak_mags = []
            peak_inds = []

    if extrema < 0:
        peak_mags *= -1.0
        x0 = -x0

    if len(peak_inds) == 0:
        logger.info('No peaks detected')

    return peak_inds, peak_mags

print "[Info] warming up..."
time.sleep(5) # 0.1 by default

cont=0
pixel=[]

print "[Info] recording..."
for frame in camera.capture_continuous(rawCapture,format='bgr',use_video_port=True):

    image = frame.array
    cont=cont+1
    gray_image=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

    if cont==1:
        [m,n,r]=focus(gray_image)
        print m,n,r
        refer=gray_image[(m-r+1):(m+r),(n-r+1):(n+r)]
    else:
        current=gray_image[(m-r+1):(m+r),(n-r+1):(n+r)]
        f_current=np.float32(current)
        f_refer=np.float32(refer)
        [fa,fb]=cv2.phaseCorrelate(f_current,f_refer)
        px=math.sqrt(math.pow(fa,2)+math.pow(fb,2))
        pixel.append(px)
        refer=current.copy()
        cv2.imshow("Frame",current)
        print current

    print cont

    key=cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)

    if (cont==300):
        break

plt.plot(pixel)
plt.show()

[idx_all, val_all]=peak_finder(pixel, 1)
[idx_SBP, val_SBP]=peak_finder(pixel, 30)
length_all=len(idx_all)
length_SBP=len(idx_SBP)
gaps=[]

for xx in range(1,length_all):
    if xx<(length_all-1):
        gaps=[gaps,idx_SBP(xx+1)-idx_SBP(xx)]

idx_AUG=[]
val_AUG=[]

for i in range(1,length_SBP):
    for j in range(1,length_all):
        if idx_SBP==idx_all:
            idx_AUG=[idx_AUG,idx_all(j+1)]
            val_AUG=[val_AUG,val_all(j+1)]
length_AUG=len(idx_AUG)

m_gap=math.ceil(0.3*np.mean(gaps)/2)
idx_Bottom=[]
val_Bottom=[]

for i in range (1,length_SBP):
    if idx_SBP(i)-m_gap<0:
        vect=pixel[1:idx_SBP(i)]
    else:
        vect=pixel[(idx_SBP(i)-m_gap):idx_SBP(i)]
    ver=min(vect)
    hor=p=list.index(value)
    val_Bottom=[val_Bottom,ver]
    idx_Bottom=[idx_Bottom,idx_SBP(i)-m_gap+hor]

length_Bottom=len(idx_Bottom)
Pulse_Rate=ceil((length_SBP/6)*60)
Augmentation=(val_SBP-val_AUG)/(val_SBP-val_Bottom)
Aug=[]

for i in range(1, len(Augmentation)-2):
    a=np.mean(Augmentation(i),Augmentation(i+1),Augmentation(i+3))
    Aug=[Aug,a]

Augmentation_Index=np.mean(Aug)