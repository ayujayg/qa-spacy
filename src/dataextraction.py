import logging
from urllib.parse import urlparse, urlencode
from urllib.request import urlopen
from os.path import splitext
import wikipedia as wk
import json
import re
from wkinfobox import WikiInfoBox
from corpus_utils import CorpusUtils

from colorama import init, Style
init() # colorama needed for Windows
from colorama_ref import ColoramaRef as cr

class TextDataExtraction(object):

    def __init__(self, api_key= None, qdict = {} ):
        self.api_key = api_key
        self.qdict = qdict
        self.params = {}
        self.query = qdict['query_term']
        self.max_results = 5

        self.url = ""
        self.response = None
        self.resp_dict = {}
        self.best_url = []
        self.corpus = []
        self.infobox = {}

        self.cu = CorpusUtils()
        self.build()

    def setup_client(self):
        service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
        self.params = {
            'query': self.query,
            'limit': self.max_results,
            'indent': True,
            'key': self.api_key
        }

        self.url = service_url + '?' + urlencode(self.params)

    def request_response(self):
        self.response = json.loads(urlopen(self.url).read())
        for item in self.response['itemListElement']:
            if 'detailedDescription' in item['result']:
                self.best_url.append(item['result']['detailedDescription']['url'])
            else:
                break
        #print(self.best_url)

    def resolve_q_entity(self):
        entity = self.qdict['subject_type']
        self.params['types'] = entity

    def get_infobox(self,url):
        ib = WikiInfoBox(url)
        return ib.get_infobox()

    def get_corpus(self, link):
        link = link.split('/')
        article = link[-1]
        article = re.sub(r'[_]', ' ', article)

        data = wk.page(title=article, auto_suggest=False).content
        self.corpus = self.cu.clean_corpus(data=data,cutoff=5)

    def build(self):
        print("\n{}{}MODULE 2: GOOGLE KG / WIKIPEDIA DATA EXTRACTION{}".format(cr.qcol4,Style.BRIGHT, Style.RESET_ALL))
        print("Search query: {}{}{}{}".format(cr.qcol3, Style.BRIGHT, self.query, Style.RESET_ALL))
        print("{}{}Collecting Wikipedia links from highest scoring responses{}".format(cr.qcol1, Style.BRIGHT, Style.RESET_ALL))
        self.resolve_q_entity()
        self.setup_client()
        self.request_response()
        self.best_url = self.best_url[0]
        print("{}{}Best article:\n{}{}\n".format(cr.qcol1, Style.BRIGHT,self.best_url,Style.RESET_ALL))
        self.infobox = self.get_infobox(self.best_url)

        self.get_corpus(self.best_url)
        print("Extracted {}{}{} candidate paragraphs from highest scoring article.\n".format(cr.qcol3,len(self.corpus), Style.RESET_ALL))

    def export(self):
        return self.infobox, self.corpus



