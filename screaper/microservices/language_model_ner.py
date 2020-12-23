"""
    Named Entity Recognition

    Implementing the API to the DeepPavlov NER Microservice
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

        content = response.json()

        print("Content is: ", content)


if __name__ == "__main__":
    print("Implementing the API to the DeepPavlov NER Microservice")

    model_ner = MicroserviceNER()
    model_ner.predict([
        "Bob Ross lived in Florida",
        "I like big cookies and I cannot lie"
    ])
