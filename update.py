#!/usr/bin/env python3

# Germany cities parser

# Script gets list of the Germany cities from Wikipedia and basic information
# about them: name, subject, district, population and coordinates.
# Copyright Andrey Zhidenkov, 2019 (c)

import os
import sys
import json

from lxml.html import fromstring

from parselab.parsing import BasicParser
from parselab.network import NetworkManager
from parselab.cache import FileCache

URL_ROOT = 'https://en.m.wikipedia.org'

class App(BasicParser):

    data = list()

    def __init__(self):
        self.cache = FileCache(namespace='germany-cities', path=os.environ.get('CACHE_PATH'))
        self.net = NetworkManager()

    def get_city_info(self, url):
        def get_td(th):
            td = th.xpath('./following-sibling::td[1]')
            return td[0].text_content().strip()

        def get_population(th):
            td = th.getparent().xpath('./following-sibling::tr//td[1]')
            return td[0].text_content().replace(',', '')

        info = {}

        page = self.get_page('%s%s' % (URL_ROOT, url))
        html = fromstring(page)

        th1 = html.xpath('.//table[contains(@class, "geography")]//tbody//tr//th[1]')
        info['name'] = th1[0].text_content().strip()

        geo = html.xpath('.//span[@class="geo"]')
        if geo is not None:
            info['coords'] = {'lat': geo[0].text_content().split('; ')[0],
                              'lon': geo[0].text_content().split('; ')[1]}

        for th in html.xpath('.//table[contains(@class, "geography")]//tr//th'):
            title = th.text_content().strip()

            if title == 'State':
                info['state'] = get_td(th)
            elif title == 'District':
                info['district'] = get_td(th)
            elif title.startswith('Population'):
                info['population'] = get_population(th)

        print(info)
        return info

    def run(self):
        page = self.get_page('https://en.m.wikipedia.org/wiki/List_of_cities_and_towns_in_Germany')
        html = fromstring(page)

        for a1 in html.xpath('.//table//tbody//tr//ul//li//a[1]'):
            print(a1.text_content())
            print(a1.get('href'))

            info = self.get_city_info(a1.get('href'))

            if info is not None:
                self.data.append(info)
            else:
                print("Couldn't get info")

        output = sorted(self.data, key=lambda k: k['name'])
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))

if __name__ == '__main__':
    app = App()
    app.run()
