import cv2 

class myCamera:
    def __init__(self,com):
        print("connecting to a camera")
        self.cam = cv2.VideoCapture(0)
    def connect(self):
        return False

    
    def getGreyscale(self):
        result,image = self.cam.read()
        vid_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return vid_gray
    
    def getHighResolution(self,tacq=1):
        try:
            result,image = self.cam.read()
            vid_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            error = False
        except:
            error = True
        return vid_gray, error
