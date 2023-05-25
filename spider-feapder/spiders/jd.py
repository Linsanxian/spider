# -*- coding: utf-8 -*-
"""
Created on 2023-05-18 22:40:06
---------
@summary:
---------
@author: admin1
"""

import feapder
import pandas as pd

host = "http://52.83.181.7:8091"
token = ""

goods_urls = [
    "https://item.jd.com/3742683.html?bbtf=1",
    "https://item.jd.com/100043646838.html",
    "https://item.jd.com/100055368673.html",
    "https://item.jd.com/1749557.html?bbtf=1",
    "https://item.jd.com/10037103873952.html?bbtf=1",
    "https://item.jd.com/10052490458220.html?bbtf=1",
    "https://item.jd.com/10052490458219.html?bbtf=1",
    "https://item.jd.com/10038277065310.html?bbtf=1",
    "https://item.jd.com/10052079434202.html?bbtf=1"
]


class Jd(feapder.Spider):

    def start_requests(self):
        uri = "/proxy/other_api/jd_api/good_detail/"
        url = f"{host}{uri}"

        for goods_url in goods_urls:
            goods_id = goods_url.split("/")[-1].split(".")[0]
            params = {
                "good_id": goods_id,
                "token": token
            }
            yield feapder.Request(url=url, params=params, callback=self.parse_goods_detail, meta={"goods_url": goods_url})

    def parse_goods_comment(self, request, response):
        data = response.json

        goods_url = request.meta['goods_url']
        shop_name = data['data']['domain']['data']['shopInfo']['shopName']
        title = data['data']['domain']['data']['skuInfo']['skuName']
        goods_id = data['data']['domain']['data']['skuInfo']['skuId']
        props = data['data']['domain']['data']['skuInfo']['brandName']

        uri = "/proxy/other_api/jd_api/good_comment/"
        url = f"{host}{uri}"
        params = {
            "good_id": goods_id,
            "sku_comment": "0",
            "page": "1",
            "sort": "0",
            "token": token
        }
        yield feapder.Request(url=url, params=params, callback=self.parse_goods_comment,
                              meta={
                                  "goods_url": goods_url,
                                  "shop_name": shop_name,
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

        for comment in data['data']['comments']:
            feedback = comment['content']
            feedbackDate = comment['creationTime']
            userNick = comment['nickname']
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
            
        df.to_csv(f"jd/{goods_id}.csv", mode='a', header=False, index=False)

        totalPage = int(data['data']['maxPage'])
        currentPage = int(request.params['page'])

        if currentPage < totalPage:
            nextPage = currentPage + 1
            uri = "/proxy/other_api/jd_api/good_comment/"
            url = f"{host}{uri}"
            params = {
                "good_id": goods_id,
                "sku_comment": "0",
                "page": str(nextPage),
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

