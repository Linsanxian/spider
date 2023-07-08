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
from feapder.utils import tools
import os
from datetime import datetime

api_host = "http://52.83.181.7:8091"
token = ""
filename = "dy_feedback"

START_DATE = datetime(2023, 6, 1)
END_DATE = datetime(2023, 7, 1)
STORE_DATA_FILE = "dy.csv"


def is_within_date_range(date_str):
    comment_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    if START_DATE <= comment_time <= END_DATE:
        return True
    else:
        return False


class Xy700DY(feapder.AirSpider):

    def start_requests(self):
        store_data = pd.read_csv(STORE_DATA_FILE, encoding="utf-8")

        uri = "/proxy/dyapp/shop_product_list/"
        url = f"{api_host}{uri}"

        for index, row in store_data.iterrows():
            shopID = row['店铺ID']
            shopName = row['店铺名称']
            encrypt_shop_id = row['店铺短位ID']
            params = {
                "sec_shop_id": encrypt_shop_id,
                "cursor": "0",
                "sort_type": "0",
                "keep_key": "",
                "token": token
            }
            yield feapder.Request(url=url, params=params, callback=self.parse_shop_goods, meta={
                "shopName": shopName,
                "shopID": shopID,
                "encrypt_shop_id": encrypt_shop_id}
            )

    def parse_shop_goods(self, request, response):
        data = response.json

        if not data['data']['aweme_msg_list']:
            return

        goods = data['data']['aweme_msg_list']

        for good in goods:
            good_name = good['name']
            goods_id = good['product_id']

            uri = "/proxy/dyapp/good_comments/"
            params = {
                "id": goods_id,
                "page": "0",
                "filter_type": "7",
                "token": token
            }
            url = f"{api_host}{uri}"

            yield feapder.Request(url=url, params=params, callback=self.parse_comments, meta={
                "good_name": good_name,
                "goods_id": goods_id,
                "shopName": request.meta.get("shopName"),
                "shopID": request.meta.get("shopID"),
                "encrypt_shop_id": request.meta.get("encrypt_shop_id")
            }
            )
        has_more = data['data']['has_more']

        if has_more:
            cursor = data['data']['cursor']
            keep_key = data['data']['keep_key']
            uri = "/proxy/dyapp/shop_product_list/"
            url = f"{api_host}{uri}"

            params = {
                "sec_shop_id": request.meta.get("encrypt_shop_id"),
                "cursor": cursor,
                "sort_type": "0",
                "keep_key": keep_key,
                "token": token
            }

            yield feapder.Request(url=url, params=params, callback=self.parse_shop_goods, meta={
                "shopName": request.meta.get("shopName"),
                "shopID": request.meta.get("shopID"),
                "encrypt_shop_id": request.meta.get("encrypt_shop_id")}
            )

    def parse_comments(self, request, response):
        data = response.json
        columns = ["shopName", "shopID", "encrypt_shop_id",
                   "good_name", "goods_id", "comment", "comment_time"]
        df = pd.DataFrame(columns=columns)

        if not data['data']['items']:
            return

        comments = data['data']['items']

        for comment in comments:
            goods_comment = comment['content']
            if goods_comment != "":
                goods_comment_time = tools.timestamp_to_date(
                    comment['comment_time'])
                if is_within_date_range(goods_comment_time):
                    df.loc[0] = [
                        request.meta.get("shopName"),
                        request.meta.get("shopID"),
                        request.meta.get("encrypt_shop_id"),
                        request.meta.get("good_name"),
                        request.meta.get("goods_id"),
                        goods_comment,
                        goods_comment_time
                    ]
                    df.to_csv(f"{filename}.csv", mode="a",
                              encoding="utf-8", index=False, header=False)

        has_more = data['data']['has_more']

        if has_more:
            uri = "/proxy/dyapp/good_comments/"
            url = f"{api_host}{uri}"
            page = int(request.params.get("page"))
            page += 1
            params = {
                "id": request.meta.get("goods_id"),
                "page": page,
                "filter_type": "7",
                "token": token
            }

            yield feapder.Request(url=url, params=params, callback=self.parse_comments, meta={
                "good_name": request.meta.get("good_name"),
                "goods_id": request.meta.get("goods_id"),
                "shopName": request.meta.get("shopName"),
                "shopID": request.meta.get("shopID"),
                "encrypt_shop_id": request.meta.get("encrypt_shop_id")
            }
            )


if __name__ == "__main__":
    Xy700DY(thread_count=5).start()
