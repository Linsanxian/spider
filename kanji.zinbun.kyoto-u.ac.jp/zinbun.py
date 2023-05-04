# -*- coding: utf-8 -*-
"""
Created on 2023-04-26 22:59:33
---------
@summary:
---------
@author: admin1
"""

import feapder
import pandas as pd
import os
from urllib.parse import urljoin


class Zinbun(feapder.AirSpider):
    def start_requests(self):
        url = "http://kanji.zinbun.kyoto-u.ac.jp/db-machine/imgsrv/takuhon/type_a/menu/7.html"
        yield feapder.Request(url, verify=False, method="GET")

    def proxies(self):
        proxies = {
            "http": "http://127.0.0.1:7890",
            "https": "http://127.0.0.1:7890",
        }
        return proxies

    def download_midware(self, request):
        request.proxies = self.proxies()
        request.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,zh-TW;q=0.8,ja;q=0.7",
            "Cache-Control": "max-age=0",
            "If-Modified-Since": "Sat, 11 Oct 2003 16:30:42 GMT",
            "If-None-Match": "W/\"269aa04-bcd5-3c96bd166f080\"",
            "Proxy-Connection": "keep-alive",
            "Referer": "http://kanji.zinbun.kyoto-u.ac.jp/db-machine/imgsrv/takuhon/t_menu.html",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
        }
        request.cookies = {
            "arp_scroll_position": "5450.5"
        }
        return request

    def parse(self, request, response):
        rows = response.xpath("//table/tr")

        data = []
        for row in rows[5:]:
            # id_ = row.xpath("./td[1]/div/a/text()").extract_first()
            # year = row.xpath("./td[4]/div/text()").extract_first()
            link = row.xpath("./td[1]/div/a/@href").extract_first()

            print(f"Link: {link}")

            if link:
                link = urljoin(request.url, link)

                yield feapder.Request(
                    link,
                    method="GET",
                    callback=self.parse_link
                )
            else:
                print(f"Skipping due to None link")

    def parse_link(self, request, response):
        id_ = response.xpath("//table/tr[2]/td[3]/text()").extract_first()
        image_url = response.xpath("//table/tr/td/img/@src")
        title = response.xpath("//table/tr[3]/td[3]/text()").extract_first()
        year = response.xpath("//table/tr[4]/td[3]/text()").extract_first()

        if image_url:
            image_url = image_url.extract_first()
            image_url = urljoin(request.url, image_url)

            yield feapder.Request(
                # f"http://http://kanji.zinbun.kyoto-u.ac.jp/db-machine/imgsrv/takuhon/{image_url}",
                image_url,
                method="GET",
                callback=self.download_img,
                meta={"id": id_, "title": title,
                      "year": year},
            )

    def download_img(self, request, response):
        id_ = request.meta["id"]
        title = request.meta["title"]

        year = request.meta["year"]
        img_url = request.url
        img_name = f"{id_}_{title}_{year}.jpg"
        with open(f"images/元/{img_name}", "wb") as f:
            f.write(response.content)
            print(f"download {img_name} success")


if __name__ == "__main__":
    Zinbun(thread_count=10).start()
