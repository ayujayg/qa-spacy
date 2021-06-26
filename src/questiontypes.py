import pandas as pd
import enum

class QType(enum.Enum):
    Num = "Numerical"  #Questions asking for simple number answers, excluding temporal and monetary figures
    Temp = "Temporal" # Questions pertaining to time
    Worth = "Value" #Questions pertaining to currency
    Expl = "Description" #Questions asking for explanation
    Name = "Name" #Questions asking for name of an object or entity

class QSubj(enum.Enum):
    Pers = "Person" #Person
    Loc = "Place" #Location
    Event = "Event" #Event
    Org = "Organization" #Organization
    Thing = "Thing" #Concepts and things i.e. marine biology, COVID, space, Buddhism
    Unre = "Unresolved"

class Question:
    def __init__(self, tree=pd.DataFrame(), chunks=pd.DataFrame(), ents=pd.DataFrame()):
        self.tree = tree
        self.chunks = chunks
        self.ents = ents
        self.qclass_dict = {}
        self.create_dict()


    def create_dict(self):
        self.qclass_dict = {
            'query_term': "None",
            'root': "None",
            'object': "None",
            'subject': "None",
            'target_answer': "None",
            'subject_type': "None",
            'named_entities': "None",
            'score_dist': "None",
            'numerical': False,
            'infobox_term': "None"
        }

    def set_qclass_dict(self, query="None", root="None", object="None",
                            subject="None", target="None", sub_type="None",
                            ne="None", num = False, score_dist = [], ibt = "None"):
        self.qclass_dict['query_term'] = query
        self.qclass_dict['root'] = root
        self.qclass_dict['subject_type'] = sub_type
        self.qclass_dict['target_answer'] = target
        self.qclass_dict['subject'] = subject
        self.qclass_dict['object'] = object
        self.qclass_dict['named_entities'] = ne
        self.qclass_dict['numerical'] = num
        self.qclass_dict['score_dist'] = score_dist
        self.qclass_dict['infobox_term'] = ibt


    def add_named_entities(self):
        if not self.ents.empty:
            l = []
            for index, row in self.ents.iterrows():
                l.append((row['ENTITY'],row['LABEL']))
            self.qclass_dict['named_entities'] = l

