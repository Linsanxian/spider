import flickrapi
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
import fake_headers
import json
import os

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
    
    def search_options(self, bbox, per_page=250, min_taken_date=None, max_taken_date=None):
        search_params = {
            'has_geo': 1,
            'extras': 'geo,url_z,date_taken,owner_name',
            'bbox': bbox,
            'per_page': per_page,
            'min_taken_date': min_taken_date,
            'max_taken_date': max_taken_date
        }
        return search_params

    def get_photos(self, **kwargs):
        page = 1
        total_pages = 1
        columns = ['照片ID', '照片标题', '照片URL', '经度', '纬度', '拍摄时间', '用户ID', '用户昵称']
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

                    df = pd.concat([df, pd.DataFrame({'照片ID': photo_id, 
                                                    '照片标题': photo_title, 
                                                    '照片URL': photo_url, 
                                                    '经度': latitude, 
                                                    '纬度': longitude, 
                                                    '拍摄时间': taken_time, 
                                                    '用户ID': owner_id, 
                                                    '用户昵称': owner_name}, index=[0])])

                print('第{}页数据获取完成'.format(page))
                print('------------------------------------')
                print('防止被封IP，等待5秒后继续')
                time.sleep(5)
                page += 1
            except flickrapi.exceptions.FlickrError as e:
                print('获取数据失败，等待10秒后重试')
                time.sleep(10)
                continue
            finally:
                print('------------------------------------')
                continue
        df.drop_duplicates(subset=['照片ID'], keep='first', inplace=True)

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

def write_to_csv(df, file_name):
    """
    将数据写入CSV文件
    """
    df.to_csv(file_name, index=False, encoding='utf-8')


def parse_local_json(data):
    
    min_lon = data['min_lon']
    min_lat = data['min_lat']
    max_lon = data['max_lon']
    max_lat = data['max_lat']
    bbox = "{},{},{},{}".format(min_lon, min_lat, max_lon, max_lat)

    return bbox

def check_path(path):
    """
    检查路径是否存在，如果不存在则创建
    """
    if not os.path.exists(path):
        os.makedirs(path)


if __name__ == '__main__':
    api_key='9798f96d9971877d1500cf9226ecc10b'
    api_secret='8177c97457d13aef'

    flickr = FlickrPhotos(api_key, api_secret)
    
    start_date = '2012-01-01'
    end_date = '2022-12-31'

    date_range = generate_monthly_date_range(start_date, end_date)

    ## 从本地JSON文件中读取bbox
    with open('location.json', 'r') as f:
        data = json.load(f)
    
    for key in data:
        bbox = parse_local_json(data[key])
        for date in date_range:
            print(f"正在获取{key}的{date['month']}数据")
            min_taken_date = date['start_date']
            max_taken_date = date['end_date']
            search_params = flickr.search_options(bbox=bbox, min_taken_date=min_taken_date, max_taken_date=max_taken_date)
            df = flickr.get_photos(**search_params)
            path = f"{key}/{date['month']}"
            check_path(path)
            write_to_csv(df, f"{path}/{min_taken_date}.csv")
            print(f"{key}的{date['month']}数据获取完成")
