import json

import yaml
from flask import Flask, request, jsonify

application = Flask(__name__)

@application.route('/get-actor-candidate-entities', methods=["GET", "POST"])
def get_actor_candidate_entities():
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
        out = yaml.load(f)

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
