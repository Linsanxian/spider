# -*- coding: utf-8 -*-
"""
Created on 2023-06-12 15:48:21
---------
@summary:
---------
@author: admin1
"""

import feapder
import pandas as pd
import re
import os
from datetime import datetime

api_host = "http://52.83.181.7:8091"
token = ""
filename = "tb_feedback"

START_DATE = datetime(2023, 6, 1)
END_DATE = datetime(2023, 7, 1)


class Xy700TB(feapder.AirSpider):

    def is_within_date_range(self, date_str):
        comment_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M')

        if START_DATE <= comment_time <= END_DATE:
            return True
        else:
            return False

    def start_requests(self):
        store_data = pd.read_csv(
            "tb.csv", encoding="utf-8", converters={'店铺ID': int, '商品ID': int})

        uri = "/proxy/other_api/tb_api/goods_detail/"
        url = f"{api_host}{uri}"

        for index, row in store_data.iterrows():
            shopID = row['店铺ID']
            shopName = row['店铺名称']
            good_id = row['商品ID']
            params = {
                "good_id": good_id,
                "token": token
            }
            yield feapder.Request(url=url, params=params, callback=self.parse_good, meta={
                "shopName": shopName
            })

    def parse_good(self, request, response):
        data = response.json

        shopName = request.meta.get("shopName")
        shopID = data['data']['seller']['shopId']
        UserId = data['data']['seller']['userId']

        uri = "/proxy/other_api/tb_api/shop_good_list/"
        url = f"{api_host}{uri}"

        params = {
            "shop_id": shopID,
            "seller_id": UserId,
            "token": token,
            "page": '1',
            "sort": '1'
        }

        yield feapder.Request(url=url, params=params, callback=self.parse_shop_good_list, meta={
            "shopName": shopName,
            "shopID": shopID,
            "userid": UserId
        })

    def parse_shop_good_list(self, request, response):
        data = response.json

        try:
            if not data['data']['itemsArray']:
                return
        except:
            return

        totalPage = data['data']['totalPage']
        goods = data['data']['itemsArray']
        for good in goods:
            goods_id = good['item_id']
            goods_title = good['title']

            uri = "/proxy/other_api/tb_api/goods_comment/"
            url = f"{api_host}{uri}"

            params = {
                "good_id": goods_id,
                "token": token,
                "page": '1',
                "sort": '1',
                "rate_type": '3'
            }

            yield feapder.Request(url=url, params=params, callback=self.parse_good_comment, meta={
                "shopName": request.meta.get("shopName"),
                "shopID": request.meta.get("shopID"),
                "userid": request.meta.get("UserId"),
                "goods_title": goods_title,
                "goods_id": goods_id
            })

        page = request.params.get("page")
        if int(page) > int(totalPage):
            return

        page = int(page) + 1
        params = {
            "shop_id": request.meta.get("shopID"),
            "seller_id": request.meta.get("UserId"),
            "token": token,
            "page": str(page),
            "sort": '1'
        }

        yield feapder.Request(url=request.url, params=params, callback=self.parse_shop_good_list, meta={
            "shopName": request.meta.get("shopName"),
            "shopID": request.meta.get("shopID"),
            "userid": request.meta.get("UserId")
        })

    def parse_good_comment(self, request, response):

        columns = ["shopName", "shopID", "goods_id", "UserID", "goods_title",
                   "comment_text", "comment_time"]

        df = pd.DataFrame(columns=columns)

        data = response.json
        if not data['data']:
            return

        comments = data['data']['rateInfoList']
        totalPage = data['data']['rateMeta']['totalPage']

        for comment in comments:
            comment_text = comment['comment']
            comment_time = comment['commentDate']
            if self.is_within_date_range(comment_time):
                df = df.append({
                    "shopName": request.meta.get("shopName"),
                    "shopID": request.meta.get("shopID"),
                    "goods_id": request.meta.get("goods_id"),
                    "userid": request.meta.get("UserId"),
                    "goods_title": request.meta.get("goods_title"),
                    "comment_text": comment_text,
                    "comment_time": comment_time
                }, ignore_index=True)

        df.to_csv(f"{filename}.csv", mode='a', index=False,
                  header=False, encoding="utf-8")

        page = request.params.get("page")
        if int(page) > int(totalPage):
            return

        page = int(page) + 1

        uri = "/proxy/other_api/tb_api/goods_comment/"
        url = f"{api_host}{uri}"
        parms = {
            "good_id": request.meta.get("goods_id"),
            "token": token,
            "page": str(page),
            "sort": '1',
            "rate_type": '3'
        }

        yield feapder.Request(url=url, params=parms, callback=self.parse_good_comment, meta={
            "shopName": request.meta.get("shopName"),
            "shopID": request.meta.get("shopID"),
            "goods_id": request.meta.get("goods_id"),
            "goods_title": request.meta.get("goods_title"),
            "userid": request.meta.get("UserId")
        })


if __name__ == "__main__":
    Xy700TB(thread_count=10).start()
