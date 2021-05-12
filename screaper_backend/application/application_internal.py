from flask import request

from screaper_backend.application import application
from screaper_backend.application.internal.internal_customers_get import _internal_customers_get
from screaper_backend.application.internal.internal_orders_edit import _internal_orders_edit
from screaper_backend.application.internal.internal_orders_get import _internal_orders_get
from screaper_backend.resources.firebase_wrapper import check_authentication_token


@application.route('/internal/customers-get', methods=["GET", "POST"])
@check_authentication_token
def internal_customers_get():
    """
        Example request could look as follows:
        {
            "user_uuid": "b6347351-7fbb-406b-9b4d-4e90e9021834"
        }
    """
    return _internal_customers_get(request)


@application.route('/internal/products', methods=["GET", "POST"])
@check_authentication_token
def internal_list_products():
    """
        Example request could look as follows:
        {
            "query": "BC"
        }

    """
    return _internal_customers_get(request)


@application.route('/internal/orders-get', methods=["GET", "POST"])
@check_authentication_token
def internal_orders_get():
    """
        Example request could look as follows:
        {}

    """
    return _internal_orders_get(request)


@application.route('/internal/orders-get-single', methods=["GET", "POST"])
@check_authentication_token
def internal_orders_get_single():
    """
        Example request could look as follows:
        {}

    """
    return internal_orders_get_single(request)


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
    return _internal_orders_edit(request)
