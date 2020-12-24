"""
    Named Entity Recognition

    Implementing the API to the DeepPavlov NER Microservice

    Returns the following set of Entity Types:
    (Relevant ones are marked by ->)
        -> PERSON : People including fictional
        -> NORP : Nationalities or religious or political groups
        -> FACILITY : Buildings, airports, highways, bridges, etc.
        -> ORGANIZATION : Companies, agencies, institutions, etc.
        -> GPE : Countries, cities, states
        -> LOCATION : Non-GPE locations, mountain ranges, bodies of water
        -> PRODUCT : Vehicles, weapons, foods, etc. (Not services)
        -> EVENT : Named hurricanes, battles, wars, sports events, etc.
        -> WORK OF ART : Titles of books, songs, etc.
        LAW : Named documents made into laws
        -> LANGUAGE : Any named language
        DATE : Absolute or relative dates or periods
        TIME : Times smaller than a day
        PERCENT : Percentage (including “%”)
        -> MONEY : Monetary values, including unit
        -> QUANTITY : Measurements, as of weight or distance
        ORDINAL : “first”, “second”
        CARDINAL : Numerals that do not fall under another type
"""
import json
import requests


class MicroserviceNER:

    def __init__(self):
        self.microservice_url = "http://127.0.0.1:5000/get-named-entities"

    def predict(self, query):
        data = json.dumps(dict(**{
            "documents": query
        }))
        print("Data is: ", data)
        response = requests.post(
            url=self.microservice_url,
            data=data,
            headers={"Content-Type": "text/json; charset=utf-8"}
        )

        # TODO: Try again on failure?

        content = response.json()
        if ("response" not in content) or (response.status_code != 200):
            raise Exception("BERT Microservice is not property working!", content)
        sentences = content["response"][0]
        named_entities = content["response"][1]

        out = []
        for sentence in named_entities:
            tmp = []
            # print("Sentence is: ", sentence)
            for x in sentence:
                # print("x is: ", x)
                if False and ("ORGANIZATION" not in x) and ("GPE" not in x) and ("LOCATION" not in x) and ("PRODUCT" not in x):
                    # print("Not included: ", x)
                    tmp.append("O")
                else:
                    # print("Included: ", x)
                    tmp.append(x)

            out.append(tmp)

        named_entities = out

        print("Content is: ", out)
        # Replace all occurences of the non-relevant items with "O"

        return sentences, named_entities


if __name__ == "__main__":
    print("Implementing the API to the DeepPavlov NER Microservice")

    model_ner = MicroserviceNER()
    model_ner.predict([
        "Bob Ross lived in Florida",
        "I like big cookies and I cannot lie"
    ])
