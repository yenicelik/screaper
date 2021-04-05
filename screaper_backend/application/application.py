import json
import random

from flask import jsonify, request, Response

from werkzeug.utils import secure_filename

from screaper_backend.resources.firebase_wrapper import check_authentication_token

from screaper_backend.exporter.exporter_offer_excel import ExporterOfferExcel

from screaper_backend.models.orders import model_orders
from screaper_backend.models.customers import model_customers
from screaper_backend.models.parts import model_parts
from screaper_backend.algorithms.product_similarity import AlgorithmProductSimilarity

from screaper_backend.application import application

ALLOWED_EXTENSIONS = {'pdf'}  # later also add excel format 'txt' 'png', 'jpg', 'jpeg'
# Algorithms
algorithm_product_similarity = AlgorithmProductSimilarity()

def check_property_is_included(input_json, property_name, type_def):
    assert property_name, property_name

    if property_name not in input_json:
        return jsonify({
            "errors": [f"{property_name} not found!", str(input_json)]
        }), 400

    if input_json[property_name] is None:
        return jsonify({
            "errors": [f"{property_name} empty!", str(input_json)]
        }), 400

    if type_def == float:
        if not isinstance(input_json[property_name], float) and not isinstance(input_json[property_name], int):
            return jsonify({
                "errors": [f"{property_name} not of type {type_def}!", str(type(input_json[property_name])),
                           str(input_json)]
            }), 400
    else:
        if not isinstance(input_json[property_name], type_def):
            return jsonify({
                "errors": [f"{property_name} not of type {type_def}!", str(type(input_json[property_name])),
                           str(input_json)]
            }), 400

    return None

def check_property_is_included_formdata(input_json, property_name, type_def, multiple=False):
    assert property_name, property_name

    if not input_json.get(property_name):
        return jsonify({
            "errors": [f"{property_name} not found or empty!", str(input_json)]
        }), 400

    if type_def == float:
        if not isinstance(input_json.get(property_name), float) and not isinstance(input_json.get(property_name), int):
            return jsonify({
                "errors": [f"{property_name} not of type {type_def}!", str(type(input_json.get(property_name))),
                           str(input_json)]
            }), 400
    else:
        if not isinstance(input_json.get(property_name), type_def):
            return jsonify({
                "errors": [f"{property_name} not of type {type_def}!", str(type(input_json.get(property_name))),
                           str(input_json)]
            }), 400

    return None

def check_optional_property(input_json, property_name, type_def):

    assert property_name, property_name

    if property_name not in input_json:
        return jsonify({
            "errors": [f"{property_name} not found!", str(input_json)]
        }), 400

    if input_json[property_name] is None:
        return None

    if type_def == float:
        if not isinstance(input_json[property_name], float) and not isinstance(input_json[property_name], int):
            return jsonify({
                "errors": [f"{property_name} not of type {type_def}!", str(type(input_json[property_name])), str(input_json)]
            }), 400
    else:
        if not isinstance(input_json[property_name], type_def):
            return jsonify({
                "errors": [f"{property_name} not of type {type_def}!", str(type(input_json[property_name])), str(input_json)]
            }), 400

    return None


@application.route('/')
def healthcheckpoint():
    """
        Example request could look as follows:
        {
            "search_query": "bearings"
        }

    """
    return jsonify({
        "response": "API is up and running!"
    }), 200


@application.route('/products', methods=["GET", "POST"])
@check_authentication_token
def list_products():
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


@application.route('/orders-get', methods=["GET", "POST"])
@check_authentication_token
def orders_get():
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

    # Get orders for this user only!
    print("User is: ", request.user)
    user_email = request.user.get("email")

    print("User uuid and user email are: ", user_uuid, user_email)

    out = model_orders.orders_by_user(user_email=user_email)
    # Turn into one mega-dictionary per object
    out = [x for x in out]

    return jsonify({
        "response": out
    }), 200


@application.route('/customers-get', methods=["GET", "POST"])
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

    print("Got request: ", input_json)

    out = model_customers.customers()
    # Turn into one mega-dictionary per object
    out = [x for x in out]

    return jsonify({
        "response": out
    }), 200


@application.route('/orders-post', methods=["GET", "POST"])
@check_authentication_token
def orders_post():
    """
        good tutorial on how to read in form data
        https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request

        Example request could look as follows:
        {
            "user_uuid": "b6347351-7fbb-406b-9b4d-4e90e9021834"
            "reference": "",
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
    user_uuid = input_form_data.get("user_uuid")
    reference = input_form_data.get("reference")
    items = input_form_data.getlist("items")

    customer_email = request.user.get('email')

    err = check_property_is_included_formdata(input_form_data, "user_uuid", type_def=str)
    if err is not None:
        return err

    err = check_property_is_included_formdata(input_form_data, "reference", type_def=str)
    if err is not None:
        return err

    item_key_value_pairs = [
        ("part_external_identifier", str),  # string
        ("manufacturer_price", float),  # number
        ("manufacturer", str),  # string
        ("manufacturer_abbreviation", str),  # string
        ("description_en", str),  # string
        ("price_currency", str),  # string
        ("cost_multiple", float),  # float

        ("item_single_price", float),
        ("sequence_order", float),  # number
        ("quantity", float),  # number
        ("total_manufacturing_price", float),  # number
        ("cost_multiple", float),  # number
        ("total_final_price", float),  # number
        ("total_final_profit", float),  # number
    ]

    if not items or len(items) == 0:
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

    if not reference:
        print(f"reference not recognized!!", str(reference), str(input_form_data))
        return jsonify({
            "errors": [f"reference not recognized!!", str(reference), str(input_form_data)]
        }), 400

    for item in items:
        part_id = item['id']
        if part_id not in model_parts.part_ids():
            print(f"part id not recognized!!", str(part_id), str(input_form_data))
            return jsonify({
                "errors": [f"part id not recognized!!", str(part_id), str(input_form_data)]
            }), 400

    # Insert this into the database
    model_orders.create_order(
        customer_email=customer_email,
        reference=reference,
        order_items=items,
        files=files
    )

    return jsonify({
        "response": "Order successfully filled!"
    }), 200

    # Do not send a file back, as this is only input from the customer
    # This file should not be generated yet, I guess, think about it later

    # return Response(wrapped_file, mimetype="text/plain", direct_passthrough=True)

# @application.route('/orders', methods=["POST"])
# def list_orders():
