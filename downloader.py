# -*- coding:utf-8 -*-
# @Time     : 2023/4/9 20:52
# @Author   : ALIEN(XuLang)
# @Project  : tool

import json
import os
import re
import sys
import time
import traceback
from threading import Thread
from typing import Optional

import requests
from Crypto.Cipher import AES
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QApplication, QListWidgetItem

from ui.ui_downloader import Ui_Downloader
# os.system(r'"D:\Python\Python Data\Scripts\pyrcc5.exe" resource.qrc -o resource_rc.py')
# os.system(r'"D:\Python\Python Data\Scripts\pyuic5.exe" ui.ui -o ui_downloader.py')
# os.system(r'"D:\Python\Python Data\Scripts\pyuic5.exe" state_widget.ui -o ui_state_widget.py')
from ui.ui_state_widget import Ui_stateWidget


class DownloadThread(QThread):
    signal = pyqtSignal(str, str)
    MAX_THREAD_NUM = 30

    def __init__(self, url):
        super().__init__()
        self.replace_dict = None
        self.config = None
        self.headers = None
        self.m3u8_text = ''
        self.cipher = None
        self.ts_head = ''
        self.m3u8_url_part = ''
        self.m3u8_url_argv = ''
        self.first_ts_url_argv = ""
        self.url = url
        self.key = None
        self.iv = None
        self.key_url = None
        self.name = ''
        self.is_pure_data = False

    def run(self):
        self.download()

    def setup(self):
        # get name
        try:
            self.name = str(int(max(os.listdir("store"), key=int)) + 1)
        except Exception:
            self.name = '1'

        # mkdir
        os.mkdir("../store/" + self.name)

        # load config
        with open("config.json", "r") as f:
            self.config = json.load(f)
        self.replace_dict = self.config["replace_str"]

        self.headers = self.config["headers"]

        # record ord url
        with open("record.yaml", "a+") as f:
            f.write(f"{self.name}: {self.url}\n")

        # check if the url is valid
        self.url = self.url_replace(self.url, self.replace_dict)
        response = requests.get(self.url, headers=self.headers)
        if response.status_code == 200:
            with open("../store/" + self.name + '/' + "m3u8.m3u8", 'w') as f:
                self.m3u8_text = response.text
                f.write(self.m3u8_text)
        else:
            self.log("m3u8 url not valid")
            return

        # save the url
        with open("../store/" + self.name + '/' + "url.txt", 'w') as f:
            f.write(self.url)

    def download(self):
        try:
            self.setup()
            self._download()
            self.merge_files()
            self.closing_work()
        except Exception as e:
            self.log(str(e))
            self.log(traceback.format_exc())
            # shutil.rmtree("../store/" + self.name)

    def _download(self):
        # get parameters
        if "?" in self.url:
            self.m3u8_url_argv = "?" + self.url.split("?")[1]
        else:
            self.m3u8_url_argv = ""

        # get ts list by m3u8
        ord_ts_list = re.findall(".*.ts", self.m3u8_text)
        first_ts_url = ord_ts_list[0]

        self.log("try to get m3u8_url_part")

        # 获取.ts的url 序号前部分 如http://xxx/
        self.m3u8_url_part = ''
        if "http" not in first_ts_url:
            if "?" in self.url:
                first_ts_url_pure = self.url.split("?")[1]
            else:
                first_ts_url_pure = self.url
            if "?" in first_ts_url:
                self.first_ts_url_argv = "?" + self.url.split("?")[1]
            else:
                self.first_ts_url_argv = self.m3u8_url_argv
            for i in range(1, 10):
                self.m3u8_url_part = "".join(self.url.rsplit("/", i)[0])
                url = self.m3u8_url_part + '/' + first_ts_url_pure + self.first_ts_url_argv
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    break
            self.m3u8_url_part += '/'
        self.log("m3u8 url part:" + self.m3u8_url_part)

        # 判断ts的序号是否可递进
        self.ts_head = ''
        self.log(f"try ts head")
        zero_num = 0
        for i in range(1, len(first_ts_url) + 1):
            url = self.m3u8_url_part + first_ts_url[:-3 - i] + '1' + '0' * (i - 1) + '.ts' + self.first_ts_url_argv
            self.log("test url: " + url)
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                self.ts_head = first_ts_url[:-3 - i]
            else:
                zero_num = i - 1
                break

        self.log("ts head:" + self.ts_head)
        # get key and iv
        self.key = self.get_key(self.url, self.m3u8_text)
        if self.key:
            self.iv = self.get_iv(self.m3u8_text)
        else:
            self.iv = None
        if self.key:
            self.log(f"key: {self.key}, iv: {self.iv}")
        else:
            self.is_pure_data = True

        if not self.is_pure_data:
            if self.iv:
                self.cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            else:
                self.cipher = AES.new(self.key, AES.MODE_CBC, b"0000000000000000")

        # 如果为可递进序号的ts
        if self.ts_head and not self.is_pure_data:
            self.log("download mode 1")
            self.download_mode1(zero_num)
        else:
            self.log("download mode 2")
            self.download_mode2()
        self.log("finished")

    # m3u8文件中的ts文件按数字标号  0.ts
    def download_mode1(self, zero_num):
        # get ts head part, 不包含序号的ts url
        if self.m3u8_url_part:
            ts_url_part = self.m3u8_url_part + '/' + self.ts_head
        else:
            ts_url_part = self.m3u8_url_part + self.ts_head
        self.log("ts url part:" + ts_url_part)

        find = []

        def get_url(index):
            index = int(index)
            url = ts_url_part + str("{:0>" + str(zero_num) + "d}").format(index) + ".ts" + self.first_ts_url_argv
            self.log(f"test url: {url}")
            return url

        def is_valid_url_index(index):
            index = int(index)
            url = get_url(index)
            try:
                status_code = self.test_url_code(url)
                if status_code == 200:
                    url = get_url(index + 1)
                    if self.test_url_code(url) != 200:
                        find.append(True)
                    return True
                else:
                    self.log("net error code:" + str(status_code))
                    return False
            except Exception as e:
                self.log(str(e)[-3:-1])
                # shutil.rmtree("../store/" + self.name)

        def find_max_index(left, right):
            if find:
                return left
            if left == right:
                return left
            middle = (left + right) // 2
            if is_valid_url_index(middle):
                return find_max_index(middle, right)
            else:
                return find_max_index(left, middle)

        index = 1
        while True:
            if is_valid_url_index(index):
                index *= 2
            else:
                break
        max_index = find_max_index(index // 2, index)

        url_list = []
        for i in range(0, max_index + 1):
            url_list.append(get_url(i))
        self.download_ts_files(url_list)

    def download_mode2(self):
        url_list = []
        ord_ts_list = re.findall(".*.ts", self.m3u8_text)
        first_ts_url = ord_ts_list[0]
        if "http" in first_ts_url:
            url_list = ord_ts_list
        else:
            for _ in ord_ts_list:
                url = self.m3u8_url_part + _ + self.m3u8_url_argv
                url_list.append(url)
                self.log("url:" + url)

        self.download_ts_files(url_list)

    @staticmethod
    def test_url_code(url):
        status_code = requests.get(url).status_code
        return status_code

    # download ts files and decode all
    def download_ts_files(self, url_list):
        self.log("begin download\n")

        mark_list = [0] * len(url_list)
        for i in range(len(url_list)):
            out = "../store/" + self.name + '/' + str(i) + ".ts"
            thread = Thread(target=self.download_ts, args=(url_list[i], out, mark_list, i))
            thread.start()
            while sum(mark_list) > self.MAX_THREAD_NUM:
                pass
            self.log(f"{i}/{len(url_list)}")
            with open("../store/" + self.name + "/log.txt", 'a') as f:
                f.write(url_list[i] + '\n')
            self.signal.emit("value", str((int(((i + 1) / len(url_list)) * 100))))
        while sum(mark_list) > 0:
            pass
        self.log(f"download ok, downloaded {len(os.listdir('../store/' + self.name))}")

    def merge_files(self):
        # init cipher
        self.log("begin merge")
        with open("../ts/" + self.name + ".ts", "wb") as l_f:
            file_list = os.listdir("../store/" + self.name)
            file_list.sort(key=lambda x: int(x.replace(".ts", "")) if ".ts" in x else 0)
            for file in file_list:
                if ".ts" in file:
                    with open("../store/" + self.name + '/' + file, "rb") as s_f:
                        l_f.write(s_f.read())
        self.log("merged ok")

    def closing_work(self):
        # 收尾处理
        # deal with m3u8 file
        m3u8_text = self.m3u8_text
        if self.ts_head:
            m3u8_text = m3u8_text.replace(self.ts_head, "")
        if self.key:
            m3u8_text = m3u8_text.replace(self.key_url, "key.key")
            with open("../store/" + self.name + "/key.key", "wb") as f:
                f.write(self.key)
        if self.iv:
            with open("../store/" + self.name + "/iv.iv", "wb") as f:
                f.write(self.iv)
        with open("../store/" + self.name + "/m3u8.m3u8", "w") as f:
            f.write(m3u8_text)

    def get_key_url(self, m3u8_url, m3u8_text=None):
        if m3u8_text is None:
            m3u8_text = requests.get(m3u8_url, headers=self.headers).text
        res = re.search('URI=".*"', m3u8_text)
        if res:
            key_url_part = res.group()[5:-1]
            if "http" in key_url_part:
                return key_url_part
            if key_url_part[0] == '/':
                key_url_part = key_url_part[1:]

            for i in range(1, len(m3u8_url.split("/"))):
                m3u8_url_part = "".join(m3u8_url.rsplit("/", i)[0])
                key_url = m3u8_url_part + '/' + key_url_part
                response = requests.get(key_url, headers=self.headers)
                if response.status_code == 200 and len(response.content) == 16:
                    return key_url
        else:
            return None

    # download .ts file and decode
    def download_ts(self, url, out, mark_list, i):
        mark_list[i] = 1
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            self.log("ts url:" + url + "time:" + str(time.ctime()))
            with open(out, "wb") as f:
                if not self.is_pure_data:
                    content = self.cipher.decrypt(response.content)
                else:
                    content = response.content
                f.write(content)
        else:
            self.log(f"{response.status_code}: {url}")
        mark_list[i] = 0

    @staticmethod
    def url_replace(m3u8_url, replace_dict):
        for ord, new in replace_dict.items():
            m3u8_url = m3u8_url.replace(ord, new)
        return m3u8_url

    def log(self, text):
        self.signal.emit("label", text)
        with open("../store/" + self.name + "/log.txt", 'a') as f:
            f.write(text + '\n')

    def run(self) -> None:
        self.download()

    def get_key(self, m3u8_url, m3u8_text):
        self.log(f"try key url")
        self.key_url = self.get_key_url(m3u8_url, m3u8_text)
        if self.key_url:
            self.log("key url:" + self.key_url)
        if self.key_url is None:
            self.log("key url not found or not accessible")
            self.is_pure_data = True
            return None
        if self.key_url:
            res = requests.get(self.key_url, headers=self.headers)
            return res.content

    @staticmethod
    def get_iv(m3u8_text) -> Optional[bytes]:
        res = re.search("IV=.*\n", m3u8_text)
        if res:
            return bytes.fromhex(res.group()[5:-1])
        else:
            return None

    @staticmethod
    def decode_ts(encoded_data, key: bytes, iv: bytes = None):
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plain_data = cipher.decrypt(encoded_data)
        return plain_data


class Downloader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scroll_area_layout = None
        self.ui = Ui_Downloader()
        self.w, self.h = self.width(), self.height()
        self.state_widgets = []
        self.thread_list = []
        self.ui.setupUi(self)

        self.setup()

    def setup(self):
        self.ui.downloadButton.clicked.connect(lambda: self.download(self.ui.urlEdit.text()))

    def download(self, url):
        self.ui.urlEdit.clear()

        self.w, self.h = self.width(), self.height()
        state_widget_ui = Ui_stateWidget()
        state_widget = QWidget()
        state_widget.setContentsMargins(0, 5, 0, 5)
        state_widget_ui.setupUi(state_widget)
        state_widget_ui.urlLabel.setText(url)
        state_widget_ui.infoLabel.setText("  ")

        state_widget_ui.infoLabel.setFixedSize(self.w - 50, 20)
        state_widget_ui.urlLabel.setFixedSize(self.w - 50, 20)
        state_widget_ui.progressBar.setFixedSize(self.w - 50, 20)
        state_widget.setFixedSize(self.w - 50, 80)

        item = QListWidgetItem()
        self.ui.infoWidget.addItem(item)
        self.ui.infoWidget.setItemWidget(item, state_widget)
        state_widget_ui.progressBar.setValue(0)

        download_thread = DownloadThread(url)
        self.thread_list.append(download_thread)
        download_thread.start()


        def update_show(str_goal, string):
            if str_goal == "label":
                state_widget_ui.infoLabel.setText(string)
            if str_goal == "value":
                state_widget_ui.progressBar.setValue(int(string))

        download_thread.signal.connect(update_show)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    downloader = Downloader()
    downloader.show()
    sys.exit(app.exec_())
