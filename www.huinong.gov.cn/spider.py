import feapder
import json
import requests
from time import sleep

keywords = "民政局"
max_page = 45
sleep_time = 0.5


class AirSpider(feapder.AirSpider):

    def get_http_proxy(self):
        return requests.get("http://127.0.0.1:5010/get/").json().get("proxy")

    def get_https_proxy(self):
        return requests.get("http://127.0.0.1:5010/get/", params={"type": "https"}).json().get("proxy")

    def proxies(self):
        proxies = {
            "http": "http://{}".format(self.get_http_proxy()),
            "https": "http://{}".format(self.get_https_proxy()),
        }
        return proxies

    def start_requests(self):
        url = "http://www.huinong.gov.cn/irs/front/search"
        for i in range(max_page):
            data = {
                "tenantIds": "158",
                "tenantId": "158",
                "searchWord": keywords,
                "dataTypeId": 4,
                "historySearchWords": [],
                "orderBy": "related",
                "searchBy": "all",
                "pageNo": i,
                "pageSize": 10,
                "endDateTime": "",
                "beginDateTime": "",
                "filters": [],
                "configTenantId": "19",
                "customFilter": {
                    "operator": "and",
                    "properties": [],
                    "filters": []
                },
                "sign": "b15003d6-9fb2-4cbc-d8ac-ecaeace460ea"
            }
            data = json.dumps(data, separators=(',', ':'))
            yield feapder.Request(url, data=data, verify=False, method="POST")

    def download_midware(self, request):
        request.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,zh-TW;q=0.8,ja;q=0.7",
            "Content-Type": "application/json",
            "Origin": "http://www.huinong.gov.cn",
            "Proxy-Connection": "keep-alive",
            "Referer": "http://www.huinong.gov.cn/nxsearch/search.html?code=17ccaae4d16&tenantId=158&searchWord=%E6%B0%91%E6%94%BF%E5%B1%80",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        }
        request.proxies = self.proxies()
        return request


    def validate(self, request, response):
        if response.status_code == 200:
            return True
        else:
            return False

    def parse(self, request, response):
        data = response.json
        for item in data["data"]["middle"]['list']:
            name = item["title_no_tag"]
            url = item["url"]
            if url and url.endswith(".pdf"):
                sleep(secs=sleep_time)
                yield feapder.Request(url, callback=self.download, meta={'name': name})

    def download(self, request, response):
        with open(request.meta['name'] + ".pdf", "wb") as f:
            f.write(response.content)

if __name__ == "__main__":
    AirSpider(thread_count=1).start()