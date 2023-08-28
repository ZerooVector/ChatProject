import cv2
import os

def CatchUsbVideo(window_name, camera_idx):
  face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

  cap = cv2.VideoCapture(camera_idx)

  while cap.isOpened():

    # 截取保存这一帧
    for i in range(500):
      # 持续读取新帧
      ret, frame = cap.read()
      # 显示新帧 
      cv2.imshow(window_name, frame)
      cv2.waitKey(10)
      if (i+1)%25 == 0:
              img_name = "{}_{}.jpg".format(name,int((i-24)/25))
              cv2.imwrite(os.path.join(dataset_path, img_name), frame)
   
    break
    
          
dataset_path = './face_dataset'
 
if not os.path.exists(dataset_path):
    os.mkdir(dataset_path)

camera = cv2.VideoCapture(0,cv2.CAP_DSHOW)
ret, frame = camera.read()

name = input('请输入姓名:')

# 展示摄像头画面  
CatchUsbVideo("camera", 0)
# 5秒后关闭窗口   
camera.release()
cv2.destroyAllWindows() 
print("已成功收集 {} 的人脸样本信息!".format(name))