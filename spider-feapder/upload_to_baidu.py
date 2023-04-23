import subprocess
import os
import time

from concurrent.futures import ThreadPoolExecutor

def login(username, password):
    subprocess.run(["BaiduPCS-Go", "login", "-username", username, "-password", password])


def upload(local_file, remote_path):
    subprocess.run(["BaiduPCS-Go", "upload", local_file, remote_path])


def delete_local_file(local_file):
    if os.path.exists(local_file):
        os.remove(local_file)
        print(f"{local_file} 已成功删除。")
    else:
        print(f"{local_file} 文件不存在。")


def process_file(local_file, remote_file):
    # 检查文件大小
    file_size = os.path.getsize(local_file)
    if file_size <= 1024 * 1024:
        print(f"{local_file} 文件小于1M，跳过上传。")
        return

    print(f"正在上传 {local_file} 到 {remote_file}")
    upload(local_file, remote_file)

    print(f"正在删除 {local_file}")
    delete_local_file(local_file)

def upload_directory(local_directory, remote_directory, concurrent_limit):
    # with ThreadPoolExecutor(max_workers=concurrent_limit) as executor:
        for root, _, files in os.walk(local_directory):
            relative_path = os.path.relpath(root, local_directory).lstrip(".").lstrip(os.sep)

            for file in files:
                local_file = os.path.join(root, file)
                remote_file = os.path.join(remote_directory, relative_path).replace("\\", "/")
                # 使用线程池处理文件
                process_file(local_file, remote_file)



if __name__ == "__main__":

    # username = "13098209337"
    # password = "nihao123"

    # login(username, password)

    local_directory = "./video/"
    remote_directory = "video/"

    concurrent_limit = 4  # 设置并发数
    
    while True:
        upload_directory(local_directory, remote_directory, concurrent_limit)
        print("等待 60 秒后继续上传。")
        time.sleep(60)