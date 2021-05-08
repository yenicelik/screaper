import datetime
import json
import random

from flask import jsonify, request
from werkzeug.utils import secure_filename

from screaper_backend.application import application
from screaper_backend.application.utils import algorithm_product_similarity, check_property_is_included_formdata, \
    check_property_is_included, check_property_is_included_typed
from screaper_backend.models.customers import model_customers
from screaper_backend.models.orders import model_orders
from screaper_backend.models.parts import model_parts
from screaper_backend.resources.firebase_wrapper import check_authentication_token


@application.route('/external/products', methods=["GET", "POST"])
@check_authentication_token
def external_list_products():
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


@application.route('/external/orders-get', methods=["GET", "POST"])
@check_authentication_token
def external_orders_get():
    """
        Example request could look as follows:
        {}

    """
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

    print("User uuid and user email are: ", user_email)

    all_orders = model_orders.orders_by_user(user_email=user_email)
    # Turn into one mega-dictionary per object
    # out = [x for x in out]

    # Based on status of the order, delete non-needed properties

    out = []

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

    for order in all_orders:

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

        # Only keep certain items within the order parts
        out.append(order)

    all_orders = out

    return jsonify({
        "response": all_orders
    }), 200


@application.route('/external/orders-post', methods=["GET", "POST"])
@check_authentication_token
def external_orders_post():
    """
        good tutorial on how to read in form data
        https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request

        Example request could look as follows:
        {
            # "reference": "",
            "shipment_address": "Seker Fabrika Athena Yenimahalle sk. 16-1 60999 Türkiye",
            "items": [
                {
                    id: number,
                    part_external_identifier: string,
                    manufacturer_status: string,
                    manufacturer_price: number,
                    manufacturer_stock: string,
                    manufacturer: string,
                    manufacturer_abbreviation: string,
                    weight_in_g: number,
                    replaced_by: string,
                    changes: number,
                    shortcut: string,
                    hs_code: string,
                    important: string,
                    description_en: string,
                    description_de: string,
                    price_currency: string,
                    sequence_order: number,

                    quantity: number;
                    total_manufacturing_price: number;
                    cost_multiple: number;
                    total_final_price: number;
                    total_final_profit: number;
                },
                ...
            ]
        }

    """

    try:
        input_form_data = request.form
        input_form_files = request.files
    except Exception as e:
        print("Request body could not be parsed!", str(e), str(request.data))
        return jsonify({
            "errors": ["Request body could not be parsed!", str(e), str(request.data)]
        }), 400

    print("Got request: ", input_form_data)
    print("Files are: ", input_form_files)

    ######################
    #
    # HANDLE FILE IF ANY
    #
    ######################

    files = {}
    if input_form_files:
        print("File was provided!", input_form_files)

        _files = request.files
        _files = {k: v for k, v in _files.items()}

        print("Files are: ", _files)

        # if user does not select file, browser also
        # submit an empty part without filename
        for filename, file in _files.items():

            print("Looking at file: ", file)

            if filename == '':
                print("errors", ["No File provided!", str(input_form_files)])
                return jsonify({
                    "errors": ["No File provided!", str(input_form_files)]
                }), 400

            filename = secure_filename(file.filename)
            if filename == '':
                print("errors", ["No File provided!", str(input_form_files)])
                return jsonify({
                    "errors": ["No File provided!", str(input_form_files)]
                }), 400

            filename = str(random.randint(10000, 99999)) + "_" + filename

            # Change this to saving the file in the filesystem (or as a blob), and referencing this save in the database
            # import os
            # file.save(os.path.join("/Users/david/screaper/data", filename))
            files[filename] = file
    else:
        print("No files provided!", input_form_files)

    # Ignore input, and return all mockups
    # reference = input_form_data.get("reference")
    shipment_address = input_form_data.get("shipment_address")
    note = input_form_data.get("note")
    items = input_form_data.getlist("items")

    customer_email = request.user.get('email')

    # err = check_property_is_included_formdata(input_form_data, "reference", type_def=str)
    # if err is not None:
    #     return err

    err = check_property_is_included_formdata(input_form_data, "shipment_address", type_def=str)
    if err is not None:
        return err

    # err = check_property_is_included_formdata(input_form_data, "note", type_def=str)
    # if err is not None:
    #     return err

    item_key_value_pairs = [
        ("part_external_identifier", str),  # string

        ("manufacturer", str),  # string
        ("manufacturer_abbreviation", str),  # string
        ("description_en", str),  # string

        # All these price-related items need to be provided in a separate, internal tool (if at all!)
        # alternatively, we need to make this accessible programmatically
        # ("price_currency", str),  # string
        # ("manufacturer_price", float),  # number
        # ("cost_multiple", float),  # float
        # ("item_single_price", float),
        # ("total_manufacturing_price", float),  # number
        # ("cost_multiple", float),  # number
        # ("total_final_price", float),  # number
        # ("total_final_profit", float),  # number

        ("sequence_order", float),  # number
        ("quantity", float),  # number
    ]

    if not items or len(items) == 0:
        print("errors", ["No items found in request!", str(items), str(request.form)])
        return jsonify({
            "errors": ["No items found in request!", str(items), str(request.form)]
        }), 400

    # decode the json into json objects
    # Also pass try catc around this?
    tmp_items = [json.loads(x) for x in items]
    items = []
    for item in tmp_items:
        if item['sequence_order'] is None:
            item['sequence_order'] = -1
        items.append(item)
    items = sorted(items, key=lambda x: x['sequence_order'])

    # Check all types for items now
    for item_json in items:
        # turn into json
        for item_name, item_type in item_key_value_pairs:
            print("Item types are: ")
            print(items)
            print(item_name)
            print(item_type)
            err = check_property_is_included(item_json, item_name, type_def=item_type)
            if err is not None:
                return err

    # optional_item_key_value_pairs = [
    #     ("manufacturer_status", str),  # string
    #     ("manufacturer_stock", float),  # string
    #     ("weight_in_g", float),  # number
    #     ("replaced_by", str),  # string
    #     ("changes", float),  # number
    #     ("shortcut", str),  # string
    #     ("hs_code", str),  # string
    #     ("important", str),  # string
    #     ("description_de", str),  # string
    # ]
    # for item_json in input_json['items']:
    #     for item_name, item_type in optional_item_key_value_pairs:
    #         err = check_optional_property(item_json, item_name, type_def=item_type)
    #         if err is not None:
    #             return err

    # email = request.user['email']
    #
    # # Based on the email

    # the customer username will basically be taken over through the customer email

    # Check if customer username is existent
    customers = model_customers.customer_emails()
    if (not customer_email) or (customer_email not in customers):
        print("Customers are: ", customers)
        print(f"customer_email not recognized!!", str(customer_email), str(input_form_data))
        return jsonify({
            "errors": [f"customer_email not recognized!!", str(customer_email), str(input_form_data)]
        }), 400

    # if not reference:
    #     print(f"reference not recognized!!", str(reference), str(input_form_data))
    #     return jsonify({
    #         "errors": [f"reference not recognized!!", str(reference), str(input_form_data)]
    #     }), 400

    for item in items:
        part_id = item['id']
        if part_id not in model_parts.part_ids():
            print(f"part id not recognized!!", str(part_id), str(input_form_data))
            return jsonify({
                "errors": [f"part id not recognized!!", str(part_id), str(input_form_data)]
            }), 400

    # Insert this into the database
    # Automatically create the reference
    reference = "BMBaker-" + datetime.datetime.today().strftime('%Y-%m-%d-%H:%M')
    model_orders.create_order(
        customer_email=customer_email,
        reference=reference,
        order_items=items,
        shipment_address=shipment_address,
        note=note,
        files=files
    )

    return jsonify({
        "response": "Order successfully filled!"
    }), 200


