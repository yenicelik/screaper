import json

from flask import jsonify

from screaper_backend.application.authentication import admin_emails
from screaper_backend.application.utils import algorithm_product_similarity


def _internal_list_products(request):
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

    # Check again if this is an admin e-mail
    if request.user['email'] not in admin_emails:
        return jsonify({
            "errors": ["Permission denied (F.002)", str(request.headers)]
        }), 403

    # # Check if the api token is valid!
    # header_token = request.headers.get('token')
    # if isinstance(header_token, str):
    #     header_token = header_token.upper()

    # Make type validation
    # Calculate the location from this

    # Retrieve input string
    query = input_json["query"]

    # Pass the query through the model
    out = algorithm_product_similarity.predict(query)

    # Save into the json
    print("out items are: ", out)

    return jsonify({
        "response": out
    }), 200
