import json

from flask import Flask, request, jsonify

from screaper_resources.resources.db import Database

application = Flask(__name__)
database = Database()

# TODO: Move this into some underlying function somewhere

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
    urls, actor_entity_candidates = database.get_all_actor_entity_candidates()

    # Fetch items closest to search query

    # Make web request to postgres server
    out = []
    for url, actor_item in zip(urls, actor_entity_candidates):
        tmp = {
            "url": url
        }
        tmp.update(actor_item.as_dict())
        tmp.pop("url_id")
        out.append(tmp)

    # Save into the json
    print("out items are: ", out[:5])

    return jsonify({
        "response": out
    }), 200
