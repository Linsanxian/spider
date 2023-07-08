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
import hashlib
import os


## 检查路径是否存在，不存在则创建
def check_path(path):
    if not os.path.exists(path):
        os.makedirs(path)
    

def generate_unique_hash(image_url):
    # 创建MD5哈希对象
    md5 = hashlib.md5()

    # 将图片URL编码为字节流
    url_bytes = image_url.encode('utf-8')

    # 更新MD5哈希对象
    md5.update(url_bytes)

    # 获取唯一的哈希值
    unique_hash = md5.hexdigest()

    return unique_hash


class JerseyKingdom(feapder.Spider):
    
    data = {
        "https://www.jersey-kingdom.co/Men-s-NFL-Jerseys-c27/": 1680,
        "https://www.jersey-kingdom.co/Men-s-MLB-Jerseys-c28/": 882,
        "https://www.jersey-kingdom.co/Men-s-NHL-Jerseys-c4/": 562,
        "https://www.jersey-kingdom.co/Men-s-NBA-Jerseys-c17/": 420,
        "https://www.jersey-kingdom.co/Men-s-NCAA-Jerseys-c7/": 115,
        "https://www.jersey-kingdom.co/Soccer-Shirt-Kits-c25/": 214,
        "https://www.jersey-kingdom.co/Kids--Jerseys-c9/": 479,
        "https://www.jersey-kingdom.co/Women-s-Jerseys-c10/": 917
    }
    
    def generate_urls(self,data):
        urls = []
        for base_url, page_count in data.items():
            for page in range(1, page_count + 1):
                url = base_url + str(page)
                urls.append(url)
        return urls

    
    def start_requests(self):
        for url in self.generate_urls(data=self.data):
            yield feapder.Request(url, method="GET", callback=self.parse, download_midware=self.download_midware)

    # def download_midware(self, request):
    #     return request
    
    def parse(self, request, response):
        url_list = response.xpath("//div[@class='hw1']/a/@href").extract()
        
        for url in url_list:
            yield feapder.Request(url, method="GET", callback=self.parse_detail)
        

    def parse_detail(self, request, response):
        
        colume = ["level1", "level2", "level3", "level4", "goods_title", "goods_price", "image_url"]
        df = pd.DataFrame(columns=colume)
        text = response.xpath("//div[@class='bar_title_long']//a//text()").extract()
        if text:
            level1 = text[0] if len(text) > 0 else ""
            level2 = text[1] if len(text) > 1 else ""
            level3 = text[2] if len(text) > 2 else ""
            level4 = text[3] if len(text) > 3 else ""
        
        goods_title = response.xpath('//div[@class="rightpart"]/p[1]/text()').extract_first().replace('/', '')
        # goods_id = response.xpath('//div[@class="rightpart"]/p[2]/text()').extract_first().split(":")[1]
        goods_price = response.xpath('//div[@class="rightpart"]/p[3]/span/text()').extract_first().split(":")[1]
        image_url = response.xpath("//div[@id='sp1']/a/img/@src").extract_first()
        
        encode_md5 = generate_unique_hash(image_url)
        
        path = f"{level1}/{level2}/{level3}/{level4}/{goods_title}"
        check_path(path)
        with open(f"{path}/{goods_title}.jpg", "wb") as f:
            f.write(requests.get(image_url).content)
        
        df.loc[0] = [level1, level2, level3, level4, goods_title, goods_price, image_url]
        df.to_csv("data.csv", mode="a", header=False, index=False)

# if __name__ == "__main__":
#     JerseyKingdom(thread_count=10).start()