# -*- coding: utf-8 -*-
"""
Created on 2023-05-23 20:25:26
---------
@summary:
---------
@author: admin1
"""

import feapder
import pandas as pd


class Gaode(feapder.AirSpider):

    def start_requests(self):
        url = "https://restapi.amap.com/v3/place/around"
        types_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
                      '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '22', '97', '99']
        for types in types_list:
            params = {
                "offset": "20",
                "key": "",
                "page_num": "1",
                "city": "110000",
                "extensions": "all",
                "location": "116.490748,39.965175",
                "radius": "5000",
                "types": types,
            }
            yield feapder.Request(url, params=params, method="GET", callback=self.poi_params)

    def poi_params(self, request, response):
        data = response.json

        colunms = ['name', 'max_type', 'sec_type', 'three_type', 'address',
                   'location', 'poi_id', 'pcode', 'cost', 'rating', 'tel']
        df = pd.DataFrame(columns=colunms)

        if data['count'] == '0':
            return

        for info in data['pois']:

            name = info['name']
            type_info = info['type'].split(';')
            max_type = type_info[0]
            sec_type = type_info[1]
            three_type = type_info[2]
            address = info.get('address', '')
            location = info['entr_location']
            poi_id = info['id']
            pcode = info['pcode']
            cost = info['biz_ext']['cost'] if 'cost' in info['biz_ext'] else ''
            rating = info['biz_ext']['rating'] if 'rating' in info['biz_ext'] else ''
            tel = info['tel'] if 'tel' in info['biz_ext'] else ''

            df = df.append({
                "name": name,
                "max_type": max_type,
                "sec_type": sec_type,
                "three_type": three_type,
                "address": address,
                'location': location,
                'poi_id': poi_id,
                'pcode': pcode,
                'cost': cost,
                'rating': rating,
                'tel': tel
            }, ignore_index=True)

        df.to_csv('gaode.csv', mode='a', header=False,
                  index=False, encoding='utf-8')

        params = {
            "offset": "20",
            "key": "aa164f48d5be4c3f8b84d315fc24c9b1",
            "page_num": str(int(request.params['page_num']) + 1),
            "city": "110000",
            "extensions": "all",
            "location": "116.490748,39.965175",
            "radius": "5000",
            "types": request.params['types'],
        }
        yield feapder.Request(request.url, params=params, method="GET", callback=self.poi_params)


if __name__ == "__main__":
    Gaode(thread_count=1).start()
