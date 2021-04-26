from flask import jsonify

from screaper_backend.algorithms.product_similarity import AlgorithmProductSimilarity

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
