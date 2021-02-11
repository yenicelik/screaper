import json

import yaml
from flask import Flask, request, jsonify
from flask_cors import CORS

from screaper_backend.models.orders import model_orders
from screaper_backend.models.product_similarity import model_product_similarity

application = Flask(__name__)
CORS(application)


@application.route('/')
def healthcheckpoint():
    """
        Example request could look as follows:
        {
            "search_query": "bearings"
        }

    """
    return jsonify({
        "response": "API is up and running!"
    }), 200


@application.route('/products', methods=["GET", "POST"])
def list_products():
    """
        Example request could look as follows:
        {
            "query": "BC"
        }

    """

    try:
        input_json = json.loads(request.data, strict=False)
    except Exception as e:
        print("Request body could not be parsed!", str(e), str(request.data))
        return jsonify({
            "errors": ["Request body could not be parsed!", str(e), str(request.data)]
        }), 400

    print("Got request: ", input_json)

    if "query" not in input_json:
        return jsonify({
            "errors": ["query not fund!", str(input_json)]
        }), 400

    if not input_json["query"]:
        return jsonify({
            "errors": ["query empty!", str(input_json)]
        }), 400

    # # Check if the api token is valid!
    # header_token = request.headers.get('token')
    # if isinstance(header_token, str):
    #     header_token = header_token.upper()

    # Make type validation
    # Calculate the location from this
    # input_json["ip"] -> you can buy such a database for ip2location here https://www.ip2location.com/database/ip2location (pretty cheap!)

    # Retrieve input string
    query = input_json["query"]

    # Pass the query through the model

    out = model_product_similarity.closest_documents(query)

    # Save into the json
    print("out items are: ", out)

    return jsonify({
        "response": out
    }), 200


@application.route('/orders', methods=["GET", "POST"])
def list_orders():
    """
        Example request could look as follows:
        {
            "user_uuid": "b6347351-7fbb-406b-9b4d-4e90e9021834"
        }

    """

    try:
        input_json = json.loads(request.data, strict=False)
    except Exception as e:
        print("Request body could not be parsed!", str(e), str(request.data))
        return jsonify({
            "errors": ["Request body could not be parsed!", str(e), str(request.data)]
        }), 400

    print("Got request: ", input_json)

    if "user_uuid" not in input_json:
        return jsonify({
            "errors": ["user_uuid not fund!", str(input_json)]
        }), 400

    if not input_json["user_uuid"]:
        return jsonify({
            "errors": ["user_uuid empty!", str(input_json)]
        }), 400


    # Ignore input, and return all mockups
    query = input_json["user_uuid"]

    out = model_orders.orders()

    return jsonify({
        "response": out
    }), 200
