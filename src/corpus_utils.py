import re, string

class CorpusUtils:

    def __init__(self):
        self.SENTENCE = re.compile(r'(?<=[a-z0-9][\.|\?])\s')
        self.WORD = re.compile(r'\w+')

    def remove_non_alphanumeric(self, sentence):
        pattern = re.compile('\W')
        return re.sub(pattern, ' ', sentence)

    def regex_word_tokenize(self,text):
        return self.WORD.findall(text)

    def remove_duplicates(self, queries):
        seen = set()
        seen_add = seen.add
        return [x for x in queries if not (x in seen or seen_add(x))]

    def contains_answer(self, s, answer):
        matched_strings = 0
        if isinstance(s, list):
            for item in s:
                matched_strings += len(re.findall(answer, item, re.IGNORECASE))
        else:
            matched_strings = len(re.findall(answer, s, re.IGNORECASE))
        return matched_strings

    def remove_short_sents(self,data=[], min = 4):
        data = [sent for sent in data if len(sent.split()) > min]
        return data

    def clean_corpus(self, data, cutoff=0):
        corpus = []
        text = data.split('== References ==')[0]
        text = re.sub(r' \([^\(\)]+\)|\s[A-Z][\.](?![A-Z])', '',text)
        paragraphs = re.split(r'\=+.+\=+\s', text)
        for p in paragraphs:
            p = ' '.join(re.split('\n+', p))
            p = re.split(self.SENTENCE, p)
            if cutoff != 0:
                p = self.remove_short_sents(data=p,min=cutoff)
            if p:
                corpus.append(p)

        return corpus