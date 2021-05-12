import json

from flask import jsonify

from screaper_backend.application.utils import algorithm_product_similarity

def _external_list_products(request):
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
        print(["errors", "query not fund!", str(input_json)])
        return jsonify({
            "errors": ["query not fund!", str(input_json)]
        }), 400

    if not input_json["query"]:
        print(["errors", "query empty!", str(input_json)])
        return jsonify({
            "errors": ["query empty!", str(input_json)]
        }), 400

    # # Check if the api token is valid!
    # header_token = request.headers.get('token')
    # if isinstance(header_token, str):
    #     header_token = header_token.upper()

    # Make type validation
    # Calculate the location from this

    # Retrieve input string
    query = input_json["query"]

    # Pass the query through the model
    tmp_out = algorithm_product_similarity.predict(query)

    out = []
    for x in tmp_out:
        keys_to_delete = set()
        for key in x.keys():
            # whitelabel allowed properties
            if key not in [
                "description_de",
                "description_en",
                "id",
                "manufacturer",
                "manufacturer_abbreviation",
                "part_external_identifier",
                "sequence_order",
            ]:
                keys_to_delete.add(key)
        for key in keys_to_delete:
            del x[key]
        out.append(x)

    # Save into the json
    print("out items are: ", out)

    return jsonify({
        "response": out
    }), 200
