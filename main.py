# [라이브러리]
import cv2
import time
import os
import glob

# PyQt5
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

# obs 가상 카메라
import pyvirtualcam

# ffmpeg 명령어 실행 및 pipe 사용
import subprocess as sp
import threading

# DB
import sqlite3

# DB init
con = sqlite3.connect('user.db')
cur = con.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
temp_patch = 0

# USER_INFO 라는 테이블이 존재하지 않을 경우 생성하도록 설정
for row in cur:
    if row[0] == "USER_INFO":
        temp_patch += 1
if temp_patch != 1:
    try:
        cur.execute(
            "CREATE TABLE USER_INFO(`USER_NO` INTeger PRIMARY KEY AUTOINCREMENT , `USER_ID`     VARCHAR(150)     NULL        , `USER_PW`     VARCHAR(150)     NULL        , `USER_NAME`      VARCHAR(150)     NULL        , `MODEL_LOCATION`     VARCHAR(30)      NULL        , `TRY_COUNT`  INT UNSIGNED    NOT NULL )")
        con.commit()
    except Exception as e:
        tmp_e = str(e)
        if tmp_e == 'table USER_INFO already exists':
            cur.execute("DROP TABLE USER_INFO")
            cur.execute(
                "CREATE TABLE USER_INFO(`USER_NO` INTeger PRIMARY KEY AUTOINCREMENT , `USER_ID`     VARCHAR(150)     NULL        , `USER_PW`     VARCHAR(150)     NULL        , `USER_NAME`      VARCHAR(150)     NULL        , `MODEL_LOCATION`     VARCHAR(30)      NULL        , `TRY_COUNT`  INT UNSIGNED    NOT NULL )")
            con.commit()
con.close()

session = ""

# [코드]
# 0. 내장 카메라 및 오디오 선택
camera = cv2.VideoCapture(0)
audio = "마이크(USB Microphone)"

# 1. 내장 카메라 정보 저장 (fps, width, height)
fps = int(camera.get(cv2.CAP_PROP_FPS))
width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 2. 스트리밍 주소
streaming_url = ""

class LoginWindow(QWidget):

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
        self.id_data_add = QLineEdit()
        self.id_data_add.setPlaceholderText("아이디")
        self.pw_data_add = QLineEdit()
        self.pw_data_add.setEchoMode(QLineEdit.Password)
        self.pw_data_add.setPlaceholderText("비밀번호")
        login_btn = QPushButton('로그인', self)
        register_btn = QPushButton('회원가입', self)
        # self.result_label = QLabel('No item', self)

        # 버튼 클릭
        login_btn.clicked.connect(self.login_btn_event)
        register_btn.clicked.connect(self.register_btn_event)

        # [디자인]
        # 레이아웃
        vbox = QVBoxLayout()
        vbox.addStretch(3)
        vbox.addWidget(logo)
        vbox.addStretch(1)
        vbox.addWidget(self.id_data_add)
        vbox.addWidget(self.pw_data_add)
        vbox.addWidget(login_btn)
        vbox.addWidget(register_btn)
        # vbox.addWidget(self.result_label)
        vbox.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def login_btn_event(self):
        id = self.id_data_add.text()
        pw = self.pw_data_add.text()
        # 빈 공간 확인
        if not (id and pw):
            QMessageBox.question(self, '에러', '빈칸을 모두 채워주세요!', QMessageBox.Yes, QMessageBox.NoButton)
        # 특수문자 체크
        elif not ((id.isalnum() == 1) and (pw.isalnum() == 1)):
            QMessageBox.question(self, '에러', '아이디 또는 비밀번호에는 영문+숫자 조합만 사용해주세요!', QMessageBox.Yes, QMessageBox.NoButton)
        else:
            con = sqlite3.connect('user.db')
            cur = con.cursor()
            cur.execute("select * from user_info where user_id='%s'" % (id))
            account_check = cur.fetchone()
            # 로그인 시도 횟수 초과시 오류 출력
            if not account_check:
                QMessageBox.question(self, '에러', '아이디가 존재하지 않습니다.', QMessageBox.Yes, QMessageBox.NoButton)
            elif account_check[5] >= 5:
                QMessageBox.question(self, '에러', '시도횟수 초과!', QMessageBox.Yes, QMessageBox.NoButton)
            # 비밀번호 검증(근데 이부분은 암호화 해야함)
            elif account_check[2] == pw:
                QMessageBox.question(self, '로그인 성공', '로그인!', QMessageBox.Yes, QMessageBox.NoButton)
                cur.execute("update user_info set try_count = 0 where user_id='%s'" % (id))
                global session
                session = account_check[1]
                widget.setCurrentIndex(widget.currentIndex() + 2)
                con.commit()
                con.close()
                print(account_check[1])
            # 로그인 실패시 시도 횟수 추가
            else:
                cur.execute("update user_info set try_count = try_count+1 where user_id='%s'" % (id))
                con.commit()
                con.close()
                QMessageBox.question(self, '에러', '로그인 실패 아이디 또는 비밀번호를 확인해주세요!', QMessageBox.Yes, QMessageBox.NoButton)
        # text = self.id_data_add.text()
        # self.result_label.setText(text)
        # 로그인 검증 하도록 설정

    # 회원가입 창 이동
    def register_btn_event(self):
        print(session)
        widget.setCurrentIndex(widget.currentIndex() + 1)