@application.route('/external/orders-edit', methods=["GET", "POST"])
@check_authentication_token
def external_orders_edit():
    """
        Update any data that was submitted by the user


        Example request could look as follows:
        {
            # "reference": "",
            "shipment_address": "Seker Fabrika Athena Yenimahalle sk. 16-1 60999 Türkiye",
            "items": [
                {
                    id: number,
                    part_external_identifier: string,
                    manufacturer_status: string,
                    manufacturer_price: number,
                    manufacturer_stock: string,
                    manufacturer: string,
                    manufacturer_abbreviation: string,
                    weight_in_g: number,
                    replaced_by: string,
                    changes: number,
                    shortcut: string,
                    hs_code: string,
                    important: string,
                    description_en: string,
                    description_de: string,
                    price_currency: string,
                    sequence_order: number,

                    quantity: number;
                    total_manufacturing_price: number;
                    cost_multiple: number;
                    total_final_price: number;
                    total_final_profit: number;
                },
                ...
            ]
        }

    """

    try:
        input_form_data = request.form
        input_form_files = request.files
    except Exception as e:
        print("Request body could not be parsed!", str(e), str(request.data))
        return jsonify({
            "errors": ["Request body could not be parsed!", str(e), str(request.data)]
        }), 400

    print("Got request: ", input_form_data)
    print("Files are: ", input_form_files)

    # TODO: Make sure that status is not delivered, etc.

    ######################
    #
    # HANDLE FILE IF ANY
    #
    ######################

    files = {}
    if input_form_files:
        print("File was provided!", input_form_files)

        _files = request.files
        _files = {k: v for k, v in _files.items()}

        print("Files are: ", _files)

        # if user does not select file, browser also
        # submit an empty part without filename
        for filename, file in _files.items():

            print("Looking at file: ", file)

            if filename == '':
                print("errors", ["No File provided!", str(input_form_files)])
                return jsonify({
                    "errors": ["No File provided!", str(input_form_files)]
                }), 400

            filename = secure_filename(file.filename)
            if filename == '':
                print("errors", ["No File provided!", str(input_form_files)])
                return jsonify({
                    "errors": ["No File provided!", str(input_form_files)]
                }), 400

            filename = str(random.randint(10000, 99999)) + "_" + filename

            # Change this to saving the file in the filesystem (or as a blob), and referencing this save in the database
            # import os
            # file.save(os.path.join("/Users/david/screaper/data", filename))
            files[filename] = file
    else:
        print("No files provided!", input_form_files)

    # Ignore input, and return all mockups
    # reference = input_form_data.get("reference")
    shipment_address = input_form_data.get("shipment_address")
    note = input_form_data.get("note")
    items = input_form_data.getlist("items")

    customer_email = request.user.get('email')

    # err = check_property_is_included_formdata(input_form_data, "reference", type_def=str)
    # if err is not None:
    #     return err

    err = check_property_is_included_formdata(input_form_data, "shipment_address", type_def=str)
    if err is not None:
        return err

    err = check_property_is_included_formdata(input_form_data, "note", type_def=str)
    if err is not None:
        return err

    item_key_value_pairs = [
        ("part_external_identifier", str),  # string

        ("manufacturer", str),  # string
        ("manufacturer_abbreviation", str),  # string
        ("description_en", str),  # string

        # All these price-related items need to be provided in a separate, internal tool (if at all!)
        # alternatively, we need to make this accessible programmatically
        # ("price_currency", str),  # string
        # ("manufacturer_price", float),  # number
        # ("cost_multiple", float),  # float
        # ("item_single_price", float),
        # ("total_manufacturing_price", float),  # number
        # ("cost_multiple", float),  # number
        # ("total_final_price", float),  # number
        # ("total_final_profit", float),  # number

        ("sequence_order", float),  # number
        ("quantity", float),  # number

    ]

    if not items or len(items) == 0:
        print("errors", ["No items found in request!", str(items), str(request.form)])
        return jsonify({
            "errors": ["No items found in request!", str(items), str(request.form)]
        }), 400

    # decode the json into json objects
    # Also pass try catc around this?
    items = [json.loads(x) for x in items]
    items = sorted(items, key=lambda x: x['sequence_order'])

    # Check all types for items now
    for item_json in items:
        # turn into json
        for item_name, item_type in item_key_value_pairs:
            print("Item types are: ")
            print(items)
            print(item_name)
            print(item_type)
            err = check_property_is_included(item_json, item_name, type_def=item_type)
            if err is not None:
                return err

    # the customer username will basically be taken over through the customer email

    # Check if customer username is existent
    customers = model_customers.customer_emails()
    if (not customer_email) or (customer_email not in customers):
        print("Customers are: ", customers)
        print(f"customer_email not recognized!!", str(customer_email), str(input_form_data))
        return jsonify({
            "errors": [f"customer_email not recognized!!", str(customer_email), str(input_form_data)]
        }), 400

    for item in items:
        part_id = item['id']
        if part_id not in model_parts.part_ids():
            print(f"part id not recognized!!", str(part_id), str(input_form_data))
            return jsonify({
                "errors": [f"part id not recognized!!", str(part_id), str(input_form_data)]
            }), 400

    # Insert this into the database
    # Automatically create the reference
    reference = "BMBaker-" + datetime.datetime.today().strftime('%Y-%m-%d-%H:%M')
    # TODO: Gotta make it edit, not create an order!
    model_orders.create_order(
        customer_email=customer_email,
        reference=reference,
        order_items=items,
        shipment_address=shipment_address,
        note=note,
        files=files
    )

    return jsonify({
        "response": "Order successfully filled!"
    }), 200


