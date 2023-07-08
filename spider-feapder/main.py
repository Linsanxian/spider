# -*- coding: utf-8 -*-
"""
Created on 2023-04-23 14:26:05
---------
@summary: 爬虫入口
---------
@author: admin1
"""

from feapder import ArgumentParser
from feapder import Spider
from spiders import ixigua
from spiders import gx
from spiders import jersey_kingdom
from spiders import buynewjerseys_cc


def crawl_jersey_kingdom():
    """
    球衣网站爬虫
    """
    spider = jersey_kingdom.JerseyKingdom(redis_key="jersey_kingdom:info")
    spider.start()

def crawl_ixigua():
    """
    Spider爬虫
    """
    spider = ixigua.Ixigua(redis_key="ixigua:video")
    spider.start()

def crawl_tb():
    """
    淘宝爬虫
    """
    spider = tb.Tb(redis_key="tb:info")
    spider.start()

def crawl_gx():
    """
    共鞋爬虫
    """
    spider = gx.Gx(redis_key="gx:info")
    spider.start()
    
def crawl_jd():
    """
    京东爬虫
    """
    spider = jd.Jd(redis_key="jd:info")
    spider.start()

def crawl_buynewjerseys():
    """
    www.buynewjerseys.cc
    """
    spider = buynewjerseys_cc.buynewjerseys(redis_key="buynewjerseys:info")
    spider.start()
    
if __name__ == "__main__":
    parser = ArgumentParser(description="爬虫")

    parser.add_argument(
        "--crawl_ixigua", action="store_true", help="西瓜视频爬虫", function=crawl_ixigua
    )

    parser.add_argument(
        "--crawl_tb", action="store_true", help="淘宝评论采集", function=crawl_tb
    )

    parser.add_argument(
        "--crawl_jd", action="store_true", help="京东评论采集", function=crawl_jd
    )

    parser.add_argument(
        "--crawl_gx", action="store_true", help="共鞋采集", function=crawl_gx
    )    
    parser.add_argument(
        "--crawl_qy", action="store_true", help="球衣网采集", function=crawl_jersey_kingdom
    )
    parser.add_argument(
        "--crawl_buynewjerseys", action="store_true", help="www.buynewjerseys.cc", function=crawl_buynewjerseys
    )

    parser.start()

    # main.py作为爬虫启动的统一入口，提供命令行的方式启动多个爬虫，若只有一个爬虫，可不编写main.py
    # 将上面的xxx修改为自己实际的爬虫名
    # 查看运行命令 python main.py --help
    # AirSpider与Spider爬虫运行方式 python main.py --crawl_xxx
    # BatchSpider运行方式
    # 1. 下发任务：python main.py --crawl_xxx 1
    # 2. 采集：python main.py --crawl_xxx 2
    # 3. 重置任务：python main.py --crawl_xxx 3
