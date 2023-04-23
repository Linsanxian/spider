# import json
# import requests
# from enum import Enum
# import fake_headers
# import os
# from time import sleep
# import re
# from bs4 import BeautifulSoup


# def html_to_text(html):
#     soup = BeautifulSoup(html, 'html.parser')
#     cleaned_text = soup.get_text()

#     return cleaned_text


# def get_headers():
#     headers = fake_headers.Headers(
#         browser="chrome",
#         os="win",
#         headers=True
#     ).generate()
#     return headers


# def create_directory(directory_name):
#     current_dir = os.getcwd()
#     new_dir = os.path.join(current_dir, directory_name)
#     os.makedirs(new_dir, exist_ok=True)
#     return new_dir


# def get_data(url, payload):
#     response = requests.request(
#         "POST", url, headers=get_headers(), data=payload)

#     if response.status_code == 200:
#         return response
#     return None


# def parse_data(datas):
#     data = []
#     for i in datas['results'][0]['hits']:
#         information = {}
#         information['name'] = i['title']
#         information['model_no'] = i['model_no']
#         information['release_date'] = i['release_date']
#         information['series'] = i['series']
#         information['price'] = i['lowest_price']
#         information['nickname'] = i['nickname']
#         information['season'] = i['season']
#         information['designer'] = i['designer']
#         information['colorway'] = i['colorway']
#         information['handle'] = i['handle']
#         information['cat_lvl0'] = i['cat_lvl0']
#         handle = i['handle']
#         res = requests.get(
#             f'https://www.kickscrew.com/products/{handle}.js').json()
#         information['description'] = html_to_text(res['description'])
#         information['images'] = [url[2:] if url.startswith(
#             '//') else url for url in res['images']]
#         information['style'] = [item.split(
#             "_")[1] for item in res['tags'] if item.startswith("STYLE_")]
#         information['toetype'] = [item.split(
#             "_")[1] for item in res['tags'] if item.startswith("TOETYPE_")]
#         information['heeltype'] = [item.split(
#             "_")[1] for item in res['tags'] if item.startswith("HEELTYPE_")]
#         information['functionality'] = [item.split(
#             "_")[1] for item in res['tags'] if item.startswith("FUNCTIONALITY_")]
#         information['solematerial'] = [item.split(
#             "_")[1] for item in res['tags'] if item.startswith("SOLEMATERIAL_")]

#         data.append(information)

#     return data


# def download_images(path, image_urls):
#     for i, url in enumerate(image_urls):
#         response = requests.get("http://" + url)
#         if response.status_code == 200:
#             with open(f"{path}/{i}.jpg", "wb") as f:
#                 f.write(response.content)
#                 print(f"Image {i} downloaded successfully.")
#         else:
#             print(f"Failed to download image {i}: {url}")


# def save_to_json(path, data):
#     import json
#     with open(f"{path}/info.json", "w") as f:
#         json.dump(data, f, indent=4)


# def save_to_csv(data):
#     import csv
#     with open(f"info.csv", "a", newline="") as f:
#         writer = csv.writer(f)
#         if f.tell() == 0:
#             writer.writerow(data.keys())

#         writer.writerow(data.values())

# if __name__ == "__main__":
#     url = "https://7ccjsevco9-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.14.3)%3B%20Browser%20(lite)%3B%20instantsearch.js%20(4.51.0)%3B%20JS%20Helper%20(3.11.3)&x-algolia-api-key=173de9e561a4bc91ca6074d4dc6db17c&x-algolia-application-id=7CCJSEVCO9"
#     classify = {
#         # "air-jordan": "62",
#         # "nike": "63",
#         # "yeezy": "23",
#         # "adidas": "41",
#         "new-balance": "62",
#         "converse": "41",
#         "asics": "41",
#         "puma": "41",
#         "ugg": "62"
#     }

#     for key, value in classify.items():
#         for i in range(int(value) + 1):
#             payload = f'{{"requests":[{{"indexName":"prod_products_sort_by_ranking_brand","params":"&hitsPerPage=16&filters=collections:{key}&page={i}"}}]}}'
#             datas = get_data(url, payload)
#             if datas.status_code == 200:
#                 print(f"获取{key}的第{i}页数据成功")
#                 print(f"开始解析")
#                 try:
#                     data = parse_data(datas.json())
#                 except Exception as e:
#                     print(f"解析{key}的第{i}页数据失败")
#                     continue
#                 print(f"解析{key}的第{i}页数据成功")
#                 print(f"开始保存")
#                 for j in data:
#                     try:
#                         path = key + "/" + j['cat_lvl0'] + "/" + j['name']
#                         create_directory(directory_name=path)
#                         image_urls = j['images']
#                         save_to_json(path, j)
#                         save_to_csv(j)
#                         print(f"开始下载图片: {j['name']}")
#                         download_images(path, image_urls)
#                     except Exception as e:
#                         print(f"保存数据失败")
#                         continue
#                 print(f"保存{key}的第{i}页数据成功")
#             else:
#                 print(f"获取{key}的第{i}页数据失败")
#                 continue

