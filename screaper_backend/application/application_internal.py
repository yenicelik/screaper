import datetime
import json
import random

from flask import request, jsonify
from werkzeug.utils import secure_filename

from screaper_backend.application import application
from screaper_backend.application.authentication import admin_emails
from screaper_backend.application.utils import algorithm_product_similarity, check_property_is_included_formdata, \
    check_property_is_included, check_property_is_included_typed
from screaper_backend.models.customers import model_customers
from screaper_backend.models.orders import model_orders
from screaper_backend.models.parts import model_parts
from screaper_backend.resources.firebase_wrapper import check_authentication_token


@application.route('/internal/customers-get', methods=["GET", "POST"])
@check_authentication_token
def customers_get():
    """
        Example request could look as follows:
        {
            "user_uuid": "b6347351-7fbb-406b-9b4d-4e90e9021834"
        }
    """
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


@application.route('/internal/products', methods=["GET", "POST"])
@check_authentication_token
def internal_list_products():
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


@application.route('/internal/orders-get', methods=["GET", "POST"])
@check_authentication_token
def internal_orders_get():
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


@application.route('/internal/orders-get-single', methods=["GET", "POST"])
@check_authentication_token
def internal_orders_get_single():
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


@application.route('/internal/orders-edit', methods=["GET", "POST"])
@check_authentication_token
def internal_orders_edit():
    """
        Update any order parameters

        Example request could look as follows:
        {
            id: 0,
            user_name: "",
            status: "",
            shipmentAddress: "",
            reference: "",

            note: "",
            dateSubmitted: "",
            validThroughDate: "",
            expectedDeliverDate: "",
            company_name: "",
            currency: "",
            items: [],
            files: [],
            paidDate: "",

            // Record all different prices and respective values
            taxRate: 0.,
            absoluteDiscount: 0.,

            totalNetPrice: 0.,
            totalPriceMinusDiscount: 0.,
            totalPriceMinusDiscountPlusTax: 0.,

            "order_id": "",
            "taxRate": "",
            "absoluteDiscount": "",
            "note": "",
            "dateSubmitted": "",
            "validThroughDate": "",
            "expectedDeliverDate": "",
            "reference": "",
            "shipment_address": "Seker Fabrika Athena Yenimahalle sk. 16-1 60999 Türkiye",
            "files": [],
            "paid_on_date":0.,
            "total_price":0.,
            "currency":0.,
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
                return jsonify({
                    "errors": ["No File provided!", str(input_form_files)]
                }), 400

            filename = secure_filename(file.filename)
            if filename == '':
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
    reference = input_form_data.get("reference")
    status = input_form_data.get("status")

    order_id = input_form_data.get("order_id")
    # Parse integer if possible
    order_id = int(order_id) if order_id else order_id

    tax_rate = input_form_data.get("tax_rate")
    tax_rate = float(tax_rate) if tax_rate else tax_rate

    absolute_discount = input_form_data.get("absolute_discount")
    absolute_discount = float(absolute_discount) if absolute_discount else absolute_discount

    date_submitted = input_form_data.get("date_submitted")
    valid_through_date = input_form_data.get("valid_through_date")
    expected_delivery_date = input_form_data.get("expected_delivery_date")
    paid_on_date = input_form_data.get("paid_on_date")

    total_price = input_form_data.get("total_price")
    total_price = float(total_price) if total_price else total_price
    currency = input_form_data.get("currency")

    customer_email = request.user.get('email')

    items = input_form_data.getlist("items")
    print("Items are: ", items)


    # Should also just write a for loop for this
    err = check_property_is_included_typed(order_id, type_def=int)
    if order_id and (err is not None):
        return err

    err = check_property_is_included_typed(tax_rate, type_def=float)
    if tax_rate and (err is not None):
        return err

    # The optional parameters
    err = check_property_is_included_typed(absolute_discount, type_def=float)
    if absolute_discount and (err is not None):
        return err

    err = check_property_is_included_formdata(input_form_data, "date_submitted", type_def=str)
    if date_submitted and (err is not None):
        return err

    err = check_property_is_included_formdata(input_form_data, "valid_through_date", type_def=str)
    if valid_through_date and (err is not None):
        return err

    err = check_property_is_included_formdata(input_form_data, "expected_delivery_date", type_def=str)
    if expected_delivery_date and (err is not None):
        return err

    err = check_property_is_included_formdata(input_form_data, "reference", type_def=str)
    if reference and (err is not None):
        return err

    err = check_property_is_included_formdata(input_form_data, "paid_on_date", type_def=str)
    if paid_on_date and (err is not None):
        return err

    err = check_property_is_included_formdata(input_form_data, "status", type_def=str)
    if paid_on_date and (err is not None):
        return err

    err = check_property_is_included_typed(total_price, type_def=float)
    if total_price and (err is not None):
        return err

    err = check_property_is_included_formdata(input_form_data, "currency", type_def=str)
    if currency and (err is not None):
        return err

    # Convert all elements to dates
    print("Date before: ", date_submitted)
    date_submitted = datetime.datetime.strptime(date_submitted, '%Y-%m-%d') if date_submitted else None
    print("Date Submitted: ", date_submitted, type(date_submitted))
    valid_through_date = datetime.datetime.strptime(valid_through_date, '%Y-%m-%d') if valid_through_date else None
    print("Valid Through Date after: ", valid_through_date, type(valid_through_date))
    # expected_delivery_date = datetime.datetime.strptime(expected_delivery_date, '%Y-%m-%d') if expected_delivery_date else None
    # print("Expected date: ", expected_delivery_date, type(expected_delivery_date))
    paid_on_date = datetime.datetime.strptime(paid_on_date, '%Y-%m-%d') if paid_on_date else None
    print("Paid after: ", paid_on_date, type(paid_on_date))

    # err = check_property_is_included_formdata(input_form_data, "items", type_def=list)
    # if items and (err is not None):
    #     return err

    item_key_value_pairs = [
        ("part_external_identifier", str),  # string

        ("manufacturer", str),  # string
        ("manufacturer_abbreviation", str),  # string
        ("description_en", str),  # string

        # All these price-related items need to be provided in a separate, internal tool (if at all!)
        # alternatively, we need to make this accessible programmatically

        # TODO: Double check which ones are relevant in the end
        ("price_currency", str),  # string
        ("manufacturer_price", float),  # number
        ("cost_multiple", float),  # float
        ("item_single_including_margin_price", float),
        ("total_manufacturing_price", float),  # number
        ("cost_multiple", float),  # number
        ("total_final_price", float),  # number
        ("total_final_profit", float),  # number

        ("sequence_order", float),  # number
        ("quantity", float),  # number

    ]

    if not items or len(items) == 0:
        print("errors", ["No items found in request!", str(items), str(request.form)])
        return jsonify({
            "errors": ["No items found in request!", str(items), str(request.form)]
        }), 400
    else:
        print("found items!", items)

    # decode the json into json objects
    # Also pass try catc around this?
    items = [json.loads(x) for x in items]
    items = sorted(items, key=lambda x: x['sequence_order'])
    print("Items found are: ")
    for x in items:
        print(x)

    # Check all types for items now
    for item_json in items:
        # turn into json
        for item_name, item_type in item_key_value_pairs:
            err = check_property_is_included(item_json, item_name, type_def=item_type)
            if err is not None:
                return err

    # Check if customer username is existent
    customers = model_customers.customer_emails()
    if (not customer_email) or (customer_email not in customers):
        print("Customers are: ", customers)
        print(f"customer_email not recognized!!", str(customer_email), str(input_form_data))
        return jsonify({
            "errors": [f"customer_email not recognized!!", str(customer_email), str(input_form_data)]
        }), 400

    # Make sure only accessible to admins
    # TODO: Make sure only accessible to admins

    for item in items:
        part_id = item['id']
        if part_id not in model_parts.part_ids():
            print(f"part id not recognized!!", str(part_id), str(input_form_data))
            return jsonify({
                "errors": [f"part id not recognized!!", str(part_id), str(input_form_data)]
            }), 400

    # Insert this into the database
    # Automatically create the reference
    model_orders.edit_order_admin(
        order_id=order_id,
        tax_rate=tax_rate,
        absolute_discount=absolute_discount,
        note=note,
        status=status,
        date_submitted=date_submitted,
        valid_through_date=valid_through_date,
        expected_delivery_date=expected_delivery_date,
        reference=reference,
        shipment_address=shipment_address,
        files=files,
        paid_on_date=paid_on_date,
        total_price_including_discount_and_taxrate=total_price,
        currency=currency,
        order_items=items,
    )

    return jsonify({
        "response": "Order successfully filled!"
    }), 200
