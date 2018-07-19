from time import sleep
from picamera.array import PiRGBArray
from picamera import PiCamera
from PIL import Image
import io
import picamera
import cv2
import time
import threading
import numpy as np
import math
import matplotlib.pyplot as plt

pixel=[]

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
    bound=int((radius/2))
    return xin,yin,bound

class ImageProcessor(threading.Thread):
    def __init__(self, owner):
        super(ImageProcessor, self).__init__()
        self.stream = io.BytesIO()
        self.event = threading.Event()
        self.terminated = False
        self.owner = owner
        self.start()

    def run(self):
        # This method runs in a separate thread
        global px
        global f_refer
        global pixel
        while not self.terminated:
            # Wait for an image to be written to the stream
            if self.event.wait(1):
                try:
                    self.stream.seek(0)
                    # Read the image and do some processing on it
                    #Image.open(self.stream)
                    #frame=self.stream.array
                    data = np.fromstring(self.stream.getvalue(), dtype=np.uint8)
                    frame=cv2.imdecode(data,1)
                    
                    gray_image=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                    
                    [M,N]=find_centroid(gray_image,75)
                    chopped_image = gray_image[(M-159):(M+160),(N-159):(N+160)]
                    [x,y,r]=get_ROI(chopped_image)
                    
                    x_G=M-160+x
                    y_G=N-160+y
                    current=gray_image[(x_G-r+1):(x_G+r),(y_G-r+1):(y_G+r)]
                    
                    f_current=np.float32(current)
                    f_refer=f_current
                    [fa,fb]=cv2.phaseCorrelate(f_current,f_refer)
                    px=math.sqrt(math.pow(fa,2)+math.pow(fb,2))

                    if px>2:
                        pixel.append(px)
                    else:
                        pixel.append(0)

                    plt.plot(pixel)
                  
                    
                    #...
                    # Set done to True if you want the script to terminate
                    # at some point
                    #self.owner.done=True
                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()
                    # Return ourselves to the available pool
                    with self.owner.lock:
                        self.owner.pool.append(self)

class ProcessOutput(object):
    def __init__(self):
        self.done = False
        # Construct a pool of 4 image processors along with a lock
        # to control access between threads
        self.lock = threading.Lock()
        self.pool = [ImageProcessor(self) for i in range(4)]
        self.processor = None

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame; set the current processor going and grab
            # a spare one
            if self.processor:
                self.processor.event.set()
            with self.lock:
                if self.pool:
                    self.processor = self.pool.pop()
                else:
                    # No processor's available, we'll have to skip
                    # this frame; you may want to print a warning
                    # here to see whether you hit this case
                    self.processor = None
        if self.processor:
            self.processor.stream.write(buf)

    def flush(self):
        # When told to flush (this indicates end of recording), shut
        # down in an orderly fashion. First, add the current processor
        # back to the pool
        if self.processor:
            with self.lock:
                self.pool.append(self.processor)
                self.processor = None
        # Now, empty the pool, joining each thread as we go
        while True:
            with self.lock:
                try:
                    proc = self.pool.pop()
                except IndexError:
                    pass # pool is empty
            proc.terminated = True
            proc.join()

with picamera.PiCamera() as camera:
    plt.show()
    camera.resolution=(1280,720)
    camera.framerate=30
    camera.iso = 400
    camera.brightness = 20
    camera.shutter_speed = 10000 # micro seconds
    camera.start_preview()
    time.sleep(2)
    output = ProcessOutput()
    camera.start_recording(output, format='mjpeg')
    while not output.done:
        camera.wait_recording(1)
    camera.stop_recording()
