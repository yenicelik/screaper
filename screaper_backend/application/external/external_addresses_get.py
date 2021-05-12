import json

from flask import jsonify

from screaper_backend.models.customers import model_customers


def _external_addresses_get(request):
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
    user_uuid = input_json["user_uuid"]

    # TODO: Modify this to return the addresses, not the customers
    out = model_customers.customers()


    # Turn into one mega-dictionary per object
    out = [x for x in out]

    return jsonify({
        "response": out
    }), 200
