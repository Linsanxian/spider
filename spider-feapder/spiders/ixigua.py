# -*- coding: utf-8 -*-
"""
Created on 2023-04-23 14:26:55
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


class Ixigua(feapder.Spider):

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

    def cookies(self):
        cookies = {
            "csrf_session_id": "a873a1fc56724759554cb764820469ed",
            "support_webp": "true",
            "support_avif": "true",
            "_tea_utm_cache_1768": "{%22utm_source%22:%22xiguastudio%22}",
            "_tea_utm_cache_2285": "{%22utm_source%22:%22xiguastudio%22}",
            "ixigua-a-s": "1",
            "ttwid": "1%7CCAolPFatxv1kW2seJ9DWEZ0XHKz-1rOIz5PdJVQF_I0%7C1682175822%7C013c3b47604c3f2aafdb308bf2b1f732e678d03a2f348db025dedf4f2acf3c1c",
            "arp_scroll_position": "4",
            "msToken": "9u5HwhlxkNxLosgE3L0Mu0FO1ABRPAeFF3ik68Ksci4UyOSYy6RCPcxS5HC_t5h7GZkZ69RakO79Uu0-rnkm2jR2k6R8oNlWQCcMJqWqFBWtYwcos6Vo4Q==",
            "tt_scid": "fcFJ-TXLMZKDex9JYHH-F.JY0U81.uu9mhfQIwycuJP-tAoDmxC4C.uVZBYt2gzT8cf1",
            "__ac_nonce": "06444da5d008fee25ba94",
            "__ac_signature": "_02B4Z6wo00f01WKK0FwAAIDAnMasbken8NViqtTAADzq8bloZMONOtr6PliKU3Ld0SLodRhGT5FzCR8D7EgNKWgz.HDhK9jae2uN0uLZWGwRlTl4tgChCTuc2kzNygr2xAsdnXWSCMID2A-.03"
        }
        return cookies
    
    def download_midware(self, request):
        request.cookies = self.cookies()
        request.headers = self.fake_header()
        # request.proxies = self.proxies()
        request.verify = False
        return request        

    # 检查目录是否存在，不存在则创建
    def check_dir(self, path):
        import os
        if not os.path.exists(path):
            os.makedirs(path)

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


# if __name__ == "__main__":
#     Ixigua(redis_key="xxx:xxx").start()
