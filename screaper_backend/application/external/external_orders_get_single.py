import json

from flask import jsonify

from screaper_backend.models.orders import model_orders


def _external_orders_get_single(request):
    try:
        input_json = json.loads(request.data, strict=False)
    except Exception as e:
        print("Request body could not be parsed!", str(e), str(request.data))
        return jsonify({
            "errors": ["Request body could not be parsed!", str(e), str(request.data)]
        }), 400

    print("Got request: ", input_json)

    # Get orders for this user only!
    print("User is: ", request.user)
    user_email = request.user.get("email")
    order_id = input_json["order_id"]

    print("User uuid and user email are: ", user_email)
    print("Order id is: ", order_id)

    # Get the order by user, and by order_id

    order = model_orders.order_by_user_and_order_id(user_email=user_email, order_id=order_id)

    # if all orders is empty, just close it
    if order is None:
        print("errors", ["No corresponding orders are found!", str(request.data)])
        return jsonify({
            "errors": ["No corresponding orders are found!", str(request.data)]
        }), 400

    # Based on status of the order, delete non-needed properties
    # TODO: Refactor this code into a common block
    all_possible_part_keys = {
        "quantity",
        "item_single_including_margin_price",
        "item_list_price",
        "id",
        "part_external_identifier",
        "manufacturer",
        "manufacturer_abbreviation",
        "description_en",
        "description_de",
        "price_currency",
        "searchstring",
    }

    all_possible_order_keys = {
        "id",  # is the order_id
        "order_id",
        "user_name",
        "reference",
        "company_name",
        "shipment_address",
        "tax_rate",
        "absolute_discount",
        "note",
        "date_submitted",
        "valid_through_date",
        "expected_delivery_date",
        "paid_on_date",
        "status",
        "items",
        "files",
        # "totalNetPrice",
        # "totalPriceMinusDiscount",
        "total_price_including_discount_and_taxrate",
        "currency",
    }

    if order["status"] == "waiting_for_offer":
        keep_part_keys = {"quantity", "id", "part_external_identifier",
                          "manufacturer", "manufacturer_abbreviation", "description_en",
                          "description_de", "price_currency", "searchstring", "order_id"
                          }
        keep_order_keys = {
            "id", "user_name", "reference",
            "company_name", "shipment_address", "note",
            "date_submitted", "status", "items", "files",
            "currency", "order_id"
        }

    elif order["status"] in {"waiting_for_confirmation", "delivery_sent", "waiting_for_delivery"}:
        keep_part_keys = all_possible_part_keys
        keep_order_keys = all_possible_order_keys

    else:
        assert False, ("Order status is not well-defined!", order["status"])

    # Only keep certain part-items in order
    items_arr = order["items"]
    order["items"] = [{k: item_dict[k] for k in keep_part_keys} for item_dict in items_arr]

    # Only keep certain keys in order
    print("Order is: ", order.keys())
    order = {k: order[k] for k in keep_order_keys}

    # Other thigs to keep / not keep
    return jsonify({
        "response": order
    }), 200
