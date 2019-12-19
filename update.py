#!/usr/bin/env python3

# Germany cities parser

# Script gets list of the Germany cities from Wikipedia and basic information
# about them: name, subject, district, population and coordinates.
# Copyright Andrey Zhidenkov, 2019 (c)

import os
import sys
import json
import argparse

from lxml.html import fromstring

from parselab.parsing import BasicParser
from parselab.network import NetworkManager
from parselab.cache import FileCache

URL_ROOT = 'https://en.m.wikipedia.org'

class App(BasicParser):

    data = list()

    def __init__(self):
        parser = argparse.ArgumentParser(description='Parse database export script')
        parser.add_argument('--url', help='Process only this URL', type=str, required=False)
        self.args = parser.parse_args()

        self.cache = FileCache(namespace='germany-cities', path=os.environ.get('CACHE_PATH'))
        self.net = NetworkManager()

    def get_url(self, url):
        if url.startswith('https://'):
            return url
        else:
            return '%s%s' % (URL_ROOT, url)

    def get_city_info(self, url):
        def get_td(th):
            td = th.xpath('./following-sibling::td[1]')
            return td[0].text_content().strip()

        def get_population(th):
            td = th.getparent().xpath('./following-sibling::tr//td[1]')
            return td[0].text_content().replace(',', '')

        def get_area(th):
            td = th.getparent().xpath('./following-sibling::tr//td[1]')
            return td[0].text_content().split('\xa0km')[0]

        info = {}

        page = self.get_page(self.get_url(url))

        if self.args.url:
            print(self.cache.get_cached_filename(url), file=sys.stderr)
        html = fromstring(page)

        th1 = html.xpath('.//table[contains(@class, "geography")]//tbody//tr//th[1]//div[@style="display:inline"]')
        info['name'] = th1[0].text_content().strip()

        geo = html.xpath('.//span[@class="geo"]')
        if geo is not None:
            info['coords'] = {'lat': geo[0].text_content().split('; ')[0],
                              'lon': geo[0].text_content().split('; ')[1]}

        for th in html.xpath('.//table[contains(@class, "geography")][1]//tr//th'):
            title = th.text_content().strip()

            if title == 'State':
                info['state'] = get_td(th)
            elif title == 'District':
                info['district'] = get_td(th)
            elif title.startswith('Population'):
                info['population'] = get_population(th)
            elif (title == 'Area' or title == 'Area[1]') and not 'area' in info.keys():
                # We need to consider only the first occurance of 'Area',
                # FIXME: check for 'Area[1]' is only for Berlin
                info['area'] = get_area(th)

        return info

    def run(self):
        if self.args.url is not None:
            info = self.get_city_info(self.args.url)
            print(json.dumps(info))
            sys.exit(0)

        page = self.get_page('https://en.m.wikipedia.org/wiki/List_of_cities_and_towns_in_Germany')
        html = fromstring(page)

        for a1 in html.xpath('.//table//tbody//tr//ul//li//a[1]'):

            info = self.get_city_info(a1.get('href'))

            if info is not None:
                print(info['name'], file=sys.stderr)
                self.data.append(info)
            else:
                print("Couldn't get info", file=sys.stderr)

        output = sorted(self.data, key=lambda k: k['name'])
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))

if __name__ == '__main__':
    app = App()
    app.run()
