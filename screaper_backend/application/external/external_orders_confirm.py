from flask import jsonify

from screaper_backend.application.utils import check_property_is_included_typed
from screaper_backend.models.customers import model_customers
from screaper_backend.models.orders import model_orders


def _external_orders_confirm(request):

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
