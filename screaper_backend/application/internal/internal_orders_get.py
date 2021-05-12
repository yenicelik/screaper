import json

from flask import jsonify

from screaper_backend.application.authentication import admin_emails
from screaper_backend.models.orders import model_orders


def _internal_orders_get(request):
    try:
        input_json = json.loads(request.data, strict=False)
    except Exception as e:
        print("Request body could not be parsed!", str(e), str(request.data))
        return jsonify({
            "errors": ["Request body could not be parsed!", str(e), str(request.data)]
        }), 400

    # Check again if this is an admin e-mail
    if request.user['email'] not in admin_emails:
        return jsonify({
            "errors": ["Permission denied (F.002)", str(request.headers)]
        }), 403

    print("Got request: ", input_json)

    # Get orders for this user only!
    print("User is: ", request.user)
    user_email = request.user.get("email")

    print("User uuid and user email are: ", user_email)

    out = model_orders.orders()
    # Turn into one mega-dictionary per object
    out = [x for x in out]

    print("Orders founr are: ", out)

    return jsonify({
        "response": out
    }), 200
