# -*- coding: utf-8 -*-
"""
Created on 2023-05-16 19:44:45
---------
@summary:
---------
@author: admin1
"""

import feapder
import pandas as pd
from urllib.parse import urlparse, parse_qs

host = "http://52.83.181.7:8091"
token = ""

goods_urls = [
    "https://detail.tmall.com/item.htm?abbucket=2&id=657607062868",
    "https://detail.tmall.com/item.htm?abbucket=2&id=675231335581",
    "https://detail.tmall.com/item.htm?abbucket=2&id=674172992235",
    "https://detail.tmall.com/item.htm?abbucket=2&id=684985253031",
    "https://detail.tmall.com/item.htm?abbucket=2&id=672674172359",
    "https://detail.tmall.com/item.htm?abbucket=2&id=657357233287",
    "https://detail.tmall.com/item.htm?abbucket=2&id=41100287248",
    "https://detail.tmall.com/item.htm?abbucket=9&id=641732197172",
    "https://detail.tmall.com/item.htm?abbucket=2&id=685038137387",
    "https://item.taobao.com/item.htm?spm=a230r.1.14.93.990974a56y9Xww&id=696227654321"
]


class Tb(feapder.Spider):
    def start_requests(self):
        uri = "/proxy/other_api/tb_api/goods_detail/"
        url = f"{host}{uri}"

        for goods_url in goods_urls:
            parse_url = urlparse(goods_url)
            query = parse_qs(parse_url.query)
            if "id" in query:
                params = {
                    "good_id": query["id"][0],
                    "token": token
                }
                yield feapder.Request(url=url, params=params, callback=self.parse_goods_detail, meta={"goods_url": goods_url})

    def parse_goods_detail(self, request, response):
        data = response.json

        goods_url = request.meta['goods_url']
        shopName = data['data']['seller']['shopName']
        title = data['data']['item']['title']
        goods_id = data['data']['item']['itemId']
        props = next((item.get('品牌') for item in data['data']['props']['groupProps'][0]['基本信息'] if '品牌' in item), None)


        uri = "/proxy/other_api/tb_api/goods_comment/"
        url = f"{host}{uri}"
        params = {
            "good_id": goods_id,
            "rate_type": "1",
            "page": "1",
            "sort": "0",
            "token": token
        }
        yield feapder.Request(url=url, params=params, callback=self.parse_goods_comment,
                              meta={
                                  "goods_url": goods_url,
                                  "shopName": shopName,
                                  "title": title,
                                  "goods_id": goods_id,
                                  "props": props
                              })

    def parse_goods_comment(self, request, response):
        data = response.json

        columns = ['goods_url', 'shopName', 'title', 'goods_id',
                   'props', 'comment', 'feedbackDate', 'userNick']
        df = pd.DataFrame(columns=columns)

        goods_url = request.meta['goods_url']
        shopName = request.meta['shopName']
        title = request.meta['title']
        goods_id = request.meta['goods_id']
        props = request.meta['props']

        for comment in data['data']['rateList']:
            feedback = comment['feedback']
            feedbackDate = comment['feedbackDate']
            userNick = comment['userNick']
            df = df.append({
                "goods_url": goods_url,
                "shopName": shopName,
                "title": title,
                "goods_id": goods_id,
                "props": props,
                "comment": feedback,
                "feedbackDate": feedbackDate,
                "userNick": userNick
            }, ignore_index=True)
            
        df.to_csv(f"{goods_id}.csv", mode='a', header=False, index=False)

        totalPage = int(data['data']['totalPage'])
        currentPage = int(request.params['page'])

        if currentPage < totalPage:
            nextPage = currentPage + 1
            uri = "/proxy/other_api/tb_api/goods_comment/"
            url = f"{host}{uri}"
            params = {
                "good_id": goods_id,
                "rate_type": "1",
                "page": nextPage,
                "sort": "0",
                "token": token
            }
            yield feapder.Request(url=url, params=params, callback=self.parse_goods_comment,
                                  meta={
                                      "goods_url": goods_url,
                                      "shopName": shopName,
                                      "title": title,
                                      "goods_id": goods_id,
                                      "props": props
                                  })


# if __name__ == "__main__":
#     Tb().start()
