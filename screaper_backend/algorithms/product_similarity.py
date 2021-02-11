"""
    Product Similarity Algorithm
"""
from screaper_backend.models.product_similarity import ProductSimilarity
from screaper_backend.resources.parts_list import PartsList


class AlgorithmProductSimilarity:

    def __init__(self):

        # Import the parts list
        self.parts_list = PartsList()

        # Import the (tf-idf) language model
        self.model_tfidf = ProductSimilarity()

        # Populate the language model with the searchstring from the part_list
        self.model_tfidf.fit(self.parts_list.searchstring_list())

        # obj = {
        #     "idx": c,
        #     "manufacturer": str(company['name']),
        #     "machine": str(machine['name']),
        #     "part": str(part['name'])
        # }

    def predict(self, query):

        # Transform query into tf-idf language-model set
        ranked_most_similar_idx = self.model_tfidf.closest_documents([query])

        # Return this sorted list of items to the frontend
        out = []
        for idx, similarity_item_idx in enumerate(ranked_most_similar_idx[:100]):

            tmp = self.parts_list.id_to_dict(similarity_item_idx)
            tmp.update({"order": idx})
            del tmp['searchstring']
            out.append(tmp)

        return out


if __name__ == "__main__":
    print("Starting predictor")
    algorithm = AlgorithmProductSimilarity()
    predictions = algorithm.predict(query="BC")
    for pred in predictions:
        print("Predictions are: ", pred)
