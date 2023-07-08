# -*- coding: utf-8 -*-
"""
Created on 2023-06-27 21:18:18
---------
@summary:
---------
@author: admin1
"""

import feapder
import pandas as pd
import requests
import os
import re
from fake_headers import Headers


# 检查路径是否存在，不存在则创建
def check_path(path):
    if not os.path.exists(path):
        os.makedirs(path)


PAGE_START = 1
URL_SUFFIX = "/"


class buynewjerseys(feapder.Spider):

    data = {
        "https://www.buynewjerseys.cc/jerseys-pc-cheapnfl-a-263": 710,
        "https://www.buynewjerseys.cc/jerseys-pc-cheapnfl-a-13": 598,
        "https://www.buynewjerseys.cc/jerseys-pc-cheapnfl-a-198": 208,
        "https://www.buynewjerseys.cc/jerseys-pc-cheapnfl-a-101": 164,
        "https://www.buynewjerseys.cc/jerseys-pc-cheapnfl-a-164": 138,
        "https://www.buynewjerseys.cc/jerseys-pc-cheapnfl-a-1": 145
    }

    def get_http_proxy(self):
        return requests.get("http://127.0.0.1:5010/get/").json().get("proxy")

    def get_https_proxy(self):
        return requests.get("http://127.0.0.1:5010/get/", params={"type": "https"}).json().get("proxy")

    def proxies(self):
        proxies = {
            "http": "http://{}".format(self.get_http_proxy()),
            "https": "http://{}".format(self.get_http_proxy()),
        }
        return proxies

    def extract_numbers(self, input_string):
        # 使用正则表达式匹配数字部分
        numbers = re.findall(r'\d+\.?\d*', input_string)

        if numbers:
            # 将匹配到的数字部分连接起来，并转换为浮点数
            extracted_numbers = float(''.join(numbers))
            return extracted_numbers
        else:
            return None

    def generate_pagination_urls(self, data):
        """
        生成分页 URL 列表

        Args:
            data: dict, 包含基础 URL 和页面数量的字典

        Returns:
            urls: list, 包含所有分页 URL 的列表
        """
        urls = []
        for base_url, page_count in data.items():
            for page in range(PAGE_START, page_count + PAGE_START):
                url = f"{base_url}-page-{page}{URL_SUFFIX}"
                urls.append(url)
        return urls

    def start_requests(self):
        for url in self.generate_pagination_urls(data=self.data):
            yield feapder.Request(url, method="GET", callback=self.parse)

    def validate(self, request, response):
        if response.status_code != 200:
            return False

    def download_midware(self, request):
        request.proxies = self.proxies()
        return request

    def fake_header(self):
        headers = Headers(
            browser="chrome",  # Generate only Chrome UA
            os="win",  # Generate ony Windows platform
            headers=True  # generate misc headers
        ).generate()
        return headers

    def parse(self, request, response):
        url_list = response.xpath(
            "//div[@class='itemImage']/a/@href").extract()

        for url in url_list:
            goods_url = f"https:{url}"
            yield feapder.Request(goods_url, method="GET", callback=self.parse_detail)

    def parse_detail(self, request, response):
        print(f"正在解析 {request.url} 的信息")
        LEVEL = ["level1", "level2", "level3", "level4"]
        GOODS_INFO = ["goods_title", "goods_price", "image_url"]

        df = pd.DataFrame(columns=LEVEL + GOODS_INFO)

        # 解析等级和商品标题
        text = response.xpath(
            "//div[@id='cheap-c-j-10']//a//text()").extract()
        level = [text[i] if len(text) > i else "" for i in range(4)]
        level_dict = dict(zip(LEVEL, level))

        goods_title = response.xpath(
            '//div[@id="product-info"]/div/b/font/text()').extract_first()
        goods_title = goods_title.replace('/', '')

        # 解析商品价格和图片链接
        firsthand_goods_price = response.xpath(
            '//h2[@class="productGeneral"]/span[@class="productSalePrice"]/text()').extract_first()
        goods_price = self.extract_numbers(firsthand_goods_price)
        image_url = response.xpath(
            "//a[@class='MagicZoom']/@href").extract_first()

        # 创建文件夹并下载图片
        path = "/".join([level_dict[l] for l in LEVEL] + [goods_title])
        check_path(path)
        with open(f"{path}/{goods_title}_01.jpg", "wb") as f:
            headers = self.fake_header()
            f.write(requests.get(image_url, headers=headers).content)

        row = list(level_dict.values()) + [goods_title, goods_price, image_url]
        df.loc[0] = row
        df.to_csv("data.csv", mode="a", header=False, index=False)
        print(f"已保存 {goods_title} 的信息")


# if __name__ == "__main__":
#     buynewjerseys(thread_count=1).start()
