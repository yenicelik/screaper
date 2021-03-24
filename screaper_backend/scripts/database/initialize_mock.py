
def _create_mock_customers(database_wrapper):
    """
        Create some mock elements:
        - Create a single customer. This is the placeholder for all customers now
    :return:
    """
    # Create one "default" customer; which is used if no customer is defined
    database_wrapper.create_customer(
        user_name="gulsan_sentetik",
        company_name="GÜLSAN SENTETİK DOKUMA SAN. VE TİC.A.Ş.",
        phone_number="(0342) 337 11 80",
        fax_number="(0342) 337 25 28",
        domain_name="",
        email="",
        address="",
        city="GAZİANTEP",
        country="",
        contact_name="Sn.Tuğba YILDIRIM"
    )
    database_wrapper.create_customer(
        user_name="kayseri_sentetik",
        company_name="KAYSERI ŞEKER FABRIKASI A.Ş.",
        phone_number="(0-352) 331 24 00 (6 hat)",
        fax_number="(0-352) 331 24 06",
        domain_name="kayseriseker.com.tr",
        email="haberlesme@kayseriseker.com.tr",
        address="Osman Kavuncu Cad. 7. KM 38070 Kocasinan",
        city="KAYSERI",
        country="",
        contact_name=""
    )
    database_wrapper.session.commit()

def _create_mock_order(database_wrapper):
    """
        Create some mock elements:
        - Create a single customer. This is the placeholder for all customers now
    :return:
    """

    # Get first customer
    customer = database_wrapper.read_customers_obj()[0]

    order = database_wrapper.create_single_order(customer=customer, reference="ref MCY-GLS")
    print("Created order with orderid: ", order.id)

    # print parts that we're gonna input:
    part = database_wrapper.read_part_by_part_id_obj(5)
    print("buying part: ", part.to_dict())
    database_wrapper.create_order_item(
        order=order,
        part=part,
        quantity=50,
        item_single_price=50,
    )
    part = database_wrapper.read_part_by_part_id_obj(100)
    print("buying part: ", part.to_dict())
    database_wrapper.create_order_item(
        order=order,
        part=part,
        quantity=12,
        item_single_price=684.13 * 2.5,
    )
    part = database_wrapper.read_part_by_part_id_obj(52)
    print("buying part: ", part.to_dict())
    database_wrapper.create_order_item(
        order=order,
        part=part,
        quantity=12,
        item_single_price=100 * 2.5,
    )
    part = database_wrapper.read_part_by_part_id_obj(53)
    print("buying part: ", part.to_dict())
    database_wrapper.create_order_item(
        order=order,
        part=part,
        quantity=12,
        item_single_price=100 * 2.5,
    )
    part = database_wrapper.read_part_by_part_id_obj(23)
    print("buying part: ", part.to_dict())
    database_wrapper.create_order_item(
        order=order,
        part=part,
        quantity=12,
        item_single_price=100 * 2.5,
    )
    part = database_wrapper.read_part_by_part_id_obj(64)
    print("buying part: ", part.to_dict())
    database_wrapper.create_order_item(
        order=order,
        part=part,
        quantity=12,
        item_single_price=100 * 2.5,
    )
    part = database_wrapper.read_part_by_part_id_obj(24)
    print("buying part: ", part.to_dict())
    database_wrapper.create_order_item(
        order=order,
        part=part,
        quantity=12,
        item_single_price=100 * 2.5,
    )
    part = database_wrapper.read_part_by_part_id_obj(64)
    print("buying part: ", part.to_dict())
    database_wrapper.create_order_item(
        order=order,
        part=part,
        quantity=12,
        item_single_price=100 * 2.5,
    )
    part = database_wrapper.read_part_by_part_id_obj(75)
    print("buying part: ", part.to_dict())
    database_wrapper.create_order_item(
        order=order,
        part=part,
        quantity=12,
        item_single_price=100 * 2.5,
    )
    part = database_wrapper.read_part_by_part_id_obj(86)
    print("buying part: ", part.to_dict())
    database_wrapper.create_order_item(
        order=order,
        part=part,
        quantity=12,
        item_single_price=100 * 2.5,
    )
    database_wrapper.session.commit()
