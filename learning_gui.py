import sys
import os
import glob
import cv2
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import threading

from PySide2 import QtWidgets

streaming_url = ""

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 로고 이미지 사용
        pixmap = QPixmap('res/logo.png')
        logo = QLabel()
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignHCenter)

        # [기능]
        # 버튼
        learn_data_add_btn = QPushButton('학습 데이터 추가', self)
        transmission_btn = QPushButton('영상 출력 설정', self)

        # 버튼 클릭
        transmission_btn.clicked.connect(self.openTransmissionClass)
        learn_data_add_btn.clicked.connect(self.openAddFaceDataClass)
        # [디자인]
        # 레이아웃
        vbox = QVBoxLayout()
        vbox.addStretch(3)
        vbox.addWidget(logo)
        vbox.addStretch(1)
        vbox.addWidget(learn_data_add_btn)
        vbox.addWidget(transmission_btn)
        vbox.addStretch(3)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def openTransmissionClass(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def openAddFaceDataClass(self):
        widget.setCurrentIndex(widget.currentIndex() + 4)

class TransmissionWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 로고 이미지 사용
        pixmap = QPixmap('res/logo.png')
        logo = QLabel()
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignHCenter)

        # [기능]
        # 버튼
        streaming_btn = QPushButton('스트리밍', self)
        virtual_cam_btn = QPushButton('가상 카메라', self)
        before_btn = QPushButton('뒤로가기', self)

        # 버튼 클릭
        streaming_btn.clicked.connect(self.openStreamingClass)
        before_btn.clicked.connect(self.openMainClass)

        # [디자인]
        # 레이아웃
        vbox = QVBoxLayout()
        vbox.addStretch(3)
        vbox.addWidget(logo)
        vbox.addStretch(1)
        vbox.addWidget(streaming_btn)
        vbox.addWidget(virtual_cam_btn)
        vbox.addWidget(before_btn)
        vbox.addStretch(3)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def openMainClass(self):
        widget.setCurrentIndex(widget.currentIndex() - 1)

    def openStreamingClass(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)


class StreamingWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 로고 이미지 사용
        pixmap = QPixmap('res/logo.png')
        logo = QLabel()
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignHCenter)

        # [기능]
        # 버튼
        server_label = QLabel("서버 주소")
        self.server_url = QLineEdit()
        key_label = QLabel("스트림 키")
        self.stream_key = QLineEdit()
        self.stream_key.setEchoMode(3)
        before_btn = QPushButton('뒤로가기', self)
        input_btn = QPushButton('확인', self)

        # 버튼 클릭
        before_btn.clicked.connect(self.openMainClass)
        input_btn.clicked.connect(self.getURL)

        # [디자인]
        # 레이아웃
        server_input_hbox = QHBoxLayout()
        server_input_hbox.addWidget(server_label)
        server_input_hbox.addWidget(self.server_url)

        key_input_hbox = QHBoxLayout()
        key_input_hbox.addWidget(key_label)
        key_input_hbox.addWidget(self.stream_key)

        btn_hbox = QHBoxLayout()
        btn_hbox.addWidget(before_btn)
        btn_hbox.addWidget(input_btn)

        vbox = QVBoxLayout()
        vbox.addStretch(3)
        vbox.addWidget(logo)
        vbox.addStretch(1)
        vbox.addLayout(server_input_hbox)
        vbox.addLayout(key_input_hbox)
        vbox.addStretch(1)
        vbox.addLayout(btn_hbox)
        vbox.addStretch(2)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def openMainClass(self):
        widget.setCurrentIndex(widget.currentIndex() - 1)

    def getURL(self):
        streaming_url = self.server_url.text() + "/" + self.stream_key.text()
        widget.setCurrentIndex(widget.currentIndex() + 1)


class BroadWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 로고 이미지 사용
        pixmap = QPixmap('res/logo.png')
        logo = QLabel()
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignHCenter)
        # [기능]
        # 버튼
        streaming_btn = QPushButton('마스킹 중지', self)
        virtual_cam_btn = QPushButton('방송 중단', self)
        before_btn = QPushButton('메인화면', self)

        # 버튼 클릭
        streaming_btn.clicked.connect(self.openStreamingClass)
        before_btn.clicked.connect(self.openMainClass)

        # [디자인]
        # 레이아웃
        vbox = QVBoxLayout()
        vbox.addStretch(3)
        vbox.addWidget(logo)
        vbox.addStretch(1)
        vbox.addWidget(streaming_btn)
        vbox.addWidget(virtual_cam_btn)
        vbox.addWidget(before_btn)
        vbox.addStretch(3)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def openMainClass(self):
        widget.setCurrentIndex(widget.currentIndex() - 3)

    def openStreamingClass(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)


