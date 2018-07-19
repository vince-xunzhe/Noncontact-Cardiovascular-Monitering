import io
import time
import threading
import picamera
import cv2
import picamera.array
import numpy as np


# Create a pool of image processors
done = False
lock = threading.Lock()
pool = []

class ImageProcessor(threading.Thread):
    def __init__(self):
        super(ImageProcessor, self).__init__()
        self.stream = io.BytesIO()
        self.event = threading.Event()
        self.terminated = False
        self.start()

    def run(self):
        # This method runs in a separate thread
        global frames
        global start
        global done
        global grayback
        while not self.terminated:
            # Wait for an image to be written to the stream
            if self.event.wait(1):
                try:
                    minpixel=1
                    self.stream.seek(0)
                    frames+=1
                    currentframe=frames ## Because frame can be incremented by other threads while proccesing

                    # Read the image and do some processing on it
                    # Construct a numpy array from the stream
                    data = np.fromstring(self.stream.getvalue(), dtype=np.uint8)
                    # "Decode" the image from the array, preserving colour
                    image = cv2.imdecode(data, 1)

                    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
                    #cv2.imwrite('fullimage'+str(currentframe)+".png",image)
                    d = cv2.absdiff(gray,grayback)
                    
                    # Gaussian blur works better but it is too slow
                    # d= cv2.GaussianBlur(d,(55,55),0) 

                    d= cv2.blur(d,(55,55))
                    # cv2.imwrite('fullimage'+str(currentframe)+"_blurnormal_55.png",d)

                    # I've tried different thresholding procedures, but the best results are with a simple binary threshold
                    #                    ret, thresh = cv2.threshold(d,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

                    ret, thresh = cv2.threshold(d,5,255,cv2.THRESH_BINARY)
                    # cv2.imwrite('fullimage'+str(currentframe)+"_thres_bin_5.png",thresh)

                    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
                    # cv2.drawContours(image, contours, -1, (0,255,0), 3)
                    # cv2.imwrite('fullimage'+str(currentframe)+"_contour.png",image)

                    for i,cnt in enumerate(contours):
                        x,y,w,h = cv2.boundingRect(cnt)
                        if (w>minpixel | h>minpixel):
                            cv2.imwrite('image_'+str(currentframe)+"_"+str(i)+'.png',image[y:(y+h),x:(x+w)])
                            print("Wrote an image "+str(currentframe)+"_"+str(i))

                    finish = time.time()
                    print('Captured %d frames at %.2ffps' % (
                            currentframe,
                            currentframe / (finish - start)))
                    #...
                    #...
                    # Set done to True if you want the script to terminate
                    # at some point
                    #done=True
                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()
                    # Return ourselves to the pool
                    with lock:
                        pool.append(self)

def streams():
    while not done:
        with lock:
            if pool:
                processor = pool.pop()
            else:
                processor = None
        if processor:
            yield processor.stream
            processor.event.set()
        else:
            # When the pool is starved, wait a while for it to refill
            print ("Waiting")            
            time.sleep(0.1)

with picamera.PiCamera() as camera:
    pool = [ImageProcessor() for i in range(4)]

    print ("Starting fixed settings setup")
    camera.resolution = (1280, 720)
    camera.framerate = 30
    # Wait for analog gain to settle on a higher value than 1
    while camera.analog_gain <= 1:
        time.sleep(0.1)

    print ("Fixing the values")
    # Now fix the values
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = g

    camera.start_preview()
    time.sleep(2)
    backstream = io.BytesIO()
    camera.capture(backstream,format='jpeg', use_video_port=True)
    databack = np.fromstring(backstream.getvalue(), dtype=np.uint8)
    # "Decode" the image from the array, preserving colour
    background = cv2.imdecode(databack, 1)
    grayback = cv2.cvtColor(background,cv2.COLOR_BGR2GRAY)
    cv2.imwrite('background'+".png",background)

    start = time.time()
    frames=0
    camera.capture_sequence(streams(), use_video_port=True)

# Shut down the processors in an orderly fashion
while pool:
    with lock:
        processor = pool.pop()
    processor.terminated = True
    processor.join()
