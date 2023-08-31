import cv2
import os
from PIL import Image
import torch
import numpy as np

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
      cv2.waitKey(5)
      if (i+1)%10 == 0:
              img_name = "test_{}.jpg".format(int((i-9)/10))
              cv2.imwrite(os.path.join(dataset_path, img_name), frame)
   
    break
  

dataset_path = '/home/syh/MyProjects/ChatProject/serverLogic/facereco/test'

camera = cv2.VideoCapture(0,cv2.CAP_DSHOW)
ret, frame = camera.read()

name = input('请输入姓名:')

# 展示摄像头画面  
CatchUsbVideo("camera", 0)
# 2秒后关闭窗口   
camera.release()
cv2.destroyAllWindows() 








from facenet_pytorch import MTCNN, InceptionResnetV1

# If required, create a face detection pipeline using MTCNN:
#mtcnn = MTCNN(image_size=224*224, margin=10)

# Create an inception resnet (in eval mode):
resnet = InceptionResnetV1(pretrained='vggface2').eval()










train_encode=[]
for i in range(20):
      img = cv2.imread("./face_dataset/{}_{}.jpg".format(name,int(i)))
      face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
      gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
      faces = face_cascade.detectMultiScale(gray)
      if len(faces)==1:
           (x, y, w, h)  = faces[0]
           w += int(w*0.1)
           h += int(h*0.1)
           face = img[y:y+h, x:x+w]
           train_encode.append(face)
      else:
            continue
 
# 检查每个元素的形状
shapes = [item.shape for item in train_encode]
# 确保所有元素具有相同的形状
if len(set(shapes)) > 1:
    # 调整元素的形状为相同的形状
    max_shape = np.max(shapes, axis=0)
    train_encode = [np.resize(item, max_shape) for item in train_encode]

# 将图像数据调整为符合模型期望的形状和类型
img = np.mean(train_encode, axis=0)
img_tensor = torch.from_numpy(img)
# 预处理数据
img_tensor = img_tensor.float() # 转换为float
img_tensor = img_tensor.permute(2, 0, 1) # 调整通道顺序
img_tensor = img_tensor.unsqueeze(0) # 增加batch维度
# Calculate embedding (unsqueeze to add batch dimension)
train_embedding = resnet(img_tensor)
train_embedding = train_embedding.detach().numpy()
print(train_embedding)










#对需要验证的人脸编码
var_encode=[]
for i in range(50):
     img = cv2.imread("./test/test_{}.jpg".format(int(i)))
     face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
     faces = face_cascade.detectMultiScale(gray)
     if len(faces)==1:
           (x, y, w, h)  = faces[0]
           w += int(w*0.1)
           h += int(h*0.1)
           face = img[y:y+h, x:x+w]
           var_encode.append(face)
     else:
            continue

length = len(var_encode)
print(length)
if length<10:
     print ("请勿遮挡面部或侧对摄像头并重新验证")
# 检查每个元素的形状
shapes = [item.shape for item in var_encode]
# 确保所有元素具有相同的形状
if len(set(shapes)) > 1:
    # 调整元素的形状为相同的形状
    max_shape = np.max(shapes, axis=0)
    var_encode = [np.resize(item, max_shape) for item in var_encode]   

var_encoding = []
for _,img in  enumerate(var_encode):
     img_tensor = torch.from_numpy(img)
     # 预处理数据
     img_tensor = img_tensor.float() # 转换为float
     img_tensor = img_tensor.permute(2, 0, 1) # 调整通道顺序
     img_tensor = img_tensor.unsqueeze(0) # 增加batch维度
     # Calculate embedding (unsqueeze to add batch dimension)
     var_embedding = resnet(img_tensor)
     var_embedding = var_embedding.detach().numpy()
     var_encoding.append(var_embedding)

print(var_encoding[0])
print(var_encoding[1])




     
     

similarity = []
count = 0
for i in range(length):
    sim = np.dot(train_embedding, var_encoding[i].T) / (np.linalg.norm(train_embedding) * np.linalg.norm(var_encoding[i]))
    similarity.append(sim)
    if float(sim) > 0.75:
        count += 1
print(similarity)
if count/length > 0.6:
    print("启动！")
else:
    print("未能识别，请重试")