# 회원가입 페이지
# 회원가입후 데이터 초기화

# Todo 얼굴학습 클래스와 연동되게. 아직 프로그래스바, 혹은 학습 상태 조회 개발 안 됐으며 메시지 박스로 확인 버튼 구현 안 됐음.
# Todo 그 다음에 자동으로 모델 형성되는거 구현 안 됨

class RegisterWindow(QWidget):

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
        self.id_data_add = QLineEdit()
        self.id_data_add.setPlaceholderText("아이디")
        self.pw_data_add = QLineEdit()
        self.pw_data_add.setEchoMode(QLineEdit.Password)
        self.pw_data_add.setPlaceholderText("비밀번호")
        self.re_pw_data_add = QLineEdit()
        self.re_pw_data_add.setEchoMode(QLineEdit.Password)
        self.re_pw_data_add.setPlaceholderText("비밀번호 재입력")
        self.name_data_add = QLineEdit()
        self.name_data_add.setPlaceholderText("이름")
        register_btn = QPushButton('회원가입', self)
        back_btn = QPushButton('뒤로가기', self)

        # 버튼 클릭
        register_btn.clicked.connect(self.register_btn_event)
        back_btn.clicked.connect(self.back_btn_event)

        # [디자인]
        # 레이아웃
        vbox = QVBoxLayout()
        vbox.addStretch(3)
        vbox.addWidget(logo)
        vbox.addStretch(1)
        vbox.addWidget(self.id_data_add)
        vbox.addWidget(self.pw_data_add)
        vbox.addWidget(self.re_pw_data_add)
        vbox.addWidget(self.name_data_add)
        vbox.addWidget(register_btn)
        vbox.addWidget(back_btn)
        vbox.addStretch(3)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def register_btn_event(self):
        id = self.id_data_add.text()
        pw = self.pw_data_add.text()
        re_pw = self.re_pw_data_add.text()
        name = self.name_data_add.text()
        # 빈 공간 확인
        if not (id and pw and re_pw and name):
            QMessageBox.question(self, '에러', '빈칸을 모두 채워주세요!', QMessageBox.Yes, QMessageBox.NoButton)
        elif not ((id.isalnum() == 1) and (pw.isalnum() == 1) and (name.isalnum() == 1)):
            QMessageBox.question(self, '에러', '아이디,비밀번호, 이름에는 영문+숫자 조합만 사용해주세요!', QMessageBox.Yes, QMessageBox.NoButton)
        elif pw != re_pw:
            QMessageBox.question(self, '에러', '비밀번호 입력값이 다릅니다! 다시 입력해주세요.', QMessageBox.Yes, QMessageBox.NoButton)
        else:
            con = sqlite3.connect('user.db')
            cur = con.cursor()
            cur.execute("select * from user_info where user_id='%s'" % (id))
            account = cur.fetchall()
            # 아이디 검증시 중복 체크
            if account:
                QMessageBox.question(self, '에러', '아이디가 중복됩니다! 다른 아이디를 입력해주세요.', QMessageBox.Yes, QMessageBox.NoButton)
            else:
                cur.execute(
                    "insert into user_info(user_id, user_pw, user_name, try_count) values ('%s', '%s', '%s', 0)" % (
                    id, pw, name))
                con.commit()
                con.close()
                returnB = QMessageBox.question(self, '회원가입 완료', '회원가입이 완료되었습니다! 로그인창으로 이동합니다.', QMessageBox.Yes,
                                               QMessageBox.NoButton)
                if returnB == QMessageBox.Yes:
                    widget.setCurrentIndex(widget.currentIndex() - 1)

    def back_btn_event(self):
        widget.setCurrentIndex(widget.currentIndex() - 1)

