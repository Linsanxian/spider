# -*- coding: utf-8 -*-
"""
Created on 2023-04-22 09:07:44
---------
@summary:
---------
@author: Linsanxian
"""

import feapder
import base64
import re
import json
from fake_headers import Headers
import pandas as pd
import requests
import os


class Ixigua(feapder.AirSpider):

    __custom_setting__ = {
        "SPIDER_MAX_RETRY_TIMES": 100,
        "USE_SESSION": True,
    }

    def start_requests(self):
        # 从json文件中读取视频链接标题,如果url为空则跳过
        df = pd.read_json('data.json')
        for i in range(len(df)):
            url = df['horizontalfeedcard__coverwrapper_链接'][i]
            if url == '':
                continue
            yield feapder.Request(url, callback=self.parse)

    def validate(self, request, response):
        if response.status_code != 200:
            raise Exception("response.status_code != 200")

    def cookies(self):
        cookies = {
            "a": 'b'
        }
        return cookies

    def fake_header(self):
        headers = Headers(
            browser="chrome",  # Generate only Chrome UA
            os="win",  # Generate ony Windows platform
            headers=True  # generate misc headers
        ).generate()

        headers['referer'] = "https://www.ixigua.com/"

        return headers

    # 检查目录是否存在，不存在则创建
    def check_dir(self, path):
        import os
        if not os.path.exists(path):
            os.makedirs(path)

    # 检查文件是否已经下载过了，文件大小需要大于1M，否则重新下载
    def check_file(self, file_name):
        if os.path.exists(file_name):
            if os.path.getsize(file_name) > 1024 * 1024:
                return True
            else:
                return False
        else:
            return False


    def download_midware(self, request):
        request.headers = self.fake_header()
        request.cookies = self.cookies()
        request.verify = False

        return request

    def parse(self, request, response):
        data = re.findall("_SSR_HYDRATED_DATA=(.*?)</script>",
                          response.text)[0].replace("undefined", "null")
        data = json.loads(data)
        video_list = video_list = data['anyVideo']['gidInformation']['packerData']['video']['videoResource']['normal']

        video_keys = list(video_list["video_list"].keys())
        for video_key in video_keys:
            definition = video_list["video_list"][video_key]["definition"]
            if definition == "720p":
                video_url = video_list["video_list"][video_key]["main_url"]
                break
            else:
                video_url = video_list["video_list"]['video_1']["main_url"]

        user_info = data['anyVideo']['gidInformation']['packerData']['video']['user_info']['name']
        title = data['anyVideo']['gidInformation']['packerData']['video']['title']
        url = base64.b64decode(video_url).decode(
            'utf-8')

        yield feapder.Request(url, callback=self.download, meta={"title": title, "user_info": user_info})

    def download(self, request, response):
        title = request.meta.get("title").replace("/", "")
        user_info = request.meta.get("user_info")
        file_name = "{}/{}".format(user_info, title)
        path = 'video/湖北'
        self.check_dir(f"{path}/{user_info}")
        with open(f"{path}/{file_name}.mp4", "wb") as f:
            f.write(response.content)


if __name__ == "__main__":
    Ixigua(thread_count=15).start()