class AddFaceData(QWidget):
        # VideoSignal = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self.running = False
        self.initUI(self.running)
        # th = threading.Thread(target=fc.onlyForRecode())
        # th.start()
        print("init은 실행됨")

    def initUI(self, running):
        alert_text = QLabel('학습 데이터 추가 중', self)
        alert_text.setAlignment(Qt.AlignCenter)

        self.win = QWidget()
        self.flabel = QLabel()
        self.total_number = QLabel()
        before_btn = QPushButton('학습 종료', self)
        before_btn.clicked.connect(self.openMainClass)
        btn_start = QPushButton("Camera On", self)
        print("여기는 initUI 러닝")
        print(self.running)

        btn_start.clicked.connect(self.start)

        # [디자인]
        # 레이아웃
        vbox = QVBoxLayout()
        vbox.addStretch(0)
        vbox.addWidget(alert_text)
        ### 여기다 비디오창 넣어야 할듯?
        print("UI쪽도 실행됨")
        vbox.addWidget(self.flabel)
        vbox.addWidget(self.total_number)
        vbox.addWidget(btn_start)
        vbox.addWidget(before_btn)
        vbox.addStretch(3)
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)

        self.setLayout(hbox)
        self.win.setLayout(vbox)

    def test(self):
        print(self.running)
        print("실행이 자동으로 됩니다.")

    def openMainClass(self):
        widget.setCurrentIndex(widget.currentIndex() - 4)

    def stop(self):
        self.running = False
        print("stoped..")

    def start(self):
        self.running = True
        th = threading.Thread(target=self.onlyForRecode)
        print("쓰레드 지정까지 됨")
        th.start()
        print("쓰레드 started..")

    def onExit(self):
        print("exit")
        self.stop(self)

    def run(self):
        cap = cv2.VideoCapture(0)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.flabel.resize(width, height)
        print("while도 됨")
        print(self.running)
        while self.running:
            ret, img = cap.read()
            if ret:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                h,w,c = img.shape
                qImg = QImage(img.data, w, h, w*c, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qImg)
                self.label.setPixmap(pixmap)
            else:
                break
        cap.release()

    def onlyForRecode(self):
        total_picture = 0
        cap = cv2.VideoCapture(0)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.flabel.resize(width, height)

        # if not cap.isOpened():
        #     print('Camera open failed!')
        #     sys.exit()
        # Network
        model = 'res10_300x300_ssd_iter_140000_fp16.caffemodel'
        config = 'deploy.prototxt'
        net = cv2.dnn.readNet(model, config)

        # if net.empty():
        #     print('Net open failed!')
        #     sys.exit()

        # Output Directory & File Index
        outdir = 'train_images/User1'
        prefix = outdir + '/face_'
        file_idx = 1

        # try:
        #     if not os.path.exists(outdir):
        #         os.makedirs(outdir)
        # except OSError:
        #     print('output folder create failed!')

        png_list = glob.glob(prefix + '*.png')
        if len(png_list) > 0:
            png_list.sort()
            last_file = png_list[-1]
            file_idx = int(last_file[-8:-4]) + 1

        # Read Frames
        cnt = 0
        while self.running:
            _, frame = cap.read()
            if frame is None:
                break
            # Face Detection
            blob = cv2.dnn.blobFromImage(frame, 1, (300, 300), (104, 177, 123))
            net.setInput(blob)
            detect = net.forward()
            detect = detect[0, 0, :, :]
            (h, w) = frame.shape[:2]

            for i in range(detect.shape[0]):
                confidence = detect[i, 2]
                if confidence < 0.8:
                    break
                # Face found!
                x1 = int(detect[i, 3] * w)
                y1 = int(detect[i, 4] * h)
                x2 = int(detect[i, 5] * w)
                y2 = int(detect[i, 6] * h)
                # Save face image as a png file
                cnt += 1
                if cnt % 10 == 0:
                    filename = '{0}{1:04d}.png'.format(prefix, file_idx)
                    self.save_face(frame, (x1, y1), (x2, y2), filename)
                    file_idx += 1
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, c = frame.shape
                frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0))
                label = 'Face: %4.3f' % confidence
                frame = cv2.putText(frame, label, (x1, y1 - 1),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
                qImg = QImage(frame.data, w, h, w * c, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qImg)
                self.flabel.setPixmap(pixmap)

        cv2.destroyAllWindows()

    def save_face(self, frame, p1, p2, filename):
        cp = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
        print("저장프로세스 작동중")
        w = p2[0] - p1[0]
        h = p2[1] - p1[1]

        if h * 3 > w * 4:
            w = round(h * 3 / 4)
        else:
            h = round(w * 4 / 3)

        x1 = cp[0] - w // 2
        y1 = cp[1] - h // 2
        if x1 < 0 and y1 < 0:
            return
        if x1 + w >= frame.shape[1] or y1 + h >= frame.shape[0]:
            return

        crop = frame[y1:y1 + h, x1:x1 + w]
        try:
            crop = cv2.resize(crop, dsize=(150, 200), interpolation=cv2.INTER_CUBIC)
        except Exception as e:
            print(str(e))
        try:
            cv2.imwrite(filename, crop)
        except Exception as e:
            print(str(e))
        self.total_number.repaint()

if __name__ == '__main__':
    def center(widget):
        qr = widget.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        widget.move(qr.topLeft())

    #이 부분은 필수
    app = QApplication(sys.argv)

    widget = QStackedWidget()

    # [디자인]
    # 창 제목 및 아이콘 적용
    widget.setWindowTitle('SecuLive')
    widget.setWindowIcon(QIcon('res/live.png'))

    # 로고 이미지 사용
    pixmap = QPixmap('res/logo.png')
    logo = QLabel()
    logo.setPixmap(pixmap)
    logo.setAlignment(Qt.AlignHCenter)

    # 폰트 설정
    fontDB = QFontDatabase()
    fontDB.addApplicationFont('res/SCDream5.otf')
    app.setFont(QFont('에스코어 드림 5 Medium'))

    mainWindow = MainWindow()
    transmissionWindow = TransmissionWindow()
    streamingWindow = StreamingWindow()
    broadWindow = BroadWindow()
    addFaceData = AddFaceData()

    widget.addWidget(mainWindow)
    widget.addWidget(transmissionWindow)
    widget.addWidget(streamingWindow)
    widget.addWidget(broadWindow)
    widget.addWidget(addFaceData)

    # [윈도우 정보]
    #widget.resize(640, 480)
    widget.resize(1280, 720)
    center(widget)
    widget.show()

    sys.exit(app.exec_())