import cv2

# 加载预训练的人脸检测模型
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# 读取输入图像
img = cv2.imread('./test.jpg')

# 将图片转换为灰度图
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 使用人脸检测模型,检测图片中的人脸
faces = face_cascade.detectMultiScale(gray)

face_imgs = []
for (x, y, w, h) in faces:
    # 构建人脸图片
    w += int(w * 0.1) 
    h += int(h * 0.1)
    face = img[y:y+h, x:x+w]
    face_imgs.append(face)
    
    # 在原图上绘制框
    cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

# 展示原图像
cv2.imshow('img', img)

# 输出保存人脸
for i, face in enumerate(face_imgs):
    cv2.imwrite(f'face{i}.jpg', face)

cv2.waitKey()