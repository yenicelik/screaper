"""
    Item Entity Defition
"""


class Item:

    def __init__(self):
        self.manufacturer = None
        self.manufacturer_abbreviation = None
        self.part_external_identifier = None
        self.description = dict()
        self.status = None
        self.price = None
        self.price_currency = None
        self.number_in_stock = None
        self.weight_in_g = None
        self.replaced_by = None

        self.changes = None  # ???
        self.shortcut = None  # ???
        self.hs_code = None  # ???
        self.important = None  # ???
