import json

from flask import jsonify

from screaper_backend.application.authentication import admin_emails
from screaper_backend.models.orders import model_orders


def _internal_orders_get_single(request):
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
    order_id = input_json["order_id"]

    print("User uuid and user email are: ", user_email)
    print("Order id is: ", order_id)

    order = model_orders.order_by_order_id(order_id=order_id)
    if order is None:
        print("errors", ["No corresponding orders are found!", str(request.data)])
        return jsonify({
            "errors": ["No corresponding orders are found!", str(request.data)]
        }), 400

    return jsonify({
        "response": order
    }), 200
