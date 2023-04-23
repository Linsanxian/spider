import time
import pymysql
import gevent
from gevent import monkey
from gevent.queue import Queue
from loguru import logger
import ngender
from phone import Phone


monkey.patch_all()
size = 1000


def judge_sex(name):
    try:
        guess_result = ngender.guess(name)
        return '男' if guess_result[0] == 'male' else '女'
    except Exception as judge_sex_error:
        logger.error(f'！！！！！！！！！！ 名字：{name}，判断名字出现问题，原因：{judge_sex_error} ！！！！！！！！！！！')
        return


def get_location(phone_num):
    try:
        info = Phone().find(phone_num)  # 通过phone库查询
        return {
            'phone': info['phone'],  # 手机号
            'phone_type': info['phone_type'],  # 手机号运营商
            'province': info['province'],  # 归属地：省份
            'city': info['city'],  # 归属地，城市
            'zip_code': info['zip_code'],  # 邮政编码
        }
    except Exception as phone_error:
        logger.error(f'！！！！！！！ 手机号：{phone_num} 出现问题，原因:{phone_error} ！！！！！！！！！！')
        return {
            'phone': None,
            'phone_type': None,
            'province': None,
            'city': None,
            'zip_code': None,
        }


def process_data(item_info, data_dict):
    # 连接数据库
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='Z^@n%H7@', db='sgk_sql_data')
    with conn.cursor() as cur:
        # 处理数据
        phone_num, name, address = item_info[0], item_info[1], item_info[2]
        if data_dict.get(phone_num):
            logger.warning(f'！！！！！！！ 手机号：{phone_num}，已经存在了，字典长度为：{len(data_dict)} ！！！！！！！！')
            cur.execute('UPDATE sgk_officials SET name=%s, address=%s WHERE moblie=%s',
                              (name, address, phone_num))
            return
        else:
            data_dict[phone_num] = name
            # 获取性别、归属地
            gender = judge_sex(name)
            phone_info = get_location(phone_num)
            province = phone_info['province']
            city = phone_info['city']
            zip_code = phone_info['zip_code']
            # 加入批量插入列表
            logger.info(f'######## 手机号：{phone_num}，名字：{name}，地址：{address}，组成一条数据成功 #########')
            # 批量插入数据到目标表
            cur.execute('INSERT INTO sgk_officials (name, moblie, address, sex, area_a, area_b,'
                                  ' area_c) VALUES (%s, %s, %s, %s, %s, %s, %s) on duplicate key update name=values(name), address=values(address), sex=values(sex)',
                                  (name, phone_num, address, gender, province, city, zip_code))
            conn.commit()
            logger.info(f"手机号：{phone_num}，insert successs")
    # 关闭数据库连接
    conn.close()


def queue_data(data):
    work = Queue()
    [work.put_nowait(i) for i in data]
    return work


def crawler(data_dict):
    while not work.empty():
        item_info = work.get_nowait()
        data_list = []
        process_data(item_info, data_dict)


def gevent_task(data_dict):
    task_list = []
    for i in range(10):
        task = gevent.spawn(crawler, (data_dict))
        task_list.append(task)
    gevent.joinall(task_list)


if __name__ == '__main__':
    start_time = time.time()
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='Z^@n%H7@', db='sgk_sql_data')
    logger.info("&&&&&&&&&&&&&&&&&&&&&&& 程序开始 &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    data_dict = {}
    with conn.cursor() as cur:
        # await cur.execute('SELECT COUNT(*) FROM sgk_original')
        # total_count = (await cur.fetchone())[0]
        # logger.info(f"***********查询到{total_count}条数据***********")
        # 分页读取原始数据并处理
        cur.execute('SELECT distinct moblie, name, address FROM sgk_original LIMIT %s, %s', (60000, 10000))
        data = cur.fetchall()
    work = queue_data(data)
    gevent_task(data_dict)
    logger.info(f"程序运行时间为：{time.time() - start_time}")