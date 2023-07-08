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
import os
from datetime import datetime

api_host = "http://52.83.181.7:8091"

token = ""
filename = "jd_feedback"

COLUMN = ["shopName", "shopId", "goodId",
          "goodName", "feedback", "creationTime"]

START_DATE = datetime(2023, 6, 1)
END_DATE = datetime(2023, 6, 30)


class Xy700JD(feapder.AirSpider):

    def get_comment_list(self, response):
        data = response.json
        return data.get("data", {}).get("comments", [])

    def get_page(self, request):
        return int(request.params.get("page", 1))

    def build_request_params(self, good_id, page, token):
        """构造请求参数"""
        return {
            "good_id": good_id,
            "page": str(page),
            "sku_comment": "0",
            "token": token,
            "sort": "4"
        }

    def is_within_date_range(self, date_str):
        comment_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

        if START_DATE <= comment_time <= END_DATE:
            return True
        else:
            return False

    def write_csv(self, filename, **kwargs):
        """
        将数据写入 csv 文件
        """

        df = pd.DataFrame(columns=COLUMN)
        new_data = {
            "shopName": kwargs.get("shopName"),
            "shopId": kwargs.get("shopId"),
            "goodId": kwargs.get("goodId"),
            "goodName": kwargs.get("goodName"),
            "feedback": kwargs.get("feedback"),
            "creationTime": kwargs.get("creationTime")
        }

        df = df.append(new_data, ignore_index=True)
        df.to_csv(f"{filename}.csv", mode='a',
                  encoding="utf-8", index=False, header=False)

    def start_requests(self):
        df = pd.read_csv("jd.csv", converters={'店铺ID': int})
        df_filtered = df.dropna(subset=['店铺ID'])
        store_ids = df_filtered.groupby("店铺ID")['店铺名称'].first()

        uri = "/proxy/other_api/jd_api/shop_goods/"
        url = f"{api_host}{uri}"
        for store_id, shopname in store_ids.items():
            shopName = shopname
            shopId = store_id
            params = {
                "shop_id": shopId,
                "page": "1",
                "sort": "0",
                "token": token
            }
            yield feapder.Request(url=url, params=params, callback=self.parse_shop_goods_list, meta={"shopId": shopId, "shopName": shopName})

    def parse_shop_goods_list(self, request, response):
        data = response.json

        shopId = request.meta.get("shopId")
        shopName = request.meta.get("shopName")

        good_list = data.get("data", {}).get("wareInfo", [])

        if not good_list:
            return

        for good in good_list:
            good_id = good.get("wareId")
            good_name = good.get("wname")

            params = self.build_request_params(good_id, 1, token)
            uri = "/proxy/other_api/jd_api/good_comment/"
            url = f"{api_host}{uri}"

            yield feapder.Request(url=url, params=params, callback=self.parse_good_comment,
                                  meta={
                                      "shopId": shopId,
                                      "goodId": good_id,
                                      "goodName": good_name,
                                      "shopName": shopName
                                  })

        if data.get("data", {}).get("hasNext"):
            page = self.get_page(request) + 1
            params = {
                "shop_id": shopId,
                "page": str(page),
                "sort": "0",
                "token": token
            }
            yield feapder.Request(url=request.url, params=params, callback=self.parse_shop_goods_list, meta={"shopId": shopId, "shopName": shopName})

    def parse_good_comment(self, request, response):

        shopId = request.meta.get("shopId")
        goodId = request.meta.get("goodId")
        goodName = request.meta.get("goodName")
        shopName = request.meta.get("shopName")
        max_page = response.json.get("data", {}).get("maxPage")

        comment_list = self.get_comment_list(response)

        if not comment_list:
            return

        for comment in comment_list:
            feedback = comment.get("content")
            comment_time_str = comment.get("creationTime")
            if self.is_within_date_range(comment_time_str):
                self.write_csv(filename, shopName=shopName, shopId=shopId, goodId=goodId,
                               goodName=goodName, feedback=feedback, creationTime=comment_time_str)
            else:
                continue
        
        page = self.get_page(request) + 1
        if page <= int(max_page):
            params = self.build_request_params(
                good_id=goodId, page=page, token=token)
            yield feapder.Request(url=request.url, params=params, callback=self.parse_good_comment,
                                  meta={
                                      "shopId": shopId,
                                      "goodId": goodId,
                                      "goodName": goodName,
                                      "shopName": shopName
                                  })


if __name__ == "__main__":
    Xy700JD(thread_count=5).start()
