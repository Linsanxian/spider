import feapder
import json
import requests
from fake_headers import Headers
import execjs



def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json().get("proxy")


def fake_header():
    headers = Headers(
        browser="chrome",  # Generate only Chrome UA
        os="win",  # Generate ony Windows platform
        headers=True  # generate misc headers
    ).generate()

    headers['Content-Type'] = 'application/json'
    headers['referer'] = "https://bz.zzzmh.cn/"

    return headers

def decrypt(resout):
    with open(file="decrypt.js", mode="r", encoding="utf-8") as f:
        js = f.read()
    
    decrypted = execjs.compile(js).call("decrypt", resout)

    return decrypted
    


class AirSpiderDemo(feapder.AirSpider):
    def start_requests(self):
        url = "https://api.zzzmh.cn/bz/v3/getData"
        for page in range(1, 3):
            data = {
                "size": 24,
                "current": page,
                "sort": 0,
                "category": 0,
                "resolution": 0,
                "color": 0,
                "categoryId": 0,
                "ratio": 0
            }
            data = json.dumps(data, separators=(',', ':'))
            yield feapder.Request(url, data=data, method="POST", callback=self.decrypt)

    def download_midware(self, request):
        request.headers = fake_header()
        request.proxies = {"http": "http://{}".format(get_proxy())}

        return request

    def decrypt_response(self, request, response):
        result = decrypt(response.json['result'])

        return result

    # def parse(self, request, response):
    #     print(response.text)
    #     print(response)


if __name__ == "__main__":
    AirSpiderDemo(thread_count=1).start()
