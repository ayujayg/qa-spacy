import spacy
import enum
import pandas as pd
from tabulate import tabulate
from qclass import QClassifier
from colorama import init, Style
init()
from colorama_ref import ColoramaRef as cr




class QuestionPreprocessing(object):
    pd.set_option("display.max_rows", None, "display.max_columns", None, "display.width", 1000, "display.colheader_justify", "center")

    def __init__(self, question, nlp = spacy.load('en_core_web_sm')):

        self.nlp = nlp #Load spacy's pre-trained large-sized model for the english language complete with word vectors
        self.doc = self.nlp(question) #Document containing the bare tokens within the question


        self.noun_chunks = pd.DataFrame(columns=["CHUNK", "BASE", "DEP"]) #partitioned noun phrases
        self.ents = pd.DataFrame(columns=["ENTITY","LABEL"]) #named entities
        self.dep_tree = pd.DataFrame(columns=["WORD","LEMMA","DEP","POS",'TAG',"PARENT","PARENT POS","CHILDREN"]) #dependency tree with children

        self.raw_q = question
        self.qdict = {}

        self.build()

    def gather_noun_chunks(self):
        for chunk in self.doc.noun_chunks:
            self.noun_chunks.loc[len(self.noun_chunks.index)] = [chunk.text, chunk.root.text, chunk.root.dep_]

    def create_tree_pos_tags(self):
        for token in self.doc:
            self.dep_tree.loc[len(self.dep_tree.index)] = [token.text,token.lemma_, token.dep_, token.pos_,token.tag_, token.head.text, token.head.pos_,
                                                       str([child for child in token.children])

                                                       ]
        self.root_verb = self.dep_tree.loc[self.dep_tree['DEP'] == 'ROOT']['WORD'].values[0]

    def gather_named_entities(self):
        for ent in self.doc.ents:
            self.ents.loc[len(self.ents.index)] = [ent.text, ent.label_]

    def classify(self):
        return QClassifier(self.dep_tree,self.noun_chunks,self.ents).classify()

    def print(self, title, id):
        print("{}{}{}".format(cr.qcol1, title, Style.RESET_ALL))
        if id == 'dep':
            print(tabulate(self.dep_tree, headers='keys', tablefmt='presto'))

        elif id == 'nc':
            print(tabulate(self.noun_chunks, headers='keys', tablefmt='presto'))
        elif id == 'ent':
            print(tabulate(self.ents, headers='keys', tablefmt='presto'))
        print("\n")

    def build(self):

        print("{}{}MODULE 1: QUESTION PRE-PROCESSING AND QUERY GENERATION{}".format(cr.qcol4,Style.BRIGHT, Style.RESET_ALL))
        print("Question: {}{}{}{}".format(cr.qcol3, Style.BRIGHT, self.raw_q, Style.RESET_ALL))

        self.create_tree_pos_tags()
        self.gather_noun_chunks()
        self.gather_named_entities()

        self.print("DEPENDENCY TREE", 'dep')
        self.print("NOUN CHUNKS", 'nc')
        self.print("NAMED ENTITIES", 'ent')

        self.qdict = self.classify()
        self.sophisticate_query()

        print("Root verb: {}{}{}, Object: {}{}{}, Subject: {}{}{}\nAnswer Type: {}{}{}, Question is about: {}{}{}, Named Entities: {}{}{} \nBest Query Term: {}{}{} Weighted Score Distribution: {}{}{}".format(
            cr.qcol3, self.qdict['root'], Style.RESET_ALL,
            cr.qcol3, self.qdict['object'], Style.RESET_ALL,
            cr.qcol3, self.qdict['subject'], Style.RESET_ALL,
            cr.qcol4, self.qdict['target_answer'], Style.RESET_ALL,
            cr.qcol4, self.qdict['subject_type'], Style.RESET_ALL,
            cr.qcol3, self.qdict['named_entities'], Style.RESET_ALL,
            cr.qcol2, self.qdict['query_term'], Style.RESET_ALL,
            cr.qcol2, self.qdict['score_dist'], Style.RESET_ALL
        ))

    def sophisticate_query(self):
        if self.qdict['query_term'].startswith("the "):
            self.qdict['query_term'] = self.qdict['query_term'][len("the "):]

    def export(self):
        exp = {
            'question':self.raw_q,
            'qdict': self.qdict
        }
        return exp

if __name__ == "__main__":
    #q1 = QuestionPreprocessing("Who is Dave Chapelle?")
    # q2 = QuestionPreprocessing("Who did Elon Musk marry?")
    #q3 = QuestionPreprocessing("Who are Michelle Obama's daughters?")
    #q4 = QuestionPreprocessing("Who won the superbowl?")
    #q5 = QuestionPreprocessing("Who is the CEO of Microsoft?")
    pass