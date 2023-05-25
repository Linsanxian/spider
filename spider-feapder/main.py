# -*- coding: utf-8 -*-
"""
Created on 2023-04-23 14:26:05
---------
@summary: 爬虫入口
---------
@author: admin1
"""

from feapder import ArgumentParser

from spiders import ixigua
# from spiders import xhs
from spiders import tb
from spiders import jd

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
    
def crawl_jd():
    """
    京东爬虫
    """
    spider = jd.Jd(redis_key="jd:info")
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

    # parser.add_argument(
    #     "--crawl_xhs",
    #     type=int,
    #     nargs=1,
    #     help="小红书评论采集, 1:下发任务,2:采集,3:重置任务",
    #     choices=[1, 2, 3],
    #     function=crawl_xhs,
    # )

    parser.start()

    # main.py作为爬虫启动的统一入口，提供命令行的方式启动多个爬虫，若只有一个爬虫，可不编写main.py
    # 将上面的xxx修改为自己实际的爬虫名
    # 查看运行命令 python main.py --help
    # AirSpider与Spider爬虫运行方式 python main.py --crawl_xxx
    # BatchSpider运行方式
    # 1. 下发任务：python main.py --crawl_xxx 1
    # 2. 采集：python main.py --crawl_xxx 2
    # 3. 重置任务：python main.py --crawl_xxx 3
