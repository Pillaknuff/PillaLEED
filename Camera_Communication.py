import cv2 
import numpy as np

class myCamera:
    def __init__(self,com):
        print("connecting to a camera")
        self.cam = cv2.VideoCapture(6)
    def connect(self):
        return False

    
    def getGreyscale(self):
        try:
            result,image = self.cam.read()
            vid_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        except:
            vid_gray = np.random.rand(100,100)
        return vid_gray
    
    def getHighResolution(self,tacq=1):
        try:
            result,image = self.cam.read()
            vid_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            error = False
        except:
            error = True
        return vid_gray, error
