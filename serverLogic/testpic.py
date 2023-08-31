import os ,cv2 
FACE_PATH = "/home/syh/MyProjects/ChatProject/serverLogic/facefolder/"
item = "165-A00check"

import os
if not os.path.exists('/home/syh/MyProjects/ChatProject/serverLogic/haarcascade_frontalface_default.xml'):
    print("Model file not found!")
