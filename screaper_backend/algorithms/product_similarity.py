"""
    Part Similarity Algorithm
"""
import gc

from screaper_backend.models.product_similarity import ProductSimilarity
from screaper_backend.models.parts import model_parts

class AlgorithmProductSimilarity:

    def __init__(self):

        # TODO: Make this use the database, NOT the parts_list

        # Import the parts list
        # Import the (tf-idf) language model
        self.model_tfidf = ProductSimilarity()

        # Populate the language model with the searchstring from the part_list
        self.model_tfidf.fit(model_parts.searchstring_list())
        model_parts._searchstring = None  # Garbagecollect then
        gc.collect()

    def predict(self, query):

        # Transform query into tf-idf language-model set
        ranked_most_similar_idx = self.model_tfidf.closest_documents([query])

        # Return this sorted list of items to the frontend
        out = []
        for idx, similarity_item_idx in enumerate(ranked_most_similar_idx[:20]):
            print("Most similar searchstring is: ")
            print(self.model_tfidf._documents[similarity_item_idx])

            tmp = model_parts.id_to_dict(similarity_item_idx)
            tmp.update({"sequence_order": idx})
            del tmp['searchstring']
            out.append(tmp)

        return out


if __name__ == "__main__":
    print("Starting predictor")
    algorithm = AlgorithmProductSimilarity()
    predictions = algorithm.predict(query="BC")
    for pred in predictions:
        print("Predictions are: ", pred)
