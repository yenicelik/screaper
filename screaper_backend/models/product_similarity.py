"""
    Part similarity based on a query
"""
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ProductSimilarity:

    def __init__(self):
        self.model = TfidfVectorizer(analyzer='char', ngram_range=(1, 4))
        self._pretrained_vectors = None
        self._documents = None

    def fit(self, documents):
        # A list of documents
        assert isinstance(documents, list), (type(documents), documents[:4])
        assert isinstance(documents[0], str), (type(documents[0]), documents[0])

        self._documents = documents
        self._pretrained_vectors = self.model.fit_transform(documents)

    def transform(self, documents):
        # A single document
        assert isinstance(documents, list), (type(documents), documents)
        for doc in documents:
            assert isinstance(doc, str), (type(doc), doc)

        assert self._pretrained_vectors is not None, self._pretrained_vectors

        return self.model.transform(documents)

    def closest_documents(self, documents):
        v0 = self._pretrained_vectors
        v1 = self.transform(documents)

        print("v0 and v1 are: ", v0.shape, v1.shape)

        similarity_matr = cosine_similarity(v0, v1).flatten()

        print("similarity matr shape is: ", similarity_matr.shape)

        # Return the items in v2 that are closest to the items in v1
        ranked_most_similar_idx = np.argsort(similarity_matr)[::-1]
        print("most similar items shape is: ", ranked_most_similar_idx.shape)

        # Return only the indices, creating the dictionary is responsibility of the algorithm
        return ranked_most_similar_idx.tolist()



model_product_similarity = ProductSimilarity()

if __name__ == "__main__":
    print("Part Similarity Starting")
