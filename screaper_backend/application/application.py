import json

from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
db = SQLAlchemy(application)
CORS(application)

from screaper_backend.algorithms.product_similarity import AlgorithmProductSimilarity
from screaper_backend.application.authentication import authentication_token, whitelisted_ips
from screaper_backend.exporter.exporter_offer_excel import ExporterOfferExcel
from screaper_backend.models.orders import model_orders

# Algorithms
algorithm_product_similarity = AlgorithmProductSimilarity()

def authenticate(request):
    header_token = request.headers.get('token')
    if header_token not in authentication_token:
        return jsonify({
            "errors": ["Permission denied", str(request.headers)]
        }), 403

    # if str(request.remote_addr) not in whitelisted_ips:
    #     return jsonify({
    #         "errors": ["Permission denied", request.headers]
    #     }), 403

    return None


def check_property_is_included(input_json, property_name, type_def):

    assert property_name, property_name

    if property_name not in input_json:
        return jsonify({
            "errors": [f"{property_name} not fund!", str(input_json)]
        }), 400

    if input_json[property_name] is None:
        return jsonify({
            "errors": [f"{property_name} empty!", str(input_json)]
        }), 400

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
    tmp = authenticate(request)
    if tmp is not None:
        return tmp

    return jsonify({
        "response": "API is up and running!"
    }), 200


@application.route('/products', methods=["GET", "POST"])
def list_products():
    """
        Example request could look as follows:
        {
            "query": "BC"
        }

    """
    tmp = authenticate(request)
    if tmp is not None:
        return tmp

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
def orders_get():
    """
        Example request could look as follows:
        {
            "user_uuid": "b6347351-7fbb-406b-9b4d-4e90e9021834"
        }

    """
    tmp = authenticate(request)
    if tmp is not None:
        return tmp

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

    out = model_orders.orders()

    return jsonify({
        "response": out
    }), 200


@application.route('/orders-post', methods=["GET", "POST"])
def orders_post():
    """
        Example request could look as follows:
        {
            "user_uuid": "b6347351-7fbb-406b-9b4d-4e90e9021834"
            "reference": "",
            "items": [
                {
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
    tmp = authenticate(request)
    if tmp is not None:
        return tmp

    try:
        input_json = json.loads(request.data, strict=False)
    except Exception as e:
        print("Request body could not be parsed!", str(e), str(request.data))
        return jsonify({
            "errors": ["Request body could not be parsed!", str(e), str(request.data)]
        }), 400

    print("Got request: ", input_json)

    err = check_property_is_included(input_json, "user_uuid", type_def=str)
    if err is not None:
        return err

    err = check_property_is_included(input_json, "items", type_def=list)
    if err is not None:
        return err

    item_key_value_pairs = [
        ("part_external_identifier", str),  # string
        ("manufacturer_status", str),  # string
        ("manufacturer_price", float),  # number
        ("manufacturer_stock", float),  # string
        ("manufacturer", str),  # string
        ("manufacturer_abbreviation", str),  # string
        ("weight_in_g", float),  # number
        ("replaced_by", str),  # string
        ("changes", float),  # number
        ("shortcut", str),  # string
        ("hs_code", str),  # string
        ("important", str),  # string
        ("description_en", str),  # string
        ("description_de", str),  # string
        ("price_currency", str),  # string
        ("cost_multiple", float), # float

        ("sequence_order", float),  # number
        ("quantity", float),  # number
        ("total_manufacturing_price", float),  # number
        ("cost_multiple", float),  # number
        ("total_final_price", float),  # number
        ("total_final_profit", float),  # number
    ]

    for item_json in input_json['items']:
        for item_name, item_type in item_key_value_pairs:
            err = check_property_is_included(item_json, item_name, type_def=item_type)
            if err is not None:
                return err

    # Ignore input, and return all mockups
    user_uuid = input_json["user_uuid"]
    items = input_json["items"]
    items = sorted(items, key=lambda x: x['sequence_order'])

    # TODO: Insert this into the database

    exporter = ExporterOfferExcel()

    # Input parts to the Excel
    for part_json in items:
        # Identify the unit number
        # Will not include this because this does not work well yet
        exporter.insert_item(
            partnumber=part_json['part_external_identifier'],
            description=part_json['description_en'],
            listprice=part_json['manufacturer_price'],
            requested_units=part_json['quantity'],
            margin_multiplier=part_json['cost_multiple'],

            stock=part_json['manufacturer_stock'],
            status=part_json['manufacturer_status'],
            weight=part_json['weight_in_g'],
            replaced=part_json['replaced_by']
        )

    exporter.update_date()

    wrapped_file = exporter.get_bytestring()

    print("Sending file: ", wrapped_file)
    print("Sending file... ")
    return Response(wrapped_file, mimetype="text/plain", direct_passthrough=True)


# @application.route('/orders', methods=["POST"])
# def list_orders():