class WhoQuestion(Question):

    def who_aux_root(self):

        rt_cond = self.tree['DEP'] == 'ROOT'
        root = self.tree[rt_cond]['WORD'].values[0]
        subject = self.chunks[self.chunks['DEP'] == 'nsubj']['BASE'].values[0]
        sd = []
        sd.append(['literal-match', subject + " " + root + " ", 1.5])
        #sd.append(['pos-match', "PROPN AUX", 0.1])
        #sd.append(['pos-match', "PRON AUX", 0.05])
        sd.append(['lemma-match', subject + " " + self.tree[rt_cond]["LEMMA"].values[0] + " ", 0.5])

        self.set_qclass_dict(query=self.chunks[self.chunks['DEP'] == 'nsubj']['CHUNK'].values[0],
                             root=root,
                             sub_type=QSubj.Pers.value,
                             target=QType.Expl.value,
                             subject=subject,
                             score_dist=sd
                             )

        self.add_named_entities()

        return self.qclass_dict

    def who_aux_possive(self):
        rt_cond = self.tree['DEP'] == 'ROOT'
        cond = self.tree['POS'] == 'PROPN'
        subject = self.chunks[self.chunks['DEP'] == 'nsubj']['BASE'].values[0]
        subj_chunk = self.chunks[self.chunks['DEP'] == 'nsubj']['CHUNK'].values[0]
        query = []

        for index, row in self.tree.loc[cond].iterrows():
            if row['WORD'] in subj_chunk:
                query.append(row['WORD'])
        query = ' '.join(query)
        sd = []
        sd.append(['literal-match', subject + " ",0.6])
        self.set_qclass_dict(query=query,
                             root=self.tree[rt_cond]['WORD'].values[0],
                             sub_type=QSubj.Pers.value,
                             target=QType.Name.value,
                             subject=subject,
                             score_dist=sd,
                             ibt=subject)

        self.add_named_entities()

        del subject,query

        return self.qclass_dict

    def who_verb_root(self):
        rt_cond = (self.tree['DEP'] == 'ROOT') & (self.tree['POS'] == 'VERB')
        root = self.tree[rt_cond]['WORD'].values[0]
        sd = []
        sd.append(['lemma-match', root + " by ", 1.0])
        sd.append(['pos-match', "NOUN AUX VERB ADP ", 0.6])
        sd.append(['literal-match', root + " ", 0.7])
        sd.append(['lemma-match',self.tree[self.tree['DEP'] == 'ROOT']['LEMMA'].values[0] + " ",0.4])

        self.set_qclass_dict(query=self.chunks[self.chunks['DEP'] == 'dobj']['CHUNK'].values[0],
                             root=root,
                             sub_type=[QSubj.Thing.value,QSubj.Event.value,QSubj.Org.value],
                             target=QType.Name.value,
                             subject=self.chunks[self.chunks['DEP'] == 'nsubj']['CHUNK'].values[0],
                             object=self.chunks[self.chunks['DEP'] == 'dobj']['CHUNK'].values[0],
                             score_dist=sd,
                             ibt=root)

        self.add_named_entities()

        return self.qclass_dict

    def who_aux_verb_root(self):
        rt_cond = (self.tree['DEP'] == 'ROOT') & (self.tree['POS'] == 'VERB')
        cond = ((self.tree['DEP'] == 'compound') & (self.tree['POS'] == 'PROPN')) | ((self.tree['DEP'] == 'nsubj') & (self.tree['POS'] == 'PROPN'))
        subject = self.chunks[self.chunks['DEP'] == 'nsubj']['CHUNK'].values[0]
        root = self.tree[rt_cond]['WORD'].values[0]
        query = []
        for index, row in self.tree.loc[cond].iterrows():
            if row['WORD'] in subject:
                query.append(row['WORD'])
        query = ' '.join(query)
        base = self.chunks[self.chunks['DEP']=='nsubj']['BASE'].values[0]
        object = self.chunks[self.chunks['DEP'] == 'dobj']['CHUNK'].values[0]
        lkp = base + " " + root
        self.set_qclass_dict(query=query,
                             root=root,
                             lkp=lkp,
                             subject=base,
                             object = object,
                             sub_type=QSubj.Pers.value,
                             target=QType.Name.value)

        self.add_named_entities()

        return self.qclass_dict

