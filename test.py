import threading
import time

timerVar = True

def printit():
    threading.Timer(6.0, printit).start()
    global timerVar
    print("hi")
    if timerVar==True:
        timerVar=False
    else:
        timerVar=True

threading.Timer(6.0, printit).start()
while(True):
    print(timerVar)