@application.route('/external/orders-confirm', methods=["GET", "POST"])
@check_authentication_token
def external_orders_confirm():
    """
        Update any data that was submitted by the user

        Example request could look as follows:
        {
            "order_id"
        }

    """

    try:
        input_form_data = request.form
        input_form_files = request.files
    except Exception as e:
        print("Request body could not be parsed!", str(e), str(request.data))
        return jsonify({
            "errors": ["Request body could not be parsed!", str(e), str(request.data)]
        }), 400

    print("Got request: ", input_form_data)
    print("Files are: ", input_form_files)

    # TODO: Make sure that status is not delivered, etc.

    # TODO: Generate the excel file, and save it as a file to the folder (?)
    # That is for waiting for offer, though
    order_id = input_form_data.get("order_id")
    # Parse integer if possible
    order_id = int(order_id) if order_id else order_id

    # Should also just write a for loop for this
    err = check_property_is_included_typed(order_id, type_def=int)
    if order_id and (err is not None):
        return err

    customer_email = request.user.get('email')
    # Check if customer username is existent
    customers = model_customers.customer_emails()
    if (not customer_email) or (customer_email not in customers):
        print("Customers are: ", customers)
        print(f"customer_email not recognized!!", str(customer_email), str(input_form_data))
        return jsonify({
            "errors": [f"customer_email not recognized!!", str(customer_email), str(input_form_data)]
        }), 400

    # Insert this into the database
    # Automatically create the reference
    model_orders.confirm_order_status_to_waiting_for_delivery(
        order_id=order_id,
        customer_email=customer_email
    )

    return jsonify({
        "response": "Order successfully filled!"
    }), 200