class WhatQuestion(Question):

    def what_aux_det(self):
        rt_cond = self.tree['DEP'] == 'ROOT'
        root = self.tree[rt_cond]['WORD'].values[0]
        subject = self.tree[self.tree['DEP']=='nsubj']['WORD'].values[0]
        query = self.chunks[self.chunks['DEP'] == 'nsubj']['CHUNK'].values[0]
        sd = []
        if (self.tree[self.tree['DEP'] == 'det']['LEMMA'].values[0] == 'a') and (self.tree[self.tree['DEP'] == 'ROOT']['WORD'].values[0] == 'is'):
            aquery = query + "s"
            sd.append(['literal-match', aquery + " are ", 1.0])
            sd.append(['literal-match', aquery + " ", 0.6])
        else:
            sd.append(['literal-match', query + " " + root + " ", 1.0])
            sd.append(['literal-match', query + " ", 0.6])
        
        sd.append(['lemma-match', query + " " + self.tree[self.tree['DEP'] == 'ROOT']['LEMMA'].values[0] + " ",0.8])
        self.set_qclass_dict(subject = subject, query = query,
                             root=root,sub_type=QSubj.Thing.value,
                             target=QType.Expl.value, score_dist=sd)
        return self.qclass_dict

    def what_aux_nsubj(self):
        rt_cond = self.tree['DEP'] == 'ROOT'
        root = self.tree[rt_cond]['WORD'].values[0]
        subject = self.tree[self.tree['DEP'] == 'nsubj']['WORD'].values[0]
        query = self.chunks[self.chunks['DEP'] == 'nsubj']['CHUNK'].values[0]
        sd = []
        sd.append(['literal-match',subject + " " + root + " ", 1.0])
        sd.append(['lemma-match', self.tree[self.tree['DEP'] == 'nsubj']['LEMMA'].values[0] + " be ", 0.8])
        self.set_qclass_dict(subject=subject, query=query,
                             root=root, sub_type=QSubj.Thing.value,
                             target=QType.Expl.value, score_dist=sd)
        return self.qclass_dict

    def what_aux_verb(self):
        rt_cond = self.tree['DEP'] == 'ROOT'
        root = self.tree[rt_cond]['WORD'].values[0]
        subject = self.tree[self.tree['DEP'] == 'nsubj']['WORD'].values[0]
        query = self.chunks[self.chunks['DEP'] == 'nsubj']['CHUNK'].values[0]
        sd = []
        sd.append(['literal-match',root + " is ", 1.0])
        sd.append(['literal-match',root + " ", 0.6])
        self.set_qclass_dict(subject=subject, query=query,
                             root=root, sub_type=QSubj.Thing.value,
                             target=QType.Expl.value, score_dist=sd)
        return self.qclass_dict

    def what_aux_det_prep(self):
        rt_cond = self.tree['DEP'] == 'ROOT'
        root = self.tree[rt_cond]['WORD'].values[0]
        subject = self.tree[self.tree['DEP'] == 'nsubj']['WORD'].values[0]
        query = self.chunks[self.chunks['DEP'] == 'pobj']['CHUNK'].values[0]
        sd = []
        sd.append(['literal-match', query + " ",0.3])
        sd.append(['literal-match', subject + " ",0.8])
        sd.append(['lemma-match',subject + " be ", 0.9])
        self.set_qclass_dict(subject=subject, query=query,
                             root=root, sub_type=QSubj.Thing.value,
                             target=QType.Name.value, score_dist=sd, ibt=subject)

        self.add_named_entities()

        return self.qclass_dict

class HowQuestion(Question):

    def how_acomp(self):
        rt_cond = self.tree['DEP'] == 'ROOT'
        root = self.tree[rt_cond]['WORD'].values[0]
        comp = self.tree[self.tree['DEP'] == 'acomp']['WORD'].values[0]
        subject = self.tree[self.tree['DEP'] == 'nsubj']['WORD'].values[0]
        query = self.chunks[self.chunks['DEP'] == 'nsubj']['CHUNK'].values[0]
        ibt = ''
        if comp == 'old' or comp == 'young': ibt = 'born'
        elif comp == 'tall': ibt = 'height'
        elif comp == 'wide' or comp == 'narrow': ibt = 'width'
        elif comp == 'long' or comp == 'short': ibt = 'length'
        elif comp == 'big' or comp == 'small': ibt = 'size'
        elif comp == 'deep' or comp == 'shallow': ibt = 'depth'
        sd = []
        sd.append(['literal-match', ibt + " ", 1.5])
        sd.append(['lemma-match', self.tree[self.tree['DEP']=='acomp']['LEMMA'].values[0] + " ", 0.9])
        self.set_qclass_dict(subject=subject, query=query,
                             root=root, sub_type=QSubj.Thing.value,
                             target=QType.Num.value, score_dist=sd, ibt=ibt, num=True)

        return self.qclass_dict

    def how_do_nsubj_verb(self):
        rt_cond = self.tree['DEP'] == 'ROOT'
        root = self.tree[rt_cond]['WORD'].values[0]
        subject = self.tree[self.tree['DEP'] == 'nsubj']['WORD'].values[0]
        query = self.chunks[self.chunks['DEP'] == 'nsubj']['CHUNK'].values[0]
        sd = []
        sd.append(['literal-match',query + " ", 0.7])
        sd.append(['literal-match', subject + " ", 0.4])
        sd.append(['pos-match', "NOUN VERB ", 0.1])
        self.set_qclass_dict(subject=subject, query=query,
                             root=root, sub_type=QSubj.Thing.value,
                             target=QType.Expl.value, score_dist=sd)
        return self.qclass_dict

