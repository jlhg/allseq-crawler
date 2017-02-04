#!/usr/bin/env python3
import sys
import re
import os
import subprocess
from html.parser import HTMLParser


class ProviderListParser(HTMLParser):

    def __init__(self):
        self.provier_links = []
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr_name, attr_value in attrs:
                if attr_name == 'href' and 'http://allseq.com/providers-list' in attr_value:
                    self.provier_links.append(attr_value)

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        pass


class ProviderInfoParser(HTMLParser):

    def __init__(self):
        self.processing = None
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
        # TODO: to be implemented
        pass

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        pass



def fetch_page(url):
    return subprocess.check_output(['wget', '-O', '-', url]).decode('utf-8')


def main():
    request_url = 'http://allseq.com/providers/?per_page=2000'
    output_file = 'output.tsv'
    fo = open(output_file, 'w')
    header = [
        'Provider Name',
        'Location',
        'Type',
        'Description',
        'Website',
        'Email'
        'Phone',
        'Phone 2'
        'Platforms',
        'Certifications',
        'Sequencing Applications',
        'Data Analysis',
        'Species'
    ]

    fo.write('\t'.join(header))
    fo.write('\n')
    fo.flush()

    request_html = fetch_page(request_url)
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
            '; '.join(piparser.platforms),
            '; '.join(piparser.certifications),
            '; '.join(piparser.sequencing_applications),
            '; '.join(piparser.data_analysis),
            piparser.species
        ]))
        fo.write('\n')
        fo.flush


if __name__ == '__main__':
    main()
