import json

from flask import jsonify

from screaper_backend.application.authentication import admin_emails
from screaper_backend.models.customers import model_customers


def _internal_customers_get(request):
    try:
        input_json = json.loads(request.data, strict=False)
    except Exception as e:
        print("Request body could not be parsed!", str(e), str(request.data))
        return jsonify({
            "errors": ["Request body could not be parsed!", str(e), str(request.data)]
        }), 400

    if request.user['email'] not in admin_emails:
        return jsonify({
            "errors": ["Permission denied (F.002)", str(request.headers)]
        }), 403

    print("Got request: ", input_json)

    out = model_customers.customers()
    # Turn into one mega-dictionary per object
    out = [x for x in out]

    return jsonify({
        "response": out
    }), 200
