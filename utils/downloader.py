import os
import time
from pathlib import Path
from threading import Thread

import requests
from Crypto.Cipher import AES
from PySide6.QtCore import Signal, QThread

from utils import analyzer


def get_store_path():
    max_num = 0
    print("current path(downloader):", os.path.abspath('.'))
    for _ in os.listdir("store"):
        if int(_) > max_num:
            max_num = int(_)
    return "store/" + str(max_num + 1)


class DownloadThread(QThread):
    signal = Signal(str, str)
    MAX_THREAD_NUM = 20

    def __init__(self, url, download_mode, store_path):
        super().__init__()
        self.download_mode = download_mode
        self.url = url
        self.serial_number, self.store_path = str(store_path.rsplit('/')[-1]), Path(store_path)

        os.mkdir(self.store_path)
        m3u8_analyzer = analyzer.Analyzer(url, self.store_path, self.download_mode)

        self.log_file = open(self.store_path / "log.txt", "a+")
        self.key = m3u8_analyzer.key
        self.iv = m3u8_analyzer.iv
        self.ts_url_list = m3u8_analyzer.ts_url_list

    def log(self, txt):
        self.log_file.write(txt + "\n")
        print(txt)

    # download .ts file and decode
    def download_ts(self, url, out, mark_list, i, finished_num):
        mark_list[i] = 1
        response = requests.get(url)
        if response.status_code == 200:
            self.log("ts url:" + url + "time:" + str(time.ctime()))
            with open(out, "wb") as f:
                if self.key:
                    if self.iv:
                        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
                    else:
                        cipher = AES.new(self.key, AES.MODE_CBC, b"0000000000000000")
                    content = cipher.decrypt(response.content)
                else:
                    content = response.content
                f.write(content)
                finished_num[0] += 1
                self.signal.emit("value", str((int((finished_num[0] / len(mark_list)) * 100))))
        else:
            self.log(f"{response.status_code}: {url}")
        mark_list[i] = 0

    # download ts files and decode all
    def download_ts_files(self, url_list):
        self.log("begin download\n")

        mark_list = [0] * len(url_list)

        finished_num = [0]

        for i in range(len(url_list)):
            out = self.store_path / (str(i) + ".ts")
            thread = Thread(target=self.download_ts, args=(url_list[i], out, mark_list, i, finished_num))
            thread.start()
            while sum(mark_list) > self.MAX_THREAD_NUM:
                QThread.msleep(100)
                pass

        while sum(mark_list) > 0:
            QThread.sleep(1)
            self.signal.emit("value", str((int((finished_num[0] / len(mark_list)) * 100))))
            pass

        self.log(f"download ok, downloaded {len(os.listdir(str(self.store_path)))}")

    def merge_files(self):
        self.log("begin merge")
        with open("ts/" + self.serial_number + ".ts", "wb") as l_f:
            file_list = os.listdir(str(self.store_path))
            file_list.sort(key=lambda x: int(x.replace(".ts", "")) if ".ts" in x else 0)
            for file in file_list:
                if ".ts" in file:
                    with open("store/" + self.serial_number + '/' + file, "rb") as s_f:
                        l_f.write(s_f.read())
        self.log("merged ok")

    def download(self):
        self.download_ts_files(self.ts_url_list)
        self.merge_files()

    def run(self):
        self.download()
