"""
    Runs the Flask application
"""

from flask import Flask, jsonify
from flask import request

from screaper_language_model.language_models.bert_multilang_ner import model_ner

application = Flask(__name__)

@application.route('/')
def healthcheckpoint():
    return 'Multilingual BERT model up and running for Named Entity Recognition (NER)'

@application.route('/get-named-entities', methods=['GET', 'POST'])
def get_named_entities():
    """
        Example request looks as follows:
        {
            "documents": [
                "Bob Ross lived in Florida",
                "I like big cookies and I cannot lie"
            ]
        }
    :return:
    """
    try:
        req_data = request.get_json(force=True)
    except Exception as e:
        return jsonify({
            "errors": ["Input data not understood", e]
        })

    if "documents" not in req_data:
        return jsonify({
            "errors": ["Input does not contain 'documents' key", req_data]
        })

    if len(req_data["documents"]) == 0:
        return jsonify({
            "errors": ["'documents' key does not contain any data", req_data]
        })

    if not isinstance(req_data["documents"], list):
        return jsonify({
            "errors": ["'documents' key is not a list", req_data]
        })

    for x in req_data["documents"]:
        if not isinstance(x, str):
            return jsonify({
                "errors": ["'documents' key does not contain string data", x]
            })

    try:
        queries = req_data["documents"]
    except Exception as e:
        return jsonify({
            "errors": ["Other exception occured", e]
        })

    out = model_ner.predict(queries)

    return jsonify({
        "response": out
    })
