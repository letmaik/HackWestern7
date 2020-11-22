import os, io
from google.cloud import vision
import cv2
import numpy as np
import pyvirtualcam

# Loading Google credentials as an environment variable
# NOTE: This will be different for macOS
os.environ['GOOGLE_APPLICATION_CREDENTIALS']= r'../hackwestern7.json'
# Loading Google cloud Vision Client
client = vision.ImageAnnotatorClient()

# ----------------
# Starting virtual webcam setup
verbose = False

# Set up webcam capture
vc = cv2.VideoCapture(0) # 0 = default camera

if not vc.isOpened():
    raise RuntimeError('could not open video source')

pref_width = 1280
pref_height = 720
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

likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE', 'LIKELY', 'VERY_LIKELY')

def emotionaloutput(face):

    # print('anger: {}'.format(likelihood_name[face.anger_likelihood]))
    # print(likelihood_name[face.anger_likelihood])

    if likelihood_name[face.anger_likelihood] != 'VERY_UNLIKELY' \
            or likelihood_name[face.sorrow_likelihood] != 'VERY_UNLIKELY':
        print("GRRRR ANGRY")

def checkPosture(pos, start):
    x = pos[0][0]
    y = pos[0][1]
    w = pos[0][2]
    h = pos[0][3]
    if abs(x - start[0][0]) > 50 or abs(y - start[0][1]) > 50 or abs(w - start[0][2]) > 50:
        print("FIX YO POSSTUUUUREEEE")
        # REPLACE with popup

try:
    delay = 0  # low-latency, reduces internal queue size
    i = 0 # i = frame counter ONLY used for snapshot

    with pyvirtualcam.Camera(width, height, fps_out, delay, print_fps=True) as cam:
        print(f'virtual cam started ({width}x{height} @ {fps_out}fps)')

        # Initiliazing posture
        rval, in_frame = vc.read()
        if not rval:
            raise RuntimeError('error fetching frame')
        gray = cv2.cvtColor(in_frame, cv2.COLOR_BGR2GRAY)
        color = cv2.cvtColor(in_frame, cv2.COLOR_BGR2RGB)
        # data/haarcascade/
        haar_cascade_face = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        # array of face positions (2d array). First is number of arrays, then inner is x, y, w, h
        startingFacePos = haar_cascade_face.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5);

        print(startingFacePos)

        # print('Faces found: ', len(startingFacePos))

        # Inside infinite loop for webcam
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
            out_frame_rgba[:, :, :3] = out_frame
            out_frame_rgba[:, :, 3] = 255

            # Send to virtual cam
            cam.send(out_frame_rgba)

            # Check Posture:
            pos = haar_cascade_face.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
            # print(pos)
            if(len(startingFacePos)>0 and len(pos)>0):
                checkPosture(pos, startingFacePos)

            # Intermittently select frames to capture and send to GCP
            # Does so once every 300 frames, in a regular application this could be once every 12 seconds

            if i % 300 == 0:  # if i is divisible by 300 then we are at the 300th frame
                # Saving frame then using it - SUPER HACKY. NOTE: FIX IF FASTER OPTION
                file = 'live.png'
                cv2.imwrite(file, in_frame)

                cam.send(out_frame_rgba)

                with io.open(file, 'rb') as image_file:
                    content = image_file.read()

                # Reducing gray screen length, sending out the same frame before. it may look like it's freezing.
                cam.send(out_frame_rgba)

                # Setup + Sending GCP request
                image = vision.Image(content=content)  # Sending regit quest
                cam.send(out_frame_rgba)
                response = client.face_detection(image=image)  # Saving response, extracting only face detection

                # Reducing gray screen length, sending out the same frame before. it may look like it's freezing.
                cam.send(out_frame_rgba)

                # NOTE: FOR NOW only, we are printing the content. Later this will be passed on to do something
                for face in response.face_annotations:
                    emotionaloutput(face)
                    cam.send(out_frame_rgba)
            else:
                # Wait until it's time for the next frame - we exclude this from above to avoid delays
                cam.sleep_until_next_frame()
            i += 1
finally:
    vc.release()