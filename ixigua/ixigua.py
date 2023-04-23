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
            "csrf_session_id": "a873a1fc56724759554cb764820469ed",
            "support_webp": "true",
            "support_avif": "true",
            "_tea_utm_cache_1768": "{%22utm_source%22:%22xiguastudio%22}",
            "_tea_utm_cache_2285": "{%22utm_source%22:%22xiguastudio%22}",
            "ixigua-a-s": "1",
            "msToken": "9DLhGnEDTISavZ6rdTNQFqS4R4b-nk4XDsYRgyMfnFgQ5YQft7vtaggF05OEIz17rSj-KM8t_KZq7OrvivkH_D2ppbarM2Ao1gi2wcRAng9GoPB7HgfvhlSK6qbJcg==",
            "tt_scid": "4T0qDTHl044IoYf.nJwRyXItDYn1h76WznT2sN-X0dHZdpwoRUz8XQTj89uGsx-Hb893",
            "ttwid": "1%7CCAolPFatxv1kW2seJ9DWEZ0XHKz-1rOIz5PdJVQF_I0%7C1682175193%7Cf46f202a2167266ab5316cbc9a28599d90de37906f7591acb5ac81755c5cb993",
            "arp_scroll_position": "191",
            "__ac_nonce": "06443f4f700ef18f46e96",
            "__ac_signature": "_02B4Z6wo00f01SOKWkwAAIDCt1wBQLxzEqUjql7AACyk5qt15ia4GpllnyAfITzqzBNQug0dinDMPvfT8leY9ZobFZOjmxHLKjm5gbpg-XMfxE90DJe5QeGSaLzkyzvQUAAKjcxq-JhC4A3p54"
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

    def get_http_proxy(self):
        return requests.get("http://127.0.0.1:5010/get/").json().get("proxy")

    def get_https_proxy(self):
        return requests.get("http://127.0.0.1:5010/get/", params={"type": "https"}).json().get("proxy")

    def proxies(self):
        proxies = {
            "http": "http://{}".format(self.get_http_proxy()),
            "https": "http://{}".format(self.get_https_proxy()),
        }
        return proxies

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
        request.proxies = self.proxies()
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