class WhenQuestion(Question):

    def when_aux(self):
        rt_cond = self.tree['DEP'] == 'ROOT'
        root = self.tree[rt_cond]['WORD'].values[0]
        subject = self.tree[self.tree['DEP'] == 'nsubj']['WORD'].values[0]
        query = self.chunks[self.chunks['DEP'] == 'nsubj']['CHUNK'].values[0]
        ibt = 'date'
        sd = []
        sd.append(['literal-match',query + " ", 0.6])
        sd.append(['regex', r'[\s\(][12][0-9]{3}[\)\s]', 1.0])
        self.set_qclass_dict(subject=subject, query=query,
                             root=root, sub_type=QSubj.Thing.value,
                             target=QType.Temp.value, score_dist=sd, ibt=ibt)
        return self.qclass_dict

class WhereQuestion(Question):

    def where_aux_nsubj(self):
        rt_cond = self.tree['DEP'] == 'ROOT'
        root = self.tree[rt_cond]['WORD'].values[0]
        subject = self.tree[self.tree['DEP'] == 'nsubj']['WORD'].values[0]
        query = self.chunks[self.chunks['DEP'] == 'nsubj']['CHUNK'].values[0]
        ibt = 'location'
        sd = []
        sd.append(['literal-match', query + " ", 0.7])
        sd.append(['literal-match', 'north', 0.5])
        sd.append(['literal-match', 'south', 0.5])
        sd.append(['literal-match', 'east', 0.5])
        sd.append(['literal-match', 'west', 0.5])
        sd.append(['pos-match', 'ADP', 0.1])
        self.set_qclass_dict(subject=subject, query=query,
                             root=root, sub_type=QSubj.Thing.value,
                             target=QType.Name.value, score_dist=sd, ibt=ibt)
        return self.qclass_dict

class WhyQuestion(Question):

    def why_aux_nsubj_verb(self):
        rt_cond = self.tree['DEP'] == 'ROOT'
        root = self.tree[rt_cond]['WORD'].values[0]
        subject = self.tree[self.tree['DEP'] == 'nsubj']['WORD'].values[0]
        query = self.chunks[self.chunks['DEP'] == 'nsubj']['CHUNK'].values[0]
        sd = []
        sd.append(['literal-match', subject + " ", 0.5])
        sd.append(['lemma-match',self.tree[self.tree['DEP']=='ROOT']['LEMMA'].values[0] + " ", 0.6])
        self.set_qclass_dict(subject=subject, query=query,
                             root=root, sub_type=QSubj.Thing.value,
                             target=QType.Expl.value, score_dist=sd)
        return self.qclass_dict

    def why_aux_nsubj_acomp(self):
        rt_cond = self.tree['DEP'] == 'ROOT'
        root = self.tree[rt_cond]['WORD'].values[0]
        subject = self.tree[self.tree['DEP'] == 'nsubj']['WORD'].values[0]
        query = self.chunks[self.chunks['DEP'] == 'nsubj']['CHUNK'].values[0]
        sd = []
        sd.append(['literal-match', subject + " ", 0.5])
        #sd.append(['lemma-match', self.tree[self.tree['POS'] == 'ADJ']['LEMMA'].values[0] + " ", 0.6])
        sd.append(['lemma-match', self.tree[self.tree['POS'] == 'ADV']['LEMMA'].values[0] + " ", 0.6])
        self.set_qclass_dict(subject=subject, query=query,
                             root=root, sub_type=QSubj.Thing.value,
                             target=QType.Expl.value, score_dist=sd)
        return self.qclass_dict