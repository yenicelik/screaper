from flask import request

from screaper_backend.application import application
from screaper_backend.application.external.external_addresses_get import _external_addresses_get
from screaper_backend.application.external.external_list_products import _external_list_products
from screaper_backend.application.external.external_orders_confirm import _external_orders_confirm
from screaper_backend.application.external.external_orders_edit import _external_orders_edit
from screaper_backend.application.external.external_orders_get_single import _external_orders_get_single
from screaper_backend.application.external.external_orders_post import _external_orders_post
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
    return _external_list_products(request)


@application.route('/external/orders-get', methods=["GET", "POST"])
@check_authentication_token
def external_orders_get():
    """
        Example request could look as follows:
        {}

    """
    return _external_list_products(request)


@application.route('/external/orders-get-single', methods=["GET", "POST"])
@check_authentication_token
def external_orders_get_single():
    """
        Example request could look as follows:
        {}

    """
    return _external_orders_get_single(request)


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
    return _external_orders_post(request)


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
    return _external_orders_edit(request)


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
    return _external_orders_confirm(request)


@application.route('/external/addresses-get', methods=["GET", "POST"])
@check_authentication_token
def external_addresses_get():
    """
        Example request could look as follows:
        {}
    """
    return _external_addresses_get(request)
