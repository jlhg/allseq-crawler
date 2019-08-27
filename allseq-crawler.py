#!/usr/bin/env python3
# import sys
# import re
# import os
import subprocess
from html.parser import HTMLParser


class ProviderListParser(HTMLParser):

    def __init__(self):
        self.provider_links = []
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr_name, attr_value in attrs:
                if attr_name == 'href' and 'https://allseq.com/providers-list' in attr_value:
                    self.provider_links.append(attr_value)

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        pass


class ProviderInfoParser(HTMLParser):

    def __init__(self):
        self.tag = None
        self.processing = None
        self.item_level = None
        self.item_parent = None
        self.provider_name = ''
        self.location = ''
        self.provider_type = ''
        self.description = ''
        self.website = ''
        self.email = ''
        self.phone = ''
        self.phone2 = ''
        self.platforms = []
        self.certifications = []
        self.sequencing_applications = []
        self.data_analysis = []
        self.species = ''
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        self.tag = tag
        if tag == 'ul':
            for attr_name, attr_value in attrs:
                if attr_name == 'class':
                    if 'provider-platforms' in attr_value:
                        self.processing = 'platforms'
                        break
                    if 'provider-keywords' in attr_value:
                        self.processing = 'certifications'
                        break
        if tag == 'li' and self.processing in ['platforms', 'certifications']:
            for attr_name, attr_value in attrs:
                if attr_name == 'class':
                    if attr_value == 'parent-item':
                        self.item_level = 'parent'
                    elif attr_value == 'child-item':
                        self.item_level = 'child'

    def handle_endtag(self, tag):
        if tag == 'ul' and self.processing in ['platforms', 'certifications']:
            self.processing = None

    def handle_data(self, data):
        if self.tag == 'th':
            if data == 'Provider Name':
                self.processing = 'provider_name'
            elif data == 'Location':
                self.processing = 'location'
            elif data == 'Type':
                self.processing = 'provider_type'
            elif data == 'Website':
                self.processing = 'website'
            elif data == 'Phone':
                self.processing = 'phone'
            elif data == 'Phone 2':
                self.processing = 'phone2'
            return

        if self.processing is not None:
            if self.processing == 'provider_name':
                self.provider_name = data
                self.processing = None
            elif self.processing == 'location':
                self.location = data
                self.processing = None
            elif self.processing == 'provider_type':
                self.provider_type = data
                self.processing = None
            elif self.processing == 'website' and self.tag == 'a':
                self.website = data
                self.processing = None
            elif self.processing == 'phone':
                self.phone = data
                self.processing = None
            elif self.processing == 'phone2':
                self.phone2 = data
                self.processing = None
            elif self.processing == 'platforms':
                if self.item_level == 'parent':
                    self.item_parent = data
                elif self.item_level == 'child':
                    self.platforms.append('-'.join([self.item_parent, data]))
            elif self.processing == 'certifications':
                if self.item_level == 'parent':
                    self.certifications.append(data)


def fetch_page(url):
    return subprocess.check_output(['wget', '-O', '-', url]).decode('utf-8')


def main():
    # request_url = 'https://allseq.com/providers/?per_page=2000'
    request_url = 'https://allseq.com/providers/?orderby=title&order_direction=ASC&per_page=2000&certifications[]=35'
    output_file = 'output.tsv'
    fo = open(output_file, 'w')
    header = [
        'Provider Name',
        'Location',
        'Type',
        # 'Description',
        'Website',
        # 'Email'
        'Phone',
        'Phone 2',
        'Platforms',
        'Certifications',
        # 'Sequencing Applications',
        # 'Data Analysis',
        # 'Species'
    ]

    fo.write('\t'.join(header))
    fo.write('\n')
    fo.flush()

    request_html = fetch_page(request_url)
    # request_html = open('test_data/provider_list.html').read()
    plparser = ProviderListParser()
    plparser.feed(request_html)
    for link in plparser.provider_links:
        provider_html = fetch_page(link)
        piparser = ProviderInfoParser()
        piparser.feed(provider_html)
        fo.write('\t'.join([
            piparser.provider_name,
            piparser.location,
            piparser.provider_type,
            piparser.website,
            piparser.phone,
            piparser.phone2,
            '; '.join(piparser.platforms),
            '; '.join(piparser.certifications),
            # '; '.join(piparser.sequencing_applications),
            # '; '.join(piparser.data_analysis),
            # piparser.species
        ]))
        fo.write('\n')
        fo.flush


if __name__ == '__main__':
    main()
