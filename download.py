import os
import re
import shutil
import traceback
from pathlib import Path
from threading import Thread
from typing import Optional

import requests
import yaml
from Crypto.Cipher import AES


class M3u8Downloader:
    MAX_THREAD_NUM = 30

    def __init__(self):
        self.key = None
        self.iv = None
        self.key_url = None
        self.fail_count = 0
        self.name = None
        self.setup()

    def setup(self):
        pass

    @staticmethod
    def download(self):
        pass

    @staticmethod
    def m_print(string):
        print(string)

    @staticmethod
    def get_key_url(m3u8_url, m3u8_text=None):
        if m3u8_text is None:
            m3u8_text = requests.get(m3u8_url).text
        res = re.search('URI=".*"', m3u8_text)
        if res:
            key_url_part = res.group()[5:-1]
            if "http" in key_url_part:
                return key_url_part
            if key_url_part[0] == '/':
                key_url_part = key_url_part[1:]
            print(f"{' ' * 20}try key url{' ' * 20}")
            for i in range(1, len(m3u8_url.split("/"))):
                m3u8_url_part = "".join(m3u8_url.rsplit("/", i)[0])
                key_url = m3u8_url_part + '/' + key_url_part
                response = requests.get(key_url)
                if response.status_code == 200 and len(response.content) == 16:
                    return key_url
        else:
            return None

    def get_key(self, m3u8_url, m3u8_text):
        self.key_url = self.get_key_url(m3u8_url, m3u8_text)
        print("key url:", self.key_url)
        if self.key_url is None:
            raise Exception("key url not found or not accessible")
        res = requests.get(self.key_url)
        return res.content

    @staticmethod
    def get_iv(m3u8_text) -> Optional[bytes]:
        res = re.search("IV=.*\n", m3u8_text)
        if res:
            return bytes.fromhex(res.group()[5:-1])
        else:
            return None

    def download_by_m3u8(self, m3u8_url):
        # check if downloaded
        with open("record.yaml", 'r') as f:
            record = yaml.safe_load(f)
        if m3u8_url in record.keys():
            name = record[m3u8_url]
            if name in os.listdir("store"):
                print("downloaded before")
                return
            else:
                print("deleted dir")

        # get the name of the dir
        dir_list = os.listdir("ts")
        dir_list.sort(key=lambda x: int(x.replace(".ts", '')))
        if dir_list:
            name = str(int(dir_list[-1].replace(".ts", '')) + 1)
        else:
            name = "1"
        os.mkdir("store/" + name)
        self.name = name  # dir name

        # check if the url is valid
        response = requests.get(m3u8_url)
        if response.status_code == 200:
            with open("store/" + self.name + '/' + "m3u8.m3u8", 'w') as f:
                m3u8_text = response.text
                f.write(m3u8_text)
        else:
            print("m3u8 url not valid")
            return

        # save the url
        with open("store/" + self.name + '/' + "url.txt", 'w') as f:
            f.write(m3u8_url)

        try:
            self._download_ts(m3u8_url, m3u8_text)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            shutil.rmtree("store/" + self.name)

    def _download_ts(self, m3u8_url, m3u8_text):
        ts_url_part_list = re.findall(".*.ts", m3u8_text)
        test_part = ts_url_part_list[0]

        m3u8_url_part = ''
        if "http" not in test_part:
            for i in range(1, 10):
                m3u8_url_part = "".join(m3u8_url.rsplit("/", i)[0])
                url = m3u8_url_part + '/' + test_part
                response = requests.get(url)
                if response.status_code == 200:
                    break
            m3u8_url_part = m3u8_url_part + '/'
        print("m3u8 url part:", m3u8_url_part)

        ts_head = ''
        print(f"{' ' * 20}try ts head{' ' * 20}")
        zero_num = 0
        for i in range(1, len(test_part) + 1):
            url = m3u8_url_part + test_part[:-3 - i] + '1' + '0' * (i - 1) + '.ts'
            response = requests.get(url)
            if response.status_code == 200:
                ts_head = test_part[:-3 - i]
            else:
                zero_num = i - 1
                break
        print("ts head:", ts_head)

        if "?" in m3u8_url:
            url_end = "?" + m3u8_url.split("?")[1]
        else:
            url_end = ''

        # get ts head part
        ts_url_part = m3u8_url_part + ts_head
        print("ts url part:", ts_url_part)

        # get key and iv
        self.key = self.get_key(m3u8_url, m3u8_text)
        self.iv = self.get_iv(m3u8_text)
        print(f"key: {self.key}, iv: {self.iv}")
        if self.iv:
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        else:
            cipher = AES.new(self.key, AES.MODE_CBC, b"0000000000000000")

        # 404 count
        self.fail_count = 0

        # download .ts file
        def download_ts(url, out):
            response = requests.get(url, out)
            if response.status_code == 200:
                print("ts url:", url)
                import time
                print("time:", time.ctime())
                with open(out, "wb") as f:
                    content = cipher.decrypt(response.content)
                    f.write(content)
            else:
                self.fail_count += 1

        thread_list = []
        for i in range(10000):
            url = ts_url_part + str("{:0>" + str(zero_num) + "d}").format(i) + ".ts" + url_end
            out = "store/" + self.name + '/' + str(i) + ".ts"
            if len(thread_list) <= self.MAX_THREAD_NUM:
                thread = Thread(target=download_ts, args=(url, out))
                thread_list.append(thread)
            else:
                thread = Thread(target=download_ts, args=(url, out))
                thread_list.append(thread)
                for thread in thread_list:
                    thread.start()
                for thread in thread_list:
                    thread.join()
                thread_list.clear()
            if self.fail_count > 30:
                break
        print(f"download ok, downloaded {len(os.listdir('store/' + self.name))}")

        with open("ts/" + self.name + ".ts", "wb") as l_f:
            file_list = os.listdir("store/1")
            file_list.sort(key=lambda x: int(x.replace(".ts", "")) if ".ts" in x else 0)
            for file in file_list:
                if ".ts" in file:
                    with open("store/1" + '/' + file, "rb") as s_f:
                        l_f.write(s_f.read())

        # deal with m3u8 file
        # key
        m3u8_text = m3u8_text.replace(self.key_url, "key.key")
        m3u8_text = m3u8_text.replace(ts_head, "")
        with open("store/" + self.name + "/key.key", "wb") as f:
            f.write(self.key)
        with open("store/" + self.name + "/iv.iv", "wb") as f:
            if self.iv:
                f.write(self.iv)
        with open("store/" + self.name + "/m3u8.m3u8", "w") as f:
            f.write(m3u8_text)

        # record the url and dir name
        with open("record.yaml", 'r') as f:
            record = yaml.safe_load(f)
        record[m3u8_url] = self.name
        with open("record.yaml", 'w') as f:
            yaml.dump(record, f)

    @staticmethod
    def decode_ts(encoded_data, key: bytes, iv: bytes = None):
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plain_data = cipher.decrypt(encoded_data)
        return plain_data


if __name__ == "__main__":
    abs_dir = os.path.abspath(".")
    dir_path = Path(abs_dir)
    dir_list = ["store", "ts"]
    file_list = ["record.yaml"]
    for d in dir_list:
        if not os.path.exists(d):
            os.mkdir(dir_path / d)

    if not os.path.exists("record.yaml"):
        with open("record.yaml", "w") as f:
            f.write("None: None")

    download = M3u8Downloader()
    m3u8_url = input("url: ")
    m3u8_url = m3u8_url.replace("try", "trailer")
    download.download_by_m3u8(m3u8_url)
