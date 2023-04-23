# -*- coding: utf-8 -*-
"""
Created on 2023-04-14 20:42:19
---------
@summary:
---------
@author: LinSanxian
"""

import feapder
from fake_headers import Headers
import json
import pandas as pd
import requests

def get_proxy():
    
    return requests.get("http://127.0.0.1:5010/get/").json().get("proxy")

def fake_header():
    headers = Headers(
        browser="chrome",  # Generate only Chrome UA
        os="win",  # Generate ony Windows platform
        headers=True  # generate misc headers
    ).generate()

    headers['Content-Type'] = 'application/json'

    return headers


class Aminer(feapder.AirSpider):

    # __custom_setting__ = dict(
    #     PROXY_ENABLE=True,
    #     PROXY_POOL_URL="http://localhost:5010/get",
    # )

    def start_callback(self):
        print("爬虫开始")

    def end_callback(self):
        print("爬虫结束")

    def download_midware(self, request):
        # 这里随机取个代理使用即可
        request.proxies = {"http": "http://{}".format(get_proxy())} 
        return request

    def start_requests(self, save_cache=True):
        keywords = ['RL', 'MARL']

        for keyword in keywords:
            for page in range(1, 500):
                payload = {
                    "query": keyword,
                    "needDetails": True,
                    "page": page,
                    "size": 20,
                    "filters": []
                }
                data = json.dumps(payload, separators=(',', ':'))
                yield feapder.Request(
                    "https://searchtest.aminer.cn/aminer-search/search/publication",
                    method="POST",
                    data=data,
                    headers=fake_header(),
                    callback=self.parse_ids
                )

    def validate(self, request, response):
        if response.status_code != 200:
            raise Exception("response.status_code != 200")

    def parse_ids(self, request, response):

        ids = [item['id'] for item in response.json['data']['hitList']]
        params = {
            "a": "getPaperData__pub.GetPageData___"
        }

        for article_id in ids:

            payload = json.dumps([
                {
                    "action": "pub.GetPageData",
                    "parameters": {
                        "ids": [
                            f"{article_id}"
                        ],
                        "include": [
                            "bp"
                        ]
                    }
                }
            ])

            yield feapder.Request(
                "https://apiv2.aminer.cn/magic",
                method="POST",
                data=payload,
                params=params,
                headers=fake_header(),
                callback=self.parse
            )

    def parse(self, request, response):
        columns = ['id', 'title', 'title_zh',
                   'authors', 'abstract', 'abstract_zh', 'pdf']
        df = pd.DataFrame(columns=columns)

        for item in response.json['data']:
            id = item['pub']['id']
            title = item['pub']['title'] if 'title' in item['pub'] else ''
            title_zh = item['pub']['title_zh'] if 'title_zh' in item['pub'] else ''
            authors = item['pub']['authors'] if 'authors' in item['pub'] else ''
            abstract = item['pub']['abstract'] if 'abstract' in item['pub'] else ''
            abstract_zh = item['pub']['abstract_zh'] if 'abstract_zh' in item['pub'] else ''
            pdf = item['pub']['pdf'] if 'pdf' in item['pub'] else ''

            df = df.append(pd.DataFrame(
                [[id, title, title_zh, authors, abstract, abstract_zh, pdf]], columns=columns))

        df.to_csv('aminer.csv', mode='a', encoding='utf-8-',
                  columns=columns, index=False, header=False)


if __name__ == "__main__":
    Aminer(thread_count=10).start()