# 3. 카툰 필터 및 fps 출력
# Todo 카툰화되어 있는거 모델써서 사람 인식하고 마스킹하는걸로 바꿔치기하기.
def cartoon_filter(img):
    h, w = img.shape[:2]
    img2 = cv2.resize(img, (w // 2, h // 2))

    blr = cv2.bilateralFilter(img2, -1, 20, 7)
    edge = 255 - cv2.Canny(img2, 80, 120)
    edge = cv2.cvtColor(edge, cv2.COLOR_GRAY2BGR)
    dst = cv2.bitwise_and(blr, edge)
    dst = cv2.resize(dst, (w, h), interpolation=cv2.INTER_NEAREST)

    return dst


def print_fps_on_video(prevtime, fps, frame):
    curtime = time.time()
    sec = curtime - prevtime
    prevtime = curtime
    fps = 1 / (sec)
    str = "FPS: %0.1f" % fps
    cv2.putText(frame, str, (0, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0))

    return prevtime, fps


# 4. 가상 카메라 스레드
class VirtualCam(QThread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.filter = True
        self.prevtime = 0
        self.fps = fps

    def resume(self):
        self.running = True

    def stop(self):
        self.running = False

    def filter_on(self):
        self.filter = True

    def filter_off(self):
        self.filter = False

    def run(self):
        with pyvirtualcam.Camera(width=width, height=height, fps=fps) as cam:
            while True:
                ret, frame = camera.read()
                if not ret:
                    break

                if self.filter:
                    frame = cartoon_filter(frame) # TODO 여기에  cartoon_filter -> 마스킹 함수로 변경. 여기 이름 수정 안 하면 그냥해

                # fps 출력하게 하기 (필요없음 주석 처리 ㄱ)
                self.prevtime, self.fps = print_fps_on_video(self.prevtime, self.fps, frame)

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                cam.send(frame)
                cam.sleep_until_next_frame()
                if self.running == False:
                    break


# 5. 방송 스레드
# Todo subprocess 명령어 실행 시 에러 나올 경우 종료하기
class Streaming(QThread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.filter = True
        self.prevtime = 0
        self.fps = fps

    def resume(self):
        self.running = True

    def stop(self):
        self.running = False

    def filter_on(self):
        self.filter = True

    def filter_off(self):
        self.filter = False

    def run(self):
        command = ['ffmpeg',
                   '-y',
                   '-re',
                   '-f', 'rawvideo',
                   '-vcodec', 'rawvideo',
                   '-pix_fmt', 'bgr24',
                   '-r', '10',
                   '-s', "{}x{}".format(width, height),
                   '-i', '-',
                   '-f', 'dshow',
                   '-rtbufsize', '10M',
                   '-i', f"audio={audio}",
                   '-c:v', 'libx264',
                   '-pix_fmt', 'yuv420p',
                   '-preset', 'ultrafast',
                   '-c:a', 'aac',
                   '-f', 'flv',
                   streaming_url]

        p = sp.Popen(command, stdin=sp.PIPE)

        while True:
            ret, frame = camera.read()
            if not ret:
                break

            if self.filter:
                frame = cartoon_filter(frame)  # TODO 여기에  cartoon_filter -> 마스킹 함수로 변경

            # fps 출력하게 하기 (필요없음 주석 처리 ㄱ)
            self.prevtime, self.fps = print_fps_on_video(self.prevtime, self.fps, frame)

            p.stdin.write(frame.tobytes())

            if self.running == False:
                break
        p.stdin.close()
        p.terminate()


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
        widget.setCurrentIndex(widget.currentIndex()+1)

    def openAddFaceDataClass(self):
        widget.setCurrentIndex(widget.currentIndex() + 5)

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
        virtual_cam_btn.clicked.connect(self.openBroadClass)
        before_btn.clicked.connect(self.openMainClass)

        # [디자인]
        # 레이아웃
        vbox = QVBoxLayout()
        vbox.addStretch(3)
        vbox.addWidget(logo)
        vbox.addStretch(1)
        vbox.addWidget(streaming_btn)
        vbox.addWidget(virtual_cam_btn)
        # vbox.addWidget(before_btn)
        vbox.addStretch(3)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def openMainClass(self):
        widget.setCurrentIndex(widget.currentIndex()-1)

    def openBroadClass(self):
        widget.setCurrentIndex(widget.currentIndex() + 2)

    def openStreamingClass(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)


class StreamingWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.streaming = Streaming()

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
        global streaming_url
        streaming_url = self.server_url.text() + "/" + self.stream_key.text()
        if (len(streaming_url) < 2):
            QMessageBox.about(self, '경고', '입력값이 없습니다.')
        else:
            widget.setCurrentIndex(widget.currentIndex() + 2)


class StreamingBroadWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.streaming = Streaming()

    def initUI(self):
        # 로고 이미지 사용
        pixmap = QPixmap('res/logo.png')
        logo = QLabel()
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignHCenter)

        # [기능]
        # 버튼
        self.work_btn = QPushButton('방송 시작', self)
        filter_btn = QPushButton('마스킹 제거', self)
        main_btn = QPushButton('송출 중단 후 메인화면', self)

        # 버튼 클릭
        self.work_btn.clicked.connect(self.streamClicked)
        filter_btn.clicked.connect(self.filterClicked)
        main_btn.clicked.connect(self.stopAndOpenMainClass)

        # [디자인]
        # 레이아웃
        vbox = QVBoxLayout()
        vbox.addStretch(3)
        vbox.addWidget(logo)
        vbox.addStretch(1)
        vbox.addWidget(self.work_btn)
        vbox.addWidget(filter_btn)
        vbox.addWidget(main_btn)
        vbox.addStretch(3)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)

        self.setLayout(hbox)

    # [버튼] 버튼 클릭 이벤트 처리 함수
    def filterClicked(self):
        btn = self.sender()
        if (btn.text() == '마스킹 적용'):
            btn.setText('마스킹 제거')
            self.streaming.filter_on()
        else:
            btn.setText('마스킹 적용')
            self.streaming.filter_off()

    def streamClicked(self):
        btn = self.sender()
        if (btn.text() == '방송 시작'):
            btn.setText('방송 중단')
            self.streaming.resume()
            self.streaming.start()
        else:
            btn.setText('방송 시작')
            self.streaming.stop()
            self.streaming.quit()

    def stopAndOpenMainClass(self):
        if (self.work_btn.text() == '방송 중단'):
            self.streaming.stop()
            self.streaming.quit()
        widget.setCurrentIndex(widget.currentIndex() - 3)


class VirtualCamBroadWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.virtualCam = VirtualCam()

    def initUI(self):
        # 로고 이미지 사용
        pixmap = QPixmap('res/logo.png')
        logo = QLabel()
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignHCenter)

        # [기능]
        # 버튼
        self.work_btn = QPushButton('가상 카메라 시작', self)
        filter_btn = QPushButton('마스킹 제거', self)
        main_btn = QPushButton('송출 중단 후 메인화면', self)

        # 버튼 클릭
        self.work_btn.clicked.connect(self.streamClicked)
        filter_btn.clicked.connect(self.filterClicked)
        main_btn.clicked.connect(self.stopAndOpenMainClass)

        # [디자인]
        # 레이아웃
        vbox = QVBoxLayout()
        vbox.addStretch(3)
        vbox.addWidget(logo)
        vbox.addStretch(1)
        vbox.addWidget(self.work_btn)
        vbox.addWidget(filter_btn)
        vbox.addWidget(main_btn)
        vbox.addStretch(3)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)

        self.setLayout(hbox)

    # [버튼] 버튼 클릭 이벤트 처리 함수
    def filterClicked(self):
        btn = self.sender()
        if (btn.text() == '마스킹 적용'):
            btn.setText('마스킹 제거')
            self.virtualCam.filter_on()
        else:
            btn.setText('마스킹 적용')
            self.virtualCam.filter_off()

    def streamClicked(self):
        btn = self.sender()
        if (btn.text() == '가상 카메라 시작'):
            btn.setText('가상 카메라 중단')
            self.virtualCam.resume()
            self.virtualCam.start()
        else:
            btn.setText('가상 카메라 시작')
            self.virtualCam.stop()
            self.virtualCam.quit()

    def stopAndOpenMainClass(self):
        if (self.work_btn.text() == '가상 카메라 중단'):
            self.virtualCam.stop()
            self.virtualCam.quit()
        widget.setCurrentIndex(widget.currentIndex() - 2)

