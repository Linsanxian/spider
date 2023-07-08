import requests
import json

# staffid 医生id 刘鉴 3131
staffid = "3130"
book_date = "2023-6-30"
uoid = "o1IpX4wEyClFO3dZ-Pfc_Q1q65_o"


def headers():
    headers = {
        "token": 'd2046714c6fca77f2590f56b1812052e',
        "referer": "https://servicewechat.com/wx9aecb4c053ba8233/62/page-frame.html",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 MicroMessenger/6.8.0(0x16080000) NetType/WIFI MiniProgramEnv/Mac MacWechat/WMPF XWEB/30515"
    }

    return headers


def get_book_list():
    url = "https://www.hongshanhis.com/wechat/api2/hsbdoctor"
    params = {
        "hospitalCode": "62837219",
        "branchid": "1526",
        "date": book_date,
        "uoid": uoid
    }
    response = requests.get(url, params=params)

    return response.json()


def get_doctor_book_list(staffid):
    url = "https://www.hongshanhis.com/wechat/api2/schedule"
    params = {
        "hospitalCode": "62837219",
        "branchId": "1526",
        "staffid": staffid,
        "uoid": uoid
    }
    response = requests.get(url, params=params, headers=headers())

    return response.json()


def add_book(staffid):
    datas = get_doctor_book_list(staffid)['data']
    try:
        for data in datas:
            if data['bookTotal'] > 0:
                print("有号，速抢！！！")
            url = "https://www.hongshanhis.com/wechat/api2/bookadd"

            payload = "{\n    \"memberId\": 57453,\n    \"doctorId\": 3130,\n    \"branchId\": \"1526\",\n    \"visitTime\": \"2023-06-28\",\n    \"hospitalCode\": \"62837219\",\n    \"visitTimeRange\": \"09:00-12:00\",\n    \"uoid\": \"o1IpX4wEyClFO3dZ-Pfc_Q1q65_o\"\n}"
            headers = {
            'Accept': 'application/json',
            'referer': 'https://servicewechat.com/wx9aecb4c053ba8233/62/page-frame.html',
            'xweb_xhr': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 MicroMessenger/6.8.0(0x16080000) NetType/WIFI MiniProgramEnv/Mac MacWechat/WMPF XWEB/30515',
            'token': 'd2046714c6fca77f2590f56b1812052e',
            'Content-Type': 'application/json;charset=UTF-8',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh',
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            print(response.text)

    except:
        return "获取信息失败"


if __name__ == "__main__":
    print(add_book(staffid))
