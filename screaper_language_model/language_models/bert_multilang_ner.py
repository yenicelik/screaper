"""
    Implements a wrapper around the BERT multilingual model.
    This implements the DeepPavlov model implementation
        https://deeppavlov.ai/

    Documentation for the NER model:
        http://docs.deeppavlov.ai/en/master/features/models/ner.html

"""
from deeppavlov import configs, build_model

class ModelNER:

    def __init__(self):
        print("Loading the NER model")
        print("Config is: ")
        print(configs.ner.ner_ontonotes_bert_mult)
        self.ner_model = build_model(configs.ner.ner_ontonotes_bert_mult, download=False)

    def predict(self, queries):
        """
        :param queries: A list of documents
        :return:
        """
        assert isinstance(queries, list), type(queries)
        # Organization has pretty bad accuracy
        out = self.ner_model(queries)
        print("Query is: ", out)
        return out


model_ner = ModelNER()

if __name__ == "__main__":
    print("Using the DeepPavlov Language Model")

    model_ner.predict([
                "Bob Ross lived in Florida",
                "I like big cookies and I cannot lie"
    ])
