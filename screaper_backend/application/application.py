import json

import yaml
from flask import Flask, request, jsonify
from flask_cors import CORS

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


@application.route('/list-companies', methods=["GET", "POST"])
def list_companies():
    """
        Example request could look as follows:
        {
            "search_query": "bearings"
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

    if "search_query" not in input_json:
        return jsonify({
            "errors": ["search_query not fund!", str(input_json)]
        }), 400

    if not input_json["search_query"]:
        return jsonify({
            "errors": ["search_query empty!", str(input_json)]
        }), 400

    # # Check if the api token is valid!
    # header_token = request.headers.get('token')
    # if isinstance(header_token, str):
    #     header_token = header_token.upper()

    # Make type validation
    # Calculate the location from this
    # input_json["ip"] -> you can buy such a database for ip2location here https://www.ip2location.com/database/ip2location (pretty cheap!)

    # Retrieve input string
    search_query = input_json["search_query"]

    # Get the yaml object which is supposed to be sent back as a json response:
    with open("screaper_backend/mockups_companies.yaml", "r") as f:
        loaded_yaml_file = yaml.load(f)['companies']

    out = []
    for company in loaded_yaml_file:
        tmp = dict()
        for key in ["name", "division", "description", "verified", "type",
                    "location", "mail_address", "phone_address", "fax_address",
                    "homepage", "uuid"]:
            tmp[key] = company[key]
        out.append(tmp)

    # Fetch items closest to search query

    # Make web request to postgres server
    # out = []
    # for url, actor_item in zip(urls, actor_entity_candidates):
    #     tmp = {
    #         "url": url
    #     }
    #     tmp.update(actor_item.as_dict())
    #     tmp.pop("url_id")
    #     out.append(tmp)

    # Save into the json
    print("out items are: ", out)

    return jsonify({
        "response": out
    }), 200


@application.route('/company', methods=["GET", "POST"])
def company():
    """
        Example request could look as follows:
        {
            "company_uuid": "45fa313d-c752-46ca-a5f6-73b045ec9d02"
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

    if "company_uuid" not in input_json:
        return jsonify({
            "errors": ["company_uuid not fund!", str(input_json)]
        }), 400

    if not input_json["company_uuid"]:
        return jsonify({
            "errors": ["company_uuid empty!", str(input_json)]
        }), 400

    # # Check if the api token is valid!
    # header_token = request.headers.get('token')
    # if isinstance(header_token, str):
    #     header_token = header_token.upper()

    # Make type validation
    # Calculate the location from this
    # input_json["ip"] -> you can buy such a database for ip2location here https://www.ip2location.com/database/ip2location (pretty cheap!)

    # Retrieve input string
    company_uuid = input_json["company_uuid"]

    # Get the yaml object which is supposed to be sent back as a json response:
    with open("screaper_backend/mockups_companies.yaml", "r") as f:
        loaded_yaml_file = yaml.load(f)['companies']

    out = []
    # Load full yaml for given company
    for company in loaded_yaml_file:
        tmp = company
        if company["uuid"] == company_uuid:
            # for key in ["company-name", "company-division", "company-description", "company-verified", "company-type",
            #             "company-location", "company-mail-address", "company-phone-address", "company-fax-address",
            #             "company-homepage", "company_uuid"]:
            #     tmp[key] = company[key]
            out.append(tmp)

    # Make web request to postgres server
    # out = []
    # for url, actor_item in zip(urls, actor_entity_candidates):
    #     tmp = {
    #         "url": url
    #     }
    #     tmp.update(actor_item.as_dict())
    #     tmp.pop("url_id")
    #     out.append(tmp)

    # Save into the json
    print("out items are: ", out)

    return jsonify({
        "response": out
    }), 200


@application.route('/list-products', methods=["GET", "POST"])
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
