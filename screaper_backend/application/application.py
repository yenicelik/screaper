import json

from flask import jsonify, request, Response

from screaper_backend.resources.firebase_wrapper import check_authentication_token

load_dotenv()

# These need to run before further imports, otherwise circular (maybe just put them into __init__
application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DatabaseUrlApplication')
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(application)
CORS(application)

from screaper_backend.algorithms.product_similarity import AlgorithmProductSimilarity
from screaper_backend.exporter.exporter_offer_excel import ExporterOfferExcel

from screaper_backend.models.orders import model_orders
from screaper_backend.models.customers import model_customers
from screaper_backend.models.parts import model_parts
from screaper_backend.algorithms.product_similarity import AlgorithmProductSimilarity

from screaper_backend.application import application

# Algorithms
algorithm_product_similarity = AlgorithmProductSimilarity()

def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return screaper_database.User.query.get(int(user_id))


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

    out = model_orders.orders()
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
        Example request could look as follows:
        {
            "user_uuid": "b6347351-7fbb-406b-9b4d-4e90e9021834"
            "reference": "",
            "customer_username": "",
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
        input_json = request.form
    except Exception as e:
        print("Request body could not be parsed!", str(e), str(request.data))
        return jsonify({
            "errors": ["Request body could not be parsed!", str(e), str(request.data)]
        }), 400

    print("Got request: ", input_json)

    # Ignore input, and return all mockups
    user_uuid = input_json.get("user_uuid")
    reference = input_json.get("reference")
    customer_username = input_json.get("customer_username")
    items = input_json.getlist("items")

    err = check_property_is_included_formdata(input_json, "user_uuid", type_def=str)
    if err is not None:
        return err

    # err = check_property_is_included_formdata(input_json, "items", type_def=list)
    # if err is not None:
    #     return err

    err = check_property_is_included_formdata(input_json, "customer_username", type_def=str)
    if err is not None:
        return err

    err = check_property_is_included_formdata(input_json, "reference", type_def=str)
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

    optional_item_key_value_pairs = [
        ("manufacturer_status", str),  # string
        ("manufacturer_stock", float),  # string
        ("weight_in_g", float),  # number
        ("replaced_by", str),  # string
        ("changes", float),  # number
        ("shortcut", str),  # string
        ("hs_code", str),  # string
        ("important", str),  # string
        ("description_de", str),  # string
    ]
    for item_json in input_json['items']:
        for item_name, item_type in optional_item_key_value_pairs:
            err = check_optional_property(item_json, item_name, type_def=item_type)
            if err is not None:
                return err

    # Ignore input, and return all mockups
    user_uuid = input_json["user_uuid"]
    reference = input_json["reference"]
    customer_username = input_json["customer_username"]

    items = input_json["items"]
    items = sorted(items, key=lambda x: x['sequence_order'])

    # Check if customer username is existent
    customers = model_customers.customer_usernames()
    if customer_username not in customers:
        print(f"customer_username not recognized!!", str(customer_username), str(input_json))
        return jsonify({
            "errors": [f"customer_username not recognized!!", str(customer_username), str(input_json)]
        }), 400

    if not reference:
        print(f"reference not recognized!!", str(reference), str(input_json))
        return jsonify({
            "errors": [f"reference not recognized!!", str(reference), str(input_json)]
        }), 400

    for item in items:
        part_id = item['id']
        if part_id not in model_parts.part_ids():
            print(f"part id not recognized!!", str(part_id), str(input_json))
            return jsonify({
                "errors": [f"part id not recognized!!", str(part_id), str(input_json)]
            }), 400

    # Insert this into the database
    model_orders.create_order(
        customer_username=customer_username,
        reference=reference,
        order_items=items
    )

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

    customer_obj = model_customers.customer_by_username(customer_username)
    exporter.insert_customer(customer_obj)
    # exporter.insert_reference(reference)

    exporter.update_date()

    wrapped_file = exporter.get_bytestring()

    print("Sending file: ", wrapped_file)
    print("Sending file... ")
    return Response(wrapped_file, mimetype="text/plain", direct_passthrough=True)

# @application.route('/orders', methods=["POST"])
# def list_orders():