class AddFaceData(QWidget):

    def __init__(self):
        super().__init__()
        self.running = False
        self.initUI(self.running)

    def initUI(self, running):
        alert_text = QLabel('학습 데이터 추가 중', self)
        alert_text.setAlignment(Qt.AlignCenter)
        aa = 0
        dummy = QLabel('dummy', self)
        dummy.setAlignment(Qt.AlignCenter)
        ### 비디오창 라벨 ###
        self.win = QWidget()
        self.flabel = QLabel()
        ###################

        btn_return = QPushButton('학습 종료', self)
        btn_return.clicked.connect(self.openMainClass)
        btn_capture_start = QPushButton("학습 시작", self)
        btn_capture_start.clicked.connect(self.start)

        # [디자인]
        # 레이아웃
        vbox = QVBoxLayout()
        vbox.addStretch(0)
        vbox.addWidget(alert_text)  # 안내문 출력
        vbox.addWidget(self.flabel) # 비디오화면 출력 라벨
        if aa:
            vbox.addWidget(dummy)

        vbox.addWidget(btn_capture_start)
        vbox.addWidget(btn_return)

        vbox.addStretch(3)
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)
        self.setLayout(hbox)
        self.win.setLayout(vbox)

    def openMainClass(self):
        self.running = False
        widget.setCurrentIndex(widget.currentIndex() - 4)

    def start(self):
        self.running = True
        th = threading.Thread(target=self.userCapture)
        #self.dummy.setText("change")
        #self.dummy.repaint()
        print("쓰레드 지정까지 됨")
        th.start()
        print("쓰레드 started..")

    # Todo 파일 경로랑 모델이 하드코딩되어 있기 때문에 db에서 유저 정보 가져가서.
    def userCapture(self):
        cap = cv2.VideoCapture(0)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.flabel.resize(width, height)

        # Network
        model = 'res10_300x300_ssd_iter_140000_fp16.caffemodel'
        config = 'deploy.prototxt'
        net = cv2.dnn.readNet(model, config)

        # Output Directory & File Index
        outdir = 'train_images/User1'
        prefix = outdir + '/face_'
        self.file_idx = 1

        png_list = glob.glob(prefix + '*.png')
        if len(png_list) > 0:
            png_list.sort()
            last_file = png_list[-1]
            self.file_idx = int(last_file[-8:-4]) + 1

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
                    filename = '{0}{1:04d}.png'.format(prefix, self.file_idx)
                    self.save_face(frame, (x1, y1), (x2, y2), filename, self.file_idx)
                    self.file_idx += 1
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

    def save_face(self, frame, p1, p2, filename, file_idx):
        #self.dummy.setText("f{file_idx}")

        cp = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
        print(f"저장프로세스 작동중: {file_idx}")
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

