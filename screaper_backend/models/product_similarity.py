"""
    Product similarity based on a query
"""
import yaml
import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ProductSimilarity:

    def _prepare_mockup_documents(self):
        # Get the yaml object which is supposed to be sent back as a json response:
        with open("/Users/david/screaper/screaper_backend/mockups_products.yaml", "r") as f:
            loaded_yaml_file = yaml.load(f, Loader=yaml.Loader)['companies']

        # Turn this into a flat list

        out = []
        # Load full yaml for given company
        c = 0
        for company in loaded_yaml_file:
            for machine in company['machines']:
                for part in machine['parts']:
                    obj = {
                        "idx": c,
                        "company": str(company['name']),
                        "machine": str(machine['name']),
                        "part": str(part['name'])
                    }
                    out.append(obj)
                    c += 1

        self.df = pd.DataFrame(out)
        self.df['text'] = self.df['company'] + " " + self.df['machine'] + " " + self.df['part']

    def __init__(self):
        self.model = TfidfVectorizer(analyzer='char', ngram_range=(1, 4))
        self._pretrained_vectors = None

        self._prepare_mockup_documents()
        self.fit(self.df['text'].tolist())

    def fit(self, documents):
        # A list of documents
        assert isinstance(documents, list), (type(documents), documents[:4])
        assert isinstance(documents[0], str), (type(documents[0]), documents[0])

        self._pretrained_vectors = self.model.fit_transform(documents)

    def transform(self, document):
        # A single document
        assert isinstance(document, str), (type(document), document)

        assert self._pretrained_vectors is not None, self._pretrained_vectors

        return self.model.transform([document])

    def closest_documents(self, documents):
        v0 = self._pretrained_vectors
        v1 = self.transform(documents)

        print("v0 and v1 are: ", v0.shape, v1.shape)

        similarity_matr = cosine_similarity(v0, v1).flatten()

        print("similarity matr shape is: ", similarity_matr.shape)

        # Return the items in v2 that are closest to the items in v1
        most_similar_items = np.argsort(similarity_matr)[::-1]
        print("most similar items shape is: ", most_similar_items.shape)

        # Return this sorted list of items to the frontend
        out = []
        for new_order, similari_item_idx in enumerate(most_similar_items):
            tmp = self.df[self.df["idx"] == similari_item_idx].to_dict('records')[0]
            tmp.update({"order": new_order})
            del tmp['text']
            out.append(tmp)

        return out

model_product_similarity = ProductSimilarity()

if __name__ == "__main__":
    print("Product Similarity Starting")
