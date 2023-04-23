import flickrapi
import json
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
import requests
import urllib.request
import os
import fake_headers
import sys


class FlickrPhotos():
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json',cache=True)
        self.flickr.cache = flickrapi.cache.SimpleCache(timeout=3600)


    def fake_header(slf):
        headers = fake_headers.Headers(
            browser="chrome",  
            os="win",  
            headers=True
        ).generate()
        
        return headers
    
    def search_options(self, tags, bbox, per_page=250, min_taken_date=None, max_taken_date=None):
        search_params = {
            'tags': tags,
            'has_geo': 1,
            'extras': 'geo,url_z,date_taken,owner_name',
            'bbox': bbox,
            'per_page': per_page,
            'min_taken_date': min_taken_date,
            'max_taken_date': max_taken_date
        }
        return search_params
    
    def filename(self, month, extension):
        return '{}.{}'.format(month, extension)

    def folder(self, folder, month):
        
        return os.path.join(folder, month)    

    def check_folder(self, folder, month):
        folder = self.folder(folder, month)
        if not os.path.exists(folder):
            os.makedirs(folder)
        return folder

    def write_to_csv(self, df, filename):
            df.to_csv(filename, index=False, encoding='utf-8')
    
    def write_to_json(self, df, filename):
        json_str = df.to_json(orient='records', force_ascii=False)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(json_str)
    
    def save_images(self, df, folder):
        for index, row in df.iterrows():
            url = row['照片URL']
            photo_id = row['照片ID']
            filename = '{}.jpg'.format(photo_id)
            filepath = os.path.join(folder, filename)
            if not os.path.exists(filepath):
                try:
                    response = requests.get(url, timeout=10,headers=self.fake_header())
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    print('图片下载成功：{}'.format(photo_id))
                except Exception as e:
                    print('图片下载失败：{}'.format(url))
            else:
                print('图片已存在：{}'.format(filepath))

    def get_photos(self, **kwargs):
        page = 1
        total_pages = 1
        columns = ['照片ID', '照片标题', '照片URL', '经度', '纬度', '拍摄时间', '用户ID', '用户昵称', '用户所在地']
        df = pd.DataFrame(columns=columns)
        while page <= total_pages:
            try:
                photos = self.flickr.photos.search(**kwargs, page=page)
                total_pages = photos['photos']['pages']
                total_photos = photos['photos']['total']
                print('正在获取{}-{}的数据'.format(kwargs['min_taken_date'],kwargs['max_taken_date']))
                print('正在获取第{}页，共{}页，共{}张照片'.format(page, total_pages, total_photos))

                for photo in photos['photos']['photo']:
                    photo_id = photo['id']
                    photo_title = photo['title']
                    photo_url = photo['url_z'] if 'url_z' in photo else ''
                    latitude = photo['latitude']
                    longitude = photo['longitude']
                    taken_time = photo['datetaken']
                    owner_id = photo['owner']
                    owner_name = photo['ownername']

                    owner_info = self.flickr.people.getInfo(user_id=owner_id)
                    owner_location = owner_info['person']['location']['_content'] if 'location' in owner_info['person'] else ''

                    df = pd.concat([df, pd.DataFrame({'照片ID': photo_id, 
                                                    '照片标题': photo_title, 
                                                    '照片URL': photo_url, 
                                                    '经度': latitude, 
                                                    '纬度': longitude, 
                                                    '拍摄时间': taken_time, 
                                                    '用户ID': owner_id, 
                                                    '用户昵称': owner_name, 
                                                    '用户所在地': owner_location}, index=[0])]).drop_duplicates(subset=['照片ID'], keep='first')

                print('第{}页数据获取完成'.format(page))
                print('------------------------------------')
                print('开始保存数据')
                csv_filename = self.filename(kwargs['min_taken_date'], 'csv')
                json_filename = self.filename(kwargs['min_taken_date'], 'json')
                self.write_to_csv(df, csv_filename)
                self.write_to_json(df, json_filename)
                floder = self.check_folder('images', kwargs['min_taken_date'])
                self.save_images(df, floder)
                print('数据保存完成')
                print('------------------------------------')
                print('防止被封IP，等待10秒后继续')
                time.sleep(10)
                page += 1
            except flickrapi.exceptions.FlickrError as e:
                print('获取数据失败，等待10秒后重试')
                time.sleep(10)
                continue
            finally:
                print('------------------------------------')
                continue

        return df

def generate_monthly_date_range(start_date, end_date):
    """
    生成指定日期范围内的所有月份，以及每个月的起始日期和结束日期，格式为YYYY-MM-DD。
    """
    date_range = []
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # 遍历每个月份
    while start_date < end_date:
        next_month = start_date + relativedelta(months=1)
        last_day_of_month = next_month - timedelta(days=1)
        date_range.append({
            'month': start_date.strftime('%Y-%m'),
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': last_day_of_month.strftime('%Y-%m-%d')
        })
        start_date = next_month

    # 添加最后一个月
    date_range.append({
        'month': end_date.strftime('%Y-%m'),
        'start_date': end_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d')
    })

    return date_range




if __name__ == '__main__':
    api_key='9798f96d9971877d1500cf9226ecc10b'
    api_secret='8177c97457d13aef'

    ## 台湾经纬度范围
    min_lon, max_lon = 119.5, 124.5
    min_lat, max_lat = 20.75, 25.5

    bbox = "{},{},{},{}".format(min_lon, min_lat, max_lon, max_lat)

    flickr = FlickrPhotos(api_key, api_secret)

    ## 起始日期和结束日期
    start_date = sys.argv[1]
    end_date = sys.argv[2]

    date_range = generate_monthly_date_range(start_date, end_date)
    for date in date_range:
        min_taken_date = date['start_date']
        max_taken_date = date['end_date']
        search_params = flickr.search_options(tags='Taiwan', bbox=bbox, min_taken_date=min_taken_date, max_taken_date=max_taken_date)
        flickr.get_photos(**search_params)
        