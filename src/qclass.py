import enum
import pandas as pd
from questiontypes import Question, WhoQuestion, WhatQuestion, WhenQuestion, WhyQuestion, WhereQuestion, HowQuestion

class QClassifier(object):

    def __init__(self, tree, noun_chunks, ents):
        self.tree = tree
        self.chunks = noun_chunks
        self.ents = ents
        self.query_dict = {}

        self.question = Question()

    def classify(self):

        def who():
            self.question = WhoQuestion(tree=self.tree, chunks=self.chunks, ents=self.ents)
            row = self.tree.loc[(self.tree['DEP'] == 'ROOT') & (self.tree['POS'] == 'VERB')]
            if row.empty:
                row = self.tree.loc[self.tree['DEP'] == 'poss']

                if row.empty:
                    self.query_dict = self.question.who_aux_root()
                    return self.query_dict

                else:
                    self.query_dict = self.question.who_aux_possive()
                    return self.query_dict

            elif row.index.values.tolist()[0] == 1:
                self.query_dict = self.question.who_verb_root()
                return self.query_dict

                #who_verb_root
            elif row.index.values.tolist()[0] != 1:
                self.query_dict = self.question.who_aux_verb_root()
                return self.query_dict
                #who_aux_verb_root

        def what():
            self.question = WhatQuestion(tree=self.tree, chunks=self.chunks, ents=self.ents)
            row = self.tree.loc[(self.tree['DEP'] == 'ROOT') & (self.tree['POS'] == 'VERB')]
            if row.empty:
                row = self.tree.loc[self.tree['DEP'] == 'prep']
                if row.empty:
                    row = self.tree.loc[self.tree['DEP'] == 'det']
                    if row.empty:
                        self.query_dict = self.question.what_aux_nsubj()
                        return self.query_dict
                    else:
                        self.query_dict = self.question.what_aux_det()
                        return self.query_dict
                else:
                    self.query_dict = self.question.what_aux_det_prep()
                    return self.query_dict
                pass
            else:
                self.query_dict = self.question.what_aux_verb()
                return self.query_dict

        def how():
            self.question = HowQuestion(tree=self.tree, chunks=self.chunks, ents=self.ents)
            row = self.tree.loc[(self.tree['DEP'] == 'ROOT') & (self.tree['POS'] == 'VERB')]
            if row.empty:
                self.query_dict = self.question.how_acomp()
                return self.query_dict
            else:
                self.query_dict = self.question.how_do_nsubj_verb()
                return self.query_dict
            pass

        def when():
            self.question = WhenQuestion(tree=self.tree, chunks=self.chunks, ents=self.ents)
            self.query_dict = self.question.when_aux()
            return self.query_dict

        def where():
            self.question = WhereQuestion(tree=self.tree, chunks=self.chunks, ents=self.ents)
            self.query_dict = self.question.where_aux_nsubj()
            return self.query_dict

        def why():
            self.question = WhyQuestion(tree=self.tree, chunks=self.chunks, ents=self.ents)
            row = self.tree.loc[(self.tree['DEP'] == 'ROOT') & (self.tree['POS'] == 'VERB')]
            if row.empty:
                self.query_dict = self.question.why_aux_nsubj_acomp()
                return self.query_dict
            else:
                self.query_dict = self.question.why_aux_nsubj_verb()
                return self.query_dict


        switch_type = {
            "Who": who,
            "What": what,
            "How": how,
            "When": when,
            "Where": where,
            "Why": why,

        }
        q = self.tree['WORD'].iloc[0]

        func = switch_type.get(q, "none")
        return func()




        self.QSubj = switch_so[self.sj[1]]
        for x in switch_type:
            if self.doc.tokens[0].text == x.casefold():
                self.QType = switch_type[self.doc.tokens[0].text]



        return root, context, subject




