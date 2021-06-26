import json
import re
from corpus_utils import CorpusUtils
import spacy
from spacy import tokenizer
from spacy.lang.char_classes import ALPHA, ALPHA_LOWER, ALPHA_UPPER, CONCAT_QUOTES, LIST_ELLIPSES, LIST_ICONS
from spacy.util import compile_infix_regex
from sklearn.feature_extraction.text import TfidfVectorizer
from websocket import create_connection
from colorama import init, Style
init() # colorama needed for Windows
from colorama_ref import ColoramaRef as cr

class BertPrediction(object):

    def __init__(self, corpus = [], qinfo = {}, nlp = spacy.load('en_core_web_md')):
        self.corpus = corpus #x number of paragraphs in wikipedia article that might contain answer
        self.question = qinfo['question']
        self.qdict = qinfo['qdict']
        self._nlp = nlp
        self._tokenizer = nlp.tokenizer
        self._ws = None
        self._predicted_result = []

        self.best_paragraph = ""

        self.build()

    def tokenize(self, text):
        tokens = []
        for t in self._nlp(text):
            tokens.append(t)
        return tokens


    def add_score(self, sentence,instruction):
        doc = self._nlp(sentence)
        tokens = []
        lemmas = []
        pos = []
        for token in doc:
            tokens.append(token.text)
            lemmas.append(token.lemma_)
            pos.append(token.pos_)
        tokens = ' '.join(tokens).lower()
        lemmas = ' '.join(lemmas).lower()
        pos = ' '.join(pos)
        score = 0.0
        m = instruction[0]
        exp = instruction[1]
        weight = instruction[2]

        if m == 'literal-match':
            score = tokens.count(exp) * weight
        elif m == 'lemma-match':
            score = lemmas.count(exp) * weight
        elif m == 'pos-match':
            score = pos.count(exp) * weight
        elif m == 'regex':
            score = len(re.findall(exp,sentence)) * weight
        return score

    def score_sentence_by_score_dist(self, sentence, score_dist):
        
        score = 0.0
        for instruction in score_dist:
            score = score + self.add_score(sentence,instruction)

        return score

    def score_chunk(self, ccc, score_dist):
        total_context_score = 0
        for c in ccc:
            sentence_score = self.score_sentence_by_score_dist(c, score_dist)
            total_context_score = total_context_score + sentence_score

        return [total_context_score, ' '.join(ccc)]

    def resolve_best_context(self, paragraphs): #1
        score_dist = self.qdict['score_dist'] #2
        scored_contexts = []
        for p in paragraphs:
            current_context_chunk = []
            current_length = 0
            for i in range(len(p)):
                if (i == len(p)-1) and (current_length + len(p[i].split()) > 50):
                    scored_contexts.append(self.score_chunk(current_context_chunk, score_dist))
                    current_context_chunk = []
                    current_length = 0
                    current_context_chunk.append(p[i])
                    scored_contexts.append(self.score_chunk(current_context_chunk, score_dist))
                elif (i == len(p)-1) and (current_length + len(p[i].split()) <= 50):
                    current_context_chunk.append(p[i])
                    scored_contexts.append(self.score_chunk(current_context_chunk, score_dist))
                else:
                    if current_length + len(p[i].split()) > 50:
                        scored_contexts.append(self.score_chunk(current_context_chunk, score_dist))
                        current_context_chunk = []
                        current_length = len(p[i].split())
                        current_context_chunk.append(p[i])
                    else:
                        current_context_chunk.append(p[i])
                        current_length = current_length + len(p[i].split())


        best = sorted(scored_contexts, key=lambda x: -x[0])
        best = [best[0][1],best[1][1],best[2][1]]
        return best

    def get_squad_prediction(self,context,query):
        data = {}
        data['data'] = [None]
        data['data'][0] = {}
        data['data'][0]['title'] = "Title"
        data['data'][0]['paragraphs'] = [None]
        data['data'][0]['paragraphs'][0] = {}
        data['data'][0]['paragraphs'][0]['context'] = context.replace(',','')
        data['data'][0]['paragraphs'][0]['qas'] = [None]
        data['data'][0]['paragraphs'][0]['qas'][0] = {}
        data['data'][0]['paragraphs'][0]['qas'][0]['question'] = query
        data['data'][0]['paragraphs'][0]['qas'][0]['id'] = "1"
        json_data = json.dumps(data)

        if self._ws is None:
            try:
                self._ws = create_connection("ws://localhost:13254")
            except:
                print("bert-qa_srv connection not available")
                return

        print("Sending candidate to BERT: {}{}{}".format(cr.qcol3,context,Style.RESET_ALL))
        self._ws.send(json_data)

        result = self._ws.recv()
        json_result = json.loads(result)

        for i in range(len(json_result)):
            print("{}. {}{} ||| {} probability : {}{} {}".format(i+1,cr.qcol4, json_result[i]['text'], Style.RESET_ALL,
                                                                cr.qcol5, json_result[i]['probability'],
                                                                Style.RESET_ALL))
            if i == 2:
                break

    def build(self):
        print("\n{}{}MODULE 3a: WIKIPEDIA ARTIClE PARAGRAPHS / SQuAD{}".format(cr.qcol4, Style.BRIGHT,
                                                                                  Style.RESET_ALL))
        print("{}\"{}\"{}".format(cr.qcol1,self.question,Style.RESET_ALL))
        best = self.resolve_best_context(self.corpus)
        for candidate in best:
            self.get_squad_prediction(candidate, self.question)
        pass



class InfoboxVectors(object):
    from scipy.spatial.distance import cosine
    def __init__(self, infobox = {}, qinfo = {}, nlp = spacy.load('en_core_web_lg')):
        self.infobox = infobox
        self.qdict = qinfo['qdict']
        self.nlp = nlp
        self.ibt = self.qdict['infobox_term']
        self.best_answer = ""
        self.sorted_keys = []

        self.build()

    def build(self):
        print("\n{}{}MODULE 3b: WIKIPEDIA INFOBOX / CLOSEST WORD VECTOR{}".format(cr.qcol4, Style.BRIGHT, Style.RESET_ALL))

        for key in self.infobox.keys():
            similarity = self.nlp(self.ibt).similarity(self.nlp(key.lower()))
            self.sorted_keys.append([key, similarity])

        self.sorted_keys = sorted(self.sorted_keys, key=lambda x: -x[1])
        print("Extracted Infobox:")
        for label, value in self.infobox.items():
            print("{}{} : {}{}{}".format(cr.qcol1,label,cr.qcol3,value,Style.RESET_ALL))
        print("{}{}{}Finding value for infobox item with closest vector to: {}{}{}".format(Style.RESET_ALL,cr.qcol1, Style.BRIGHT,
                                                                                          cr.qcol2, self.ibt, Style.RESET_ALL))
        best_key = self.sorted_keys[0][0]
        best_sim = self.sorted_keys[0][1]
        best_value = self.infobox[best_key]
        print("{}Best Answer from Infobox: {}{}{}".format(cr.qcol1,cr.qcol4,best_value, Style.RESET_ALL))
        print("Key: {}{}{}, Similarity: {}{}{}".format(cr.qcol3,best_key, Style.RESET_ALL, cr.qcol5,best_sim,Style.RESET_ALL))
        pass

if __name__ == "__main__":
    from wkinfobox import WikiInfoBox
    infobox = WikiInfoBox("https://en.wikipedia.org/wiki/World_War_II").get_infobox()
    iv = InfoboxVectors(infobox=infobox)
    pass