import time
import cv2.cv2 as cv2
import numpy as np
import pyvirtualcam

verbose = False

# Set up webcam capture
vc = cv2.VideoCapture(0) # 0 = default camera

if not vc.isOpened():
    raise RuntimeError('could not open video source')

pref_width = 960
pref_height = 720
pref_fps_in = 30
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

finally:
    vc.release()
    