if __name__ == '__main__':
    def center(widget):
        qr = widget.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        widget.move(qr.topLeft())


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

    loginWindow = LoginWindow()
    registerWindow = RegisterWindow()
    mainWindow = MainWindow()
    transmissionWindow = TransmissionWindow()
    streamingWindow = StreamingWindow()
    virtualCamBroadWindow = VirtualCamBroadWindow()
    streamingBroadWindow = StreamingBroadWindow()
    addFaceData = AddFaceData()

    widget.addWidget(loginWindow)
    widget.addWidget(registerWindow)
    widget.addWidget(mainWindow)
    widget.addWidget(transmissionWindow)
    widget.addWidget(streamingWindow)
    widget.addWidget(virtualCamBroadWindow)
    widget.addWidget(streamingBroadWindow)
    widget.addWidget(addFaceData)
    # [트레이 아이콘]
    tray_icon = QSystemTrayIcon()
    tray_icon.setIcon(QIcon('res/live.png'))

    show_action = QAction("Show")
    hide_action = QAction("Hide")
    quit_action = QAction("Exit")

    show_action.triggered.connect(widget.show)
    hide_action.triggered.connect(widget.hide)
    quit_action.triggered.connect(qApp.quit)

    tray_menu = QMenu()
    tray_menu.addAction(show_action)
    tray_menu.addAction(hide_action)
    tray_menu.addAction(quit_action)
    tray_icon.setContextMenu(tray_menu)
    tray_icon.show()

    # [윈도우 정보]
    widget.resize(640, 480)
    center(widget)
    widget.show()

    sys.exit(app.exec_())