import os

# def rename_files_under_path(path):
#     # 遍历目录及子目录
#     for dirpath, dirnames, filenames in os.walk(path):
#         for filename in filenames:
#             # 构造新的文件名
#             last_dir = os.path.basename(dirpath)
#             new_name = "{}_{}".format(last_dir.replace("'", "").replace('"', ''), filename.replace("'", "").replace('"', ''))
#             # 构造新的路径
#             old_path = os.path.join(dirpath, filename)
#             new_path = os.path.join(dirpath, new_name)
#             # 重命名文件
#             os.rename(old_path, new_path)
#             print("文件已重命名为：", new_path)



# def remove_quotes_in_subdirectories(path):
#     for root, dirs, files in os.walk(path):
#         for d in dirs:
#             subdirectory = os.path.join(root, d)
#             # 去掉目录名中的单引号和双引号
#             new_subdirectory = subdirectory.replace("'", "").replace('"', '')
#             os.rename(subdirectory, new_subdirectory)


### 遍历目录及子目录，查找json文件，读取json文件，修改json文件中的内容，查询name字段，去掉name字段中的单引号和双引号，保存修改后的json文件
import json

def remove_quotes_in_json_files(path):
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith(".json"):
                json_file = os.path.join(root, f)
                with open(json_file, "r") as f:
                    data = json.load(f)
                data["name"] = data["name"].replace("'", "").replace('"', '').replace(":", "").replace("/", "")
                with open(json_file, "w") as f:
                    json.dump(data, f, indent=4)


### 遍历目录及子目录，找到所有的jpg文件,修改名称
def rename_to_index(path):
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith(".jpg"):
                ## 构造新的文件名,以_分割，取第二个元素
                last_name = f.split("_")[1]
                new_name = f.replace(f, last_name)
                old_path = os.path.join(root, f)
                new_path = os.path.join(root, new_name)
                os.rename(old_path, new_path)

## 检测目录是不是存在
def check_dir(path):
    if os.path.exists(path):
        pass
    else:
        os.makedirs(path)


### 遍历目录及子目录，找到所有的json文件，读取json文件，获取name字段，并修改当前目录下所有jpg文件名称，以name字段为前缀，移动到新路径
def raname_and_move(path):
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith(".json"):
                json_file = os.path.join(root, f)
                with open(json_file, "r") as f:
                    data = json.load(f)
                name = data["name"]
                for i in files:
                    if i.endswith(".jpg"):
                        old_path = os.path.join(root, i)
                        new_name = name + "_" + i
                        new_path = os.path.join(root, new_name)
                        os.rename(old_path, new_path)
                        
                        # print(old_path)
                        # new_path = os.path.join(root, name + "_" + i)
                        # os.rename(old_path, new_path)


                

# path = "yeezy"
# # remove_quotes_in_json_files(path)
# # rename_to_index(path)
# # raname_and_move(path)

import os

# 递归查询目录深度
def get_directory_depth(path):
    if os.path.isdir(path):
        return 1 + max(get_directory_depth(os.path.join(path, sub_path))
                       for sub_path in os.listdir(path))
    else:
        return 0

# 查找目录深度大于3的目录
def find_deep_directories(path):
    deep_directories = []
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            depth = get_directory_depth(dir_path)
            if depth > 4:
                deep_directories.append(dir_path)
    return deep_directories

# 打印目录的子目录
def print_subdirectories(path):
    for root, dirs, files in os.walk(path):
        if root != path:
            print("子目录路径：", root)

# 测试代码
if __name__ == '__main__':
    path = 'asics'
    deep_directories = find_deep_directories(path)
    if deep_directories:
        print("目录深度大于3的目录有：")
        for directory in deep_directories:
            print("目录路径：", directory)
            print("子目录：")
            print_subdirectories(directory)
            print()
    else:
        print("没有目录深度大于4的目录。")