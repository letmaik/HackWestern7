import os, io
from google.cloud import vision
# from google.cloud.vision import types
import pandas as pd
import json

os.environ['GOOGLE_APPLICATION_CREDENTIALS']= r'../hackwestern7.json'

client = vision.ImageAnnotatorClient()

FILE_NAME = 'rbc-denysHappy.png'
FOLDER_PATH = r'C:\Users\Iyad\Desktop\4th Year\HackWestern\HackWestern7\testImages'


with io.open(os.path.join(FOLDER_PATH, FILE_NAME), 'rb') as image_file:
    content = image_file.read()


image = vision.Image(content=content)
response = client.face_detection(image=image)
# print(reponse.)
# df = pd.DataFrame(columns=['locale','description'])

for face in response.face_annotations:
    joy = vision.Likelihood(face.joy_likelihood)
    anger = vision.Likelihood(face.anger_likelihood)
    sorrow = vision.Likelihood(face.sorrow_likelihood)
    surprise = vision.Likelihood(face.surprise_likelihood)

    vertices = ['(%s,%s)' % (v.x, v.y) for v in face.bounding_poly.vertices]
    print('Happy?:', joy.name)
    print('Angry?:', anger.name)
    print('Sorrow?:', sorrow.name)
    print('Surprised?:', surprise.name)

    print('Face bounds:', ",".join(vertices))