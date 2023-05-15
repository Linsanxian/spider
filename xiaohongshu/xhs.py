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

token = ""
host = ""
page = 1


def check_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def search_params(page, token, search_id='', session_id=''):
    return {
        "keyword": "湄洲岛",
        "page": page,
        "sort": "2",
        "node_type": "1",
        "key": token,
        "search_id": search_id,
        "session_id": session_id
    }


def note_info_params(note_id, token):
    return {
        "note_id": note_id,
        "key": token,
    }


def comments_params(note_id, token, cursor):
    return {
        "note_id": note_id,
        "cursor": cursor,
        "key": token,
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
        global page

        if not data['data']['items']:
            return
        print(json.dumps(data, indent=4, ensure_ascii=False))

        for item in data['data']['items']:
            if item['model_type'] == "hot_query":
                continue
            note_id = item['id'] if item['id'] else ''

            params = note_info_params(note_id, token)
            yield feapder.Request(note_url,
                                  params=params,
                                  method="GET",
                                  callback=self.parse_note)

        has_more = data['data']['has_more']

        if has_more:
            page += 1
            search_id = data['data']['search_id']
            session_id = data['data']['session_id']

            params = search_params(page, token, search_id, session_id)

            yield feapder.Request(search_url,
                                  params=params,
                                  method="GET",
                                  callback=self.get_all_note)

    def parse_note(self, request, response):
        data = response.json

        if not data['data']:
            return

        note_id = data['data']['id']
        title = data['data']['title']
        desc = data['data']['desc']
        author = data['data']['user']['nickname']
        images_list = data['data']['images_list'] if data['data']['images_list'] else ''
        comments_count = data['data']['comments_count']
        # create_time = data['data']['time']
        create_time = datetime.fromtimestamp(data['data']['time'])

        if images_list:
            for image in images_list:
                image_url = image['url']
                fileid = image['fileid']

                yield feapder.Request(image_url,
                                      method="GET",
                                      callback=self.download_image,
                                      meta={
                                          "note_id": note_id,
                                          "fileid": fileid
                                      })

        if comments_count > 0:
            uri = "/other_api/xhs_api/note_comments/"
            url = f"{host}{uri}"

            params = comments_params(note_id, token, '')

            yield feapder.Request(url,
                                  params=params,
                                  method="GET",
                                  callback=self.parse_comments,
                                  meta={
                                      "title": title,
                                      "desc": desc,
                                      "author": author,
                                      "note_id": note_id,
                                      "create_time": create_time
                                  })

    def parse_comments(self, request, response):

        uri = "/other_api/xhs_api/note_comments/"
        url = f"{host}{uri}"

        columns = ["note_id", "title", "create_time", "author", "desc",
                   "comments", "comments_id", "comments_author"]

        df = pd.DataFrame(columns=columns)

        title = request.meta['title']
        desc = request.meta['desc']
        author = request.meta['author']
        note_id = request.params['note_id']
        create_time = request.meta['create_time']

        data = response.json

        if not data['data']['comments']:
            return

        for item in data['data']['comments']:
            comments = item['content']
            comments_id = item['id']
            comments_author = item['user']['nickname'] if item['user'] else ''

            df = df.append({
                "note_id": note_id,
                "title": title,
                "create_time": create_time,
                "author": author,
                "desc": desc,
                "comments": comments,
                "comments_id": comments_id,
                "comments_author": comments_author
            }, ignore_index=True)

        df.to_csv("xhs.csv", mode='a', header=False, index=False)

        cursor = data['data']['cursor']

        if cursor:
            params = comments_params(note_id, token, cursor)

            yield feapder.Request(url,
                                  params=params,
                                  method="GET",
                                  callback=self.parse_comments,
                                  meta={
                                      "title": title,
                                      "desc": desc,
                                      "author": author,
                                      "note_id": note_id,
                                      "create_time": create_time
                                  })

    def download_image(self, request, response):
        path = f"images/{request.meta['note_id']}"
        fileid = request.meta['fileid']
        check_dir(path)

        with open(f"{path}/{fileid}.jpg", "wb") as f:
            f.write(response.content)


if __name__ == "__main__":
    Xhs(thread_count=2).start()
