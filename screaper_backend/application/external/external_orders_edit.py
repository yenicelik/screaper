import datetime
import json
import random

from flask import jsonify
from werkzeug.utils import secure_filename

from screaper_backend.application.utils import check_property_is_included, check_property_is_included_formdata
from screaper_backend.models.customers import model_customers
from screaper_backend.models.orders import model_orders
from screaper_backend.models.parts import model_parts


def _external_orders_edit(request):
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
