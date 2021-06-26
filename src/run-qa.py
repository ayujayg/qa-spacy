import argparse
import sys
import os
import multiprocessing as mp

from wkinfobox import WikiInfoBox

java_path = "C:/Program Files/Java/jdk-15.0.2/bin/java.exe"
os.environ['JAVAHOME'] = java_path

API_KEY = 'AIzaSyCNWeaQbSLwqhNm5AsjdiaFp8gZF0PHafk'

import spacy
import datetime as dt
from spacy.tokenizer import Tokenizer
from spacy.lang.char_classes import ALPHA, ALPHA_LOWER, ALPHA_UPPER, CONCAT_QUOTES, LIST_ELLIPSES, LIST_ICONS
from spacy.util import compile_infix_regex
from spacy.language import Language
from spacy.tokens import Doc


def custom_tokenizer(nlp):
    infixes = (
        LIST_ELLIPSES
        + LIST_ICONS
        + [
            r"(?<=[0-9])[+\-\*^](?=[0-9-])",
            r"(?<=[{al}{q}])\.(?=[{au}{q}])".format(
                al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES
            ),
            r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
            #r"(?<=[{a}])(?:{h})(?=[{a}])".format(a=ALPHA, h=HYPHENS),
            r"(?<=[{a}0-9])[:<>=/](?=[{a}])".format(a=ALPHA),
        ]
    )

    infix_re = compile_infix_regex(infixes)

    return Tokenizer(nlp.vocab, prefix_search=nlp.tokenizer.prefix_search,
                                suffix_search=nlp.tokenizer.suffix_search,
                                infix_finditer=infix_re.finditer,
                                token_match=nlp.tokenizer.token_match,
                                rules=nlp.Defaults.tokenizer_exceptions)

nlp = spacy.load('en_core_web_lg')

from qpreprocessing import QuestionPreprocessing
from dataextraction import TextDataExtraction
from answermatching import BertPrediction, InfoboxVectors
#parser = argparse.ArgumentParser()

#parser.add_argument('--question', dest='question', required=True, help="any question you want to ask")

#args = parser.parse_args()

question = "What is the capital of California?"
qa = QuestionPreprocessing(question=question, nlp=nlp)
qinfo = qa.export()
del qa

tde = TextDataExtraction(api_key=API_KEY,qdict=qinfo['qdict'])
infobox, corpus = tde.export()
del tde

bp = BertPrediction(corpus=corpus, qinfo=qinfo,nlp=nlp)
if infobox and qinfo['qdict']['infobox_term'] != "None":
    ib = InfoboxVectors(infobox=infobox, qinfo=qinfo, nlp=nlp)

del corpus, qinfo
