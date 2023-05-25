import requests
import json
import pandas as pd

host = "https://api.bilibili.com"

# uri = "/x/web-interface/view"
# uri = "/main/suggest"
uri = '/x/web-interface/search/all/v2'
cookie = "buvid3=C3CED153-1566-216E-90C7-1BF64FE2C16B08472infoc; i-wanna-go-back=-1; b_lsid=3F7DDA110_18842884C3D; _uuid=1B371773-38CE-E58B-291F-7F1BA46E1048708713infoc; buvid_fp=f6033aec7a769716a24c60820e5f423e; home_feed_column=5; b_nut=1684743410; CURRENT_FNVAL=4048; rpdid=|(k|~k~u)lY)0J\'uY)R~RJRuJ; innersign=0; header_theme_version=CLOSE; buvid4=1A76B55A-611F-3776-2538-A8153644267C10005-023052216-B2Y1vFpwbkgYrKm8lZ5CUg%3D%3D; SESSDATA=c57b21f7%2C1700297624%2C9bb0f%2A52; bili_jct=a98cc71da8ba5bec6acd9b1eb6fdc041; DedeUserID=266490953; DedeUserID__ckMd5=1d22bb3b4c50da7e; sid=po3fnsbe; browser_resolution=1792-414; b_ut=5; FEED_LIVE_VERSION=V8"

# 1. 获取标题

data = pd.read_csv("bilibili.csv", encoding="utf-8")
for keyword in data['title']:
    # print(keyword)

    params = {
        "search_type": "video",
        "keyword": keyword,
        "page": "1",
        "order": "totalrank",
        "duration": "0"
    }
    
    

    resp = requests.get(host + uri, params=params, headers={"cookie": cookie}).json()
    aid = resp['data']['result'][10]['data'][0]['aid']
    bv_id = resp['data']['result'][10]['data'][0]['bvid']
    title = keyword
    duration = resp['data']['result'][10]['data'][0]['duration']
    
    df = pd.DataFrame({'aid':aid,'bv_id':bv_id,'title':title,'duration':duration},index=[0])
    df.to_csv('bilibili-1.csv',mode='a',header=False,index=False,encoding='utf-8')
    
    print(aid, bv_id, title, duration)
    
    
    
    

# print(json.dumps(data, ensure_ascii=False, indent=4))


# print(json.dumps(data, ensure_ascii=False, indent=4))
