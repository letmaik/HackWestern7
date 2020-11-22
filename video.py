import time
import cv2
import numpy as np
import pyvirtualcam
from datetime import *
from easygui import *
from threading import Thread

verbose = False
currentTime = datetime.now()
inbreak = False

def goInBreak(cam):
    global inbreak
    while (inbreak == True):
        image = cv2.imread("bearbreak.jpg", 1)
        output = convertImage(image)
        cam.send(output)
        cam.sleep_until_next_frame()

# Set up webcam capture
vc = cv2.VideoCapture(0) # 0 = default camera

#convert image
def convertImage(img):
      # Read frame from webcam
        image = cv2.resize(img,(640,480))
        # 1) Edges
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        
        # 2) Color
        color = cv2.bilateralFilter(image, 9, 300, 300)

        # convert to RGBA
        out_frame = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)
        out_frame_rgba = np.zeros((height, width, 4), np.uint8)
        out_frame_rgba[:,:,:3] = out_frame
        out_frame_rgba[:,:,3] = 255

        # Send to virtual cam
        return out_frame_rgba

def zoom(cam):
    while True:
        global currentTime
        temp = datetime.now()
        if temp>=currentTime+timedelta(seconds=10):
            currentTime=temp
            #cam.sleep_until_next_frame()
            break

        # Read frame from webcam
        rval, in_frame = vc.read()
        if not rval:
            raise RuntimeError('error fetching frame')

        # 1) Edges
        gray = cv2.cvtColor(in_frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        
        # 2) Color
        color = cv2.bilateralFilter(in_frame, 9, 300, 300)

        # convert to RGBA
        out_frame = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)
        out_frame_rgba = np.zeros((height, width, 4), np.uint8)
        out_frame_rgba[:,:,:3] = out_frame
        out_frame_rgba[:,:,3] = 255

        # Send to virtual cam
        cam.send(out_frame_rgba)

        # Wait until it's time for the next frame
        cam.sleep_until_next_frame()

def outputUser():
    global vc
    # Check if camera opened successfully
    if (vc.isOpened()== False): 
        print("Error opening video stream or file")

    # Read until video is completed
    while(vc.isOpened()):
        # Capture frame-by-frame
        ret, frame = vc.read()
        if ret == True:
            # Display the resulting frame
            cv2.imshow('Frame',frame)

            # Press Q on keyboard to  exit
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows() 
                vc = cv2.VideoCapture(0)
                break

        # Break the loop
        else: 
            cv2.destroyAllWindows() 
            vc = cv2.VideoCapture(0) 
            break

    cv2.destroyAllWindows()      
    vc = cv2.VideoCapture(0)

def shareVideo(cam):
    global vc
    # Check if camera opened successfully
    if (vc.isOpened()== False): 
        print("Error opening video stream or file")

    # Read until video is completed
    while(vc.isOpened()):
        # Capture frame-by-frame
        ret, frame = vc.read()
        if ret == True:
            # # Display the resulting frame
            # cv2.imshow('Frame',frame)
            output = convertImage(frame)
            cam.send(output)
            cam.sleep_until_next_frame()

            # Press Q on keyboard to  exit
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows() 
                vc = cv2.VideoCapture(0)
                break

        # Break the loop
        else: 
            cv2.destroyAllWindows() 
            vc = cv2.VideoCapture(0) 
            break

    cv2.destroyAllWindows()      
    vc = cv2.VideoCapture(0)

if not vc.isOpened():
    raise RuntimeError('could not open video source')

pref_width = 640
pref_height = 480
pref_fps_in = 60
vc.set(cv2.CAP_PROP_FRAME_WIDTH, pref_width)
vc.set(cv2.CAP_PROP_FRAME_HEIGHT, pref_height)
vc.set(cv2.CAP_PROP_FPS, pref_fps_in)

# Query final capture device values (may be different from preferred settings)
width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps_in = vc.get(cv2.CAP_PROP_FPS)
print(f'webcam capture started ({width}x{height} @ {fps_in}fps)')

fps_out = 20
try:
    delay = 0 # low-latency, reduces internal queue size

    with pyvirtualcam.Camera(width, height, fps_out, delay, print_fps=True) as cam:
        print(f'virtual cam started ({width}x{height} @ {fps_out}fps)')

        while True:
            zoom(cam)
            inbreak = True
            thread = Thread(target=goInBreak, args=(cam,))
            thread.start()
            
            theTitle = "Breaktime | Happy Mood"
            choices = ["Do it Myself", "Share", "Not Now"]
            reply = buttonbox(
            theTitle, choices=choices)

            if reply=="Share":     # show a Continue/Cancel dialog
                inbreak=False
                thread.join()
                vc = cv2.VideoCapture('exercises3.mp4')
                shareVideo(cam)
            elif reply=="Not Now":  # user chose Cancel
                inbreak=False
                thread.join()
            elif reply=="Do it Myself":
                vc = cv2.VideoCapture('exercises3.mp4')
                outputUser()
                inbreak=False
                thread.join()
            else: 
                inbreak=False
                thread.join()
finally:
    vc.release()