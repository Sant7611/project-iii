import re
import math
from collections import Counter, defaultdict

class SearchEngine():
    def __init__(self):
        self.documents = {}      # doc_id -> {word_counts, total_words, title}
        self.doc_freq = defaultdict(int)  # word -> how many docs contain it
        self.total_docs = 0

    def _tokenize(self,text):
        words = re.findall(r'\b[a-z]+\b', text.lower())
        return words
    
    def add_document(self,doc_id, title, content):
        text = f'{title} { content}'
        words = self._tokenize(text)
        words_count = Counter(words)

        self.documents[doc_id]={
            'counts':words_count,
            'total':len(words),
            'title':title
        }

        self.total_docs +=1

        for word in words_count:
            self.doc_freq[word] +=1

    def _tf(self, word, doc_id):
        doc = self.documents[doc_id]
        return doc['counts'].get(word,0)/ doc['total'] if doc['total'] > 0 else 0
    
    def _idf(self, word):
        df = self.doc_freq.get(word, 0)
        return math.log(self.total_docs / (df + 1)) + 1  # +1 smoothing
    
    def _tfidf(self, word, doc_id):
        return self._tf(word, doc_id) * self._idf(word)

    def search(self, query, top_n=10):
        query_words = self._tokenize(query)
        scores = {}
        
        for doc_id in self.documents:
            score = sum(self._tfidf(word, doc_id) for word in query_words)
            if score > 0:
                scores[doc_id] = score
        
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_n]

    def build_index(self, posts):
        """Rebuild the entire index from a queryset of Post objects."""
        self.documents.clear()
        self.doc_freq.clear()
        self.total_docs = 0
        
        for post in posts:
            self.add_document(post.id, post.title, post.content)
