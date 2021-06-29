from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread
from PyQt5.QtWidgets import QDialog, QPushButton, QLabel, QTextBrowser, QHBoxLayout, QVBoxLayout, QFileDialog, QApplication
import os
from PIL import Image
import shutil

img_root = []
img_list = []

class MyMainGUI(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.open_button = QPushButton("이미지 경로")
        self.read_button = QPushButton("이미지 읽기")
        self.start_button = QPushButton("변환 시작")

        self.path_label = QLabel("", self)
        self.img_list_tb = QTextBrowser()
        self.progress_Label = QLabel("", self)

        hbox = QHBoxLayout()
        hbox.addStretch(0)
        hbox.addWidget(self.open_button)
        hbox.addWidget(self.path_label)
        hbox.addStretch(5)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.read_button)
        hbox2.addWidget(self.start_button)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addWidget(self.img_list_tb)
        vbox.addStretch(3)
        vbox.addLayout(hbox2)
        vbox.addStretch(1)
        vbox.addWidget(self.progress_Label)

        self.setLayout(vbox)

        self.setWindowTitle('PyGomPhoto')
        self.setGeometry(300, 300, 500, 200)


class MyMain(MyMainGUI):
    add_sec_signal = pyqtSignal()
    send_instance_singal = pyqtSignal("PyQt_PyObject")

    def __init__(self, parent=None):
        super().__init__(parent)

        self.open_button.clicked.connect(self.open_floder)
        self.read_button.clicked.connect(self.read)
        self.start_button.clicked.connect(self.convert)

        self.th_reader = reader(parent=self)
        self.th_reader.updated_list.connect(self.list_update)

        self.th_convert = converter(parent=self)
        self.th_convert.updated_label.connect(self.progress_update)

        self.show()

    @pyqtSlot()
    def open_floder(self):
        self.fname = QFileDialog.getExistingDirectory(self, "폴더 열기")
        self.path_label.setText(self.fname)

        global img_root
        img_root = self.fname

    @pyqtSlot()
    def read(self):
        self.th_reader.start()

    @pyqtSlot()
    def convert(self):
        self.th_convert.start()

    @pyqtSlot(str)
    def list_update(self, msg):
        self.img_list_tb.append(msg)
    
    @pyqtSlot(str)
    def progress_update(self, msg):
        global img_list
        p = int(float(int(msg) + 1) / len(img_list) * 100)
        self.progress_Label.setText("{}% 변환 완료".format(p))


class reader(QThread):
    updated_list = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.main = parent

    def __del__(self):
        self.wait()

    def run(self):
        global img_root
        self.root = img_root

        if self.root is not None:
            for (path, dir, files) in os.walk(self.root):
                for filename in files:
                    ext = os.path.splitext(filename)[-1]
                    if ext in ('.JPG', '.PNG', '.GIF', '.BMP', '.jpg', '.png', '.gif', '.bmp'):
                        self.updated_list.emit("%s/%s" % (path, filename))
                        img_list.append("%s/%s" % (path, filename))


class converter(QThread):
    updated_label = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.main = parent

    def __del__(self):
        self.wait()

    def run(self):
        global img_list
        self.list = img_list

        if len(self.list) != 0:
            for i in range(len(self.list)):
                self.get_exif_timestamp(self.list[i])
                self.updated_label.emit(str(i))

    def get_exif_timestamp(self, path):
        img_name = path.split("/")[-1]

        try:
            date = Image.open(path)._getexif()[36867]
            date = (date.split(" ")[0]).replace(":", "-")
            
            yyyy = date.split("-")[0]
            mmdd = date.split("-")[1] + "-" + date.split("-")[2]
            new_dir = "./Image/" + yyyy + "/" + mmdd

            if not os.path.exists(new_dir):
                os.makedirs(new_dir)
            
            shutil.copyfile(path, new_dir + "/" + img_name)

        except:
            new_dir = "./Image/" + "날짜정보 없는 사진"

            if not os.path.exists(new_dir):
                os.makedirs(new_dir)
            
            shutil.copyfile(path, new_dir + "/" + img_name)



if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = MyMain()
    app.exec_()