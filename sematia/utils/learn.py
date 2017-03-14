from .. import app
from . import log
from sklearn.feature_extraction.text import CountVectorizer
#from sklearn.feature_extraction.text import TfidfVectorizer
#from sklearn.metrics.pairwise import cosine_similarity
#from scipy.cluster.hierarchy import ward, dendrogram
#import matplotlib.pyplot as plt
from io import BytesIO

log = log.Log

class Learn():
   

    @staticmethod
    def bag_of_words(data):
        vectorizer = CountVectorizer(analyzer = "word",   \
            tokenizer = None,    \
            preprocessor = None, \
            stop_words = None,   \
            max_features = 5000) 

        features = vectorizer.fit_transform(data)

    @staticmethod
    def tf_idf_vectorize(data):

        #define vectorizer parameters
        tfidf_vectorizer = TfidfVectorizer(max_df=0.8, max_features=200000,
                                         min_df=0.2, stop_words=None,
                                         use_idf=True, tokenizer=None, ngram_range=(1,3))

        tfidf_matrix = tfidf_vectorizer.fit_transform(data) #fit the vectorizer to synopses

        dist = 1 - cosine_similarity(tfidf_matrix)

        return dist

    @staticmethod
    def hierarchical_clustering(dist, titles):
        return ''
        """
        linkage_matrix = ward(dist) #define the linkage_matrix using ward clustering pre-computed distances

        fig, ax = plt.subplots(figsize=(15, 20)) # set size
        ax = dendrogram(linkage_matrix, orientation="right", labels=titles);

        plt.tick_params(\
            axis= 'x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom='off',      # ticks along the bottom edge are off
            top='off',         # ticks along the top edge are off
            labelbottom='off')

        plt.tight_layout() #show plot with tight layout

        buf = BytesIO()
        plt.savefig(buf)
        buf.seek(0)
        return buf
        """
