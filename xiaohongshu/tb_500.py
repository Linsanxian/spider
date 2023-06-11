# -*- coding: utf-8 -*-
"""
Created on 2023-05-13 10:39:56
---------
@summary:
---------
@author: admin1
"""

import feapder
import pandas as pd
import os
import json
from datetime import datetime
import requests

token = ""
host = "http://52.83.181.7:8091/proxy"
page = 1


def check_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def search_params(page, token, search_id='', session_id=''):
    return {
        "keyword": "西昌阳光康旅城市",
        "page": page,
        "sort": "1",
        "node_type": "0",
        "token": token,
        "search_id": search_id,
        "session_id": session_id
    }


def note_info_params(note_id, token):
    return {
        "note_id": note_id,
        "token": token,
    }


def comments_params(note_id, token, cursor):
    return {
        "note_id": note_id,
        "cursor": cursor,
        "token": token,
    }


class Xhs(feapder.AirSpider):

    def start_requests(self):
        uri = "/other_api/xhs_api/search_note/"
        url = f"{host}{uri}"

        params = search_params(1, token)

        yield feapder.Request(url, params=params, method="GET", callback=self.get_all_note)

    def get_all_note(self, request, response):

        search_uri = "/other_api/xhs_api/search_note/"
        note_uri = "/other_api/xhs_api/note_info/"

        search_url = f"{host}{search_uri}"
        note_url = f"{host}{note_uri}"

        data = response.json

        if not data['data']['items']:
            return

        for item in data['data']['items']:
            if item['model_type'] == "hot_query":
                continue
            note_id = item['note']['id'] if item['note'] else ''

            params = note_info_params(note_id, token)
            yield feapder.Request(note_url,
                                  params=params,
                                  method="GET",
                                  callback=self.parse_note)

        has_more = data['data']['has_more']

        if has_more:
            page = request.params['page'] + 1
            search_id = data['data']['search_id']
            session_id = data['data']['session_id']

            params = search_params(page, token, search_id, session_id)

            yield feapder.Request(search_url,
                                  params=params,
                                  method="GET",
                                  callback=self.get_all_note)

    def parse_note(self, request, response):
        data = response.json

        column = [
            "note_id", "title", "desc", "author", "note_type",
        ]
        df = pd.DataFrame(columns=column)

        if not data['data']:
            return

        note_id = data['data']['data'][0]['note_list'][0]['id']
        title = data['data']['data'][0]['note_list'][0]['title']
        note_type = data['data']['data'][0]['note_list'][0]['type']
        desc = data['data']['data'][0]['note_list'][0]['desc']
        author = data['data']['data'][0]['user']['name']
        images_list = data['data']['data'][0]['note_list'][0]['images_list'] if data[
            'data']['data'][0]['note_list'][0]['images_list'] else ''

        path = f"data/{note_id}"

        df.loc[0] = [note_id, title, desc, author, note_type]
        df.to_csv("note.csv", mode='a', header=False,
                  index=False, encoding='utf-8')

        if note_type == 'video':
            video_url = data['data']['data'][0]['note_list'][0]['video']['url']
            check_dir(path)
            with open(f"{path}/{note_id}.mp4", "wb") as f:
                f.write(requests.get(video_url).content)

        if images_list:
            for image in images_list:
                image_url = image['url']
                #  取fileid的后4位作为文件名
                fileid = image['fileid'][-6:]

                check_dir(path)
                with open(f"{path}/{fileid}.jpg", "wb") as f:
                    f.write(requests.get(image_url).content)


if __name__ == "__main__":
    Xhs(thread_count=2).start()
