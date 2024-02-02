import json
import os
import re
from pathlib import Path
from typing import Optional

import requests
import wget
from Crypto.Cipher import AES


class Function:
    @staticmethod
    def get_iv(m3u8_text) -> Optional[bytes]:
        res = re.search("IV=.*\n", m3u8_text)
        if res:
            return bytes.fromhex(res.group()[5:-1])
        else:
            return None

    @staticmethod
    def get_key_url(m3u8_text):
        res = re.search('URI=".*"', m3u8_text)
        if res:
            key_url_part = res.group()[5:-1]
            if "http" in key_url_part:
                key_url = key_url_part
                return key_url

            if key_url_part[0] == '/':
                key_url_part = key_url_part[1:]

            for i in range(1, len(m3u8_url.split("/"))):
                m3u8_url_part = "".join(m3u8_url.rsplit("/", i)[0])
                key_url = m3u8_url_part + '/' + key_url_part
                response = requests.get(key_url)
                if response.status_code == 200 and len(response.content) == 16:
                    return key_url
        else:
            return None

    @staticmethod
    def get_key(m3u8_text):
        key_url = Function.get_key_url(m3u8_text)
        if key_url is None:
            return None
        if key_url:
            res = requests.get(key_url)
            return res.content

    @staticmethod
    def decode_ts(encoded_data, key: bytes, iv: bytes = None):
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plain_data = cipher.decrypt(encoded_data)
        return plain_data


class Analyzer:
    SimpleAnalyze = 1
    RecursiveAnalyze = 2

    def __init__(self, url: str, store_path, analyze_mode):
        if not os.path.exists(store_path):
            return

        self.url = url
        # get parameters
        if "?" in self.url:
            self.pure_url, self.m3u8_url_argv = self.url.split("?")
        else:
            self.m3u8_url_argv = ""
            self.pure_url = self.url

        self.analyze_mode = analyze_mode
        self.store_path = Path(store_path)
        self.key = None
        self.iv = None
        self.ts_url_list = None
        self.error = False
        self.log_file = open(self.store_path / "log.txt", "w+")
        self.config = None
        self.setup()

    def setup(self):
        # configure
        with open("config.json", "r") as f:
            self.config = json.load(f)

        # replace url
        replace_dict = self.config["replace_str"]
        for old, new in replace_dict.items():
            self.url = self.url.replace(old, new)
        self.log("m3u8 url: " + self.url)

        # download m3u8 file
        self.log("downloading m3u8 file...")
        m3u8_path = self.store_path / "m3u8.txt"
        wget.download(url=self.url,
                      out=str(m3u8_path)
                      )
        with open(m3u8_path, 'r') as f:
            m3u8_txt = f.read()

        # get key
        self.log("get key")
        self.key = Function.get_key(m3u8_txt)
        if self.key:
            self.log("key:" + str(self.key))

        # get iv
        self.log("get iv...")
        self.iv = Function.get_iv(m3u8_txt)
        if self.iv:
            self.log("iv" + str(self.iv))

        # get ts url
        self.log("get ts url...")
        self.ts_url_list = self.get_ts_url(m3u8_txt)
        self.log(f"ts url list:, {self.ts_url_list}")
        self.store_result()

    def simple_analysis(self, m3u8_txt):
        ts_url_list = []
        m3u8_url_front_part = self.url.rsplit('/', 1)[0]
        ord_ts_list = re.findall(".*.ts", m3u8_txt)
        for _ in ord_ts_list:
            if "http" in _:
                ts_url_list.append(_)
            else:
                ts_url_list.append(m3u8_url_front_part + '/' + _)
        
        return ts_url_list
    
    @staticmethod
    def test_url_status_code(url):
        status_code = requests.get(url).status_code
        return status_code

    def recursive_analysis(self, m3u8_txt):
        # ts_url_list: ts list
        # m3u8_url_front_part: http://xxxx/xxx/xxx/
        # ts_url_0: a ts url

        ts_url_list = []  # result
        ord_ts_list = re.findall(".*.ts", m3u8_txt)
        ts_url_0 = ord_ts_list[0]

        m3u8_url_front_part = self.url.rsplit('/', 1)[0]

        self.log("try to get m3u8_url_part")
        # 获取.ts的url 序号前部分 如http://xxx/ + "xxxx.ts"
        ts_params = ""
        if "http" not in ts_url_0:
            # get ts params
            if "?" in ts_url_0:
                pure_ts_url, ts_params = self.url.split("?")
            else:
                pure_ts_url, ts_params = self.m3u8_url_argv, ""

            # 穷举获取.ts的url序号前部分 如http://xxx/
            for i in range(1, 10):
                m3u8_url_front_part = "".join(self.url.rsplit("/", i)[0])  # m3u8 url 前的某部分
                url = m3u8_url_front_part + '/' + pure_ts_url + "?" + ts_params
                response = requests.get(url)
                if response.status_code == 200:
                    break

            m3u8_url_front_part = m3u8_url_front_part + '/'
        self.log("m3u8 url part:" + m3u8_url_front_part)

        # 判断ts的序号是否可递推
        ts_url_head = ''
        front_zero_num = 0
        self.log("try ts head")
        for i in range(1, len(ts_url_0) + 1):
            url = m3u8_url_front_part \
                  + ts_url_0[:- len(".ts") - i] + '1' + '0' * (i - 1) + '.ts' \
                  + "?" + ts_params

            self.log("test url: " + url)

            response = requests.get(url)
            if response.status_code == 200:
                ts_url_head = ts_url_0[:-3 - i]
            else:
                front_zero_num = i - 1
                break
        self.log("ts head:" + ts_url_head)

        # get ts head part, 不包含序号的ts url
        if m3u8_url_front_part:
            ts_url_part = m3u8_url_front_part + '/' + ts_url_head
        else:
            ts_url_part = m3u8_url_front_part + ts_url_head
        self.log("ts url part:" + ts_url_part)

        find = []

        def get_url(_index):
            _index = int(_index)
            _url = ts_url_part + str("{:0>" + str(front_zero_num) + "d}").format(_index) + ".ts" + "?" + ts_params
            self.log(f"test url: {_url}")
            return _url

        def is_valid_url_index(_index):
            _index = int(_index)
            _url = get_url(index)
            try:
                status_code = self.test_url_status_code(_url)
                if status_code == 200:
                    _url = get_url(_index + 1)
                    if self.test_url_status_code(url) != 200:
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

        return ts_url_list

    def get_ts_url(self, m3u8_txt):
        # simple analysis
        if self.analyze_mode == self.SimpleAnalyze:
            print("mode: simple analysis")
            return self.simple_analysis(m3u8_txt)

        # recursive analyze
        elif self.analyze_mode == self.RecursiveAnalyze:
            return self.recursive_analysis(m3u8_txt)

    def log(self, txt):
        self.log_file.write(txt + "\n")
        print(txt)

    def store_result(self):
        results = {
            "m3u8_url": self.url,
            "ts path": self.ts_url_list,
            "key": self.key,
            "iv": self.iv
        }

        with open(self.store_path / "results.json", "w+") as f:
            json.dump(results, f)


if __name__ == '__main__':
    m3u8_url = input('url:')
    analyzer = Analyzer(url=m3u8_url, store_path=Path("m3u8/store/1"), analyze_mode=Analyzer.SimpleAnalyze)
