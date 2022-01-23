import sys
import cv2
import time
prevTime = 0
#카페모델을 위한 model, config 세팅
model = 'res10_300x300_ssd_iter_140000_fp16.caffemodel'
config = 'deploy.prototxt'
#model = 'opencv_face_detector_uint8.pb'
#config = 'opencv_face_detector.pbtxt'
net = cv2.dnn.readNet(model, config)


cap = cv2.VideoCapture('iu.mp4')
#cap = cv2.VideoCapture('godok.mp4')
#cap = cv2.VideoWriter('')
#cap = cv2.VideoCapture(0)



# 이 부분은 카메라 오픈이 안 될경우를 위한 함수
# if not cap.isOpened():
#     print('Camera open failed!')
#     sys.exit()

net = cv2.dnn.readNet(model, config)

if net.empty():
    print('Net open failed!')
    sys.exit()

while True:
    ret, frame = cap.read()

    if not ret:
        break

    blob = cv2.dnn.blobFromImage(frame, 1, (300, 300), (104, 177, 123))
    net.setInput(blob)
    out = net.forward()
    ##########################################
    #이하는 실시간 fps 출력
    curTime = time.time()
    sec = curTime - prevTime
    prevTime = curTime
    fps = 1 / (sec)
    str = "FPS : %0.1f" % fps
    cv2.putText(frame, str, (0, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0))
    ###########################################
    detect = out[0, 0, :, :]
    (h, w) = frame.shape[:2]

    for i in range(detect.shape[0]):
        confidence = detect[i, 2]
        if confidence < 0.5:
            break

        x1 = int(detect[i, 3] * w)
        y1 = int(detect[i, 4] * h)
        x2 = int(detect[i, 5] * w)
        y2 = int(detect[i, 6] * h)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0))

        label = f'Face: {confidence:4.2f}'
        cv2.putText(frame, label, (x1, y1 - 1), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()




# 사진 얼굴 인증 코드 잔재
# import sys
# import cv2
# img = cv2.imread('iu.jpg')
# if img is None:
#     print('Image load failed!')
#     sys.exit()
# cv2.namedWindow('image')
# x=160; y=150; w=600; h=750
# roi = img[y:y+h, x:x+w]
# dst = cv2.blur(roi, (50, 50))
# img[y:y+h, x:x+w] = dst
# # print(roi.shape)
# cv2.imshow('image', img)
# cv2.waitKey()
# cv2.destroyAllWindows()
#
