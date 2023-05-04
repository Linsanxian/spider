import feapder
import pandas as pd
import requests


class AirSpider51Job(feapder.AirSpider):

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
        url = "https://cupidjob.51job.com/open/noauth/search-pc"

        # 互联网/电子商务
        jobArea = "000000"
        hr_positions = {
            '0601': '人事总监',
            '0602': '人事经理',
            '0603': '人事主管',
            '0604': '人事专员',
            '0606': '招聘主管',
            '0607': '薪资福利经理',
            '0608': '薪资福利专员',
            '0609': '培训经理',
            '0610': '培训专员',
            '0611': 'HRBP',
            '0626': '招聘专员',
            '0627': '绩效考核经理',
            '0628': '绩效考核助理',
            '0629': '企业文化',
            '0630': '人力资源信息系统专员',
            '0635': '劳务派遣专员',
        }

        for function, gangwei in hr_positions.items():
            for page in range(1, 51):
                params = {
                    "api_key": "51job",
                    "keyword": "",
                    "searchType": "2",
                    "function": function,
                    "industry": "32",
                    "jobArea": jobArea,
                    "jobArea2": "",
                    "landmark": "",
                    "metro": "",
                    "salary": "",
                    "workYear": "",
                    "degree": "",
                    "companyType": "",
                    "companySize": "",
                    "jobType": "",
                    "issueDate": "",
                    "sortType": "0",
                    "pageNum": page,
                    "requestId": "",
                    "pageSize": "20",
                    "source": "1",
                    "accountId": "226159870",
                    "pageCode": "sou|sou|soulb"
                }
                yield feapder.Request(url, params=params, method="GET", meta={"gangwei": gangwei})

    def download_midware(self, request):
        request.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,zh-TW;q=0.8,ja;q=0.7",
            "Connection": "keep-alive",
            "From-Domain": "51job_web",
            "Origin": "https://we.51job.com",
            "Referer": "https://we.51job.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "account-id": "226159870",
            "partner": "",
            "property": "%7B%22partner%22%3A%22%22%2C%22webId%22%3A2%2C%22fromdomain%22%3A%2251job_web%22%2C%22frompageUrl%22%3A%22https%3A%2F%2Fwe.51job.com%2F%22%2C%22pageUrl%22%3A%22https%3A%2F%2Fwe.51job.com%2Fpc%2Fsearch%3Fkeyword%3D%25E8%2596%25AA%25E8%25B5%2584%26searchType%3D2%26sortType%3D0%26metro%3D%22%2C%22identityType%22%3A%22%22%2C%22userType%22%3A%22%22%2C%22isLogin%22%3A%22%E6%98%AF%22%2C%22accountid%22%3A%22226159870%22%7D",
            "sec-ch-ua": "\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"macOS\"",
            "sign": "7c763f4a61d56811a0fa3666dfea6e64fbc85e37e0c6b6d91092b92bb26fc2be",
            "user-token": "3cfb66afff3ebdcaa960ef2c7a01968564463f2a",
            "uuid": "6dd8ae1aa338da6035a36a1e75928ced"
        }
        request.cookies = {
            "sajssdk_2015_cross_new_user": "1",
            "guid": "6dd8ae1aa338da6035a36a1e75928ced",
            "nsearch": "jobarea%3D%26%7C%26ord_field%3D%26%7C%26recentSearch0%3D%26%7C%26recentSearch1%3D%26%7C%26recentSearch2%3D%26%7C%26recentSearch3%3D%26%7C%26recentSearch4%3D%26%7C%26collapse_expansion%3D",
            "acw_tc": "ac11000116824127944534252e00deec1dbb85dc0cfa54787543e43cc7b024",
            "uid": "wKhJRGRHlPuCRhjanBTAAg==",
            "sensorsdata2015jssdkcross": "%7B%22distinct_id%22%3A%22226159870%22%2C%22first_id%22%3A%22187b79dead0bed-0647eb3602634f4-1d525634-2073600-187b79dead14e5%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTg3Yjc5ZGVhZDBiZWQtMDY0N2ViMzYwMjYzNGY0LTFkNTI1NjM0LTIwNzM2MDAtMTg3Yjc5ZGVhZDE0ZTUiLCIkaWRlbnRpdHlfbG9naW5faWQiOiIyMjYxNTk4NzAifQ%3D%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%22226159870%22%7D%2C%22%24device_id%22%3A%22187b79dead0bed-0647eb3602634f4-1d525634-2073600-187b79dead14e5%22%7D",
            "search": "jobarea%7E%60%7C%21recentSearch0%7E%60000000%A1%FB%A1%FA000000%A1%FB%A1%FA0627%A1%FB%A1%FA32%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA2%A1%FB%A1%FA1%7C%21recentSearch1%7E%60000000%A1%FB%A1%FA000000%A1%FB%A1%FA0607%A1%FB%A1%FA32%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA2%A1%FB%A1%FA1%7C%21recentSearch2%7E%60000000%A1%FB%A1%FA000000%A1%FB%A1%FA0610%A1%FB%A1%FA32%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA2%A1%FB%A1%FA1%7C%21recentSearch3%7E%60000000%A1%FB%A1%FA000000%A1%FB%A1%FA0606%A1%FB%A1%FA32%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA2%A1%FB%A1%FA1%7C%21recentSearch4%7E%60000000%A1%FB%A1%FA000000%A1%FB%A1%FA0603%A1%FB%A1%FA32%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA2%A1%FB%A1%FA1%7C%21",
            "JSESSIONID": "E684026DA29D14BB2F876EF9A26CD836"
        }
        request.proxies = self.proxies()
        return request

    def parse(self, request, response):
        data = response.json
        if not data['resultbody']['job']['items']:
            return
        # 使用pandas进行数据处理
        df = pd.DataFrame(data['resultbody']['job']['items'])
        df['岗位'] = request.meta.get('gangwei')
        selected_columns = ['jobName', 'jobAreaString', 'provideSalaryString','companyTypeString','companySizeString','fullCompanyName','companyHref','workYearString','degreeString','岗位']
        filtered_df = df[selected_columns]
        
        # 保存数据
        filtered_df.to_csv('51job.csv', mode='a', header=False,
                  index=False, encoding='utf-8')


if __name__ == "__main__":
    AirSpider51Job(thread_count=3).start()
