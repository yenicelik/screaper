"""
    Union Special Data Importer
    pip openpyxl
    pip xlrd

    # TODO: Implement typed input (should be for database anyways).
    # Write database importer script

    # TODO: Introduce UUIDs for each item (should be done once we push into the database)
"""
import os
import re
import pandas as pd
import numpy as np
from dotenv import load_dotenv

load_dotenv()

class DataImporterUnionSpecial:

    def _str_to_number(self, x):
        if isinstance(x, str):
            x = x.replace(",", "").replace("'", "")
        return float(x)

    def __init__(self):

        path = os.getenv("UNSP_PRICE_LIST_PATH")
        df = pd.read_csv(path)

        print("df is: ", df.head())
        print("Cols: ", df.columns)
        print("Length: ", len(df))

        # replace
        # A : active
        # C : availability / price must be checked
        # G : not available anymore or replaced
        # R : parts on request
        # T : dead part

        # Implement description in another language

        self.df = df.rename(columns={
            'Partnumber': "part_external_identifier",
            'Status': "manufacturer_status",
            'Price €': "manufacturer_price",
            'Stock': "manufacturer_stock",

            'Weight in g': "weight_in_g",
            'Replaced by': "replaced_by",

            'Changes': "changes",
            'Shortcut': "shortcut",
            'HS Code': "hs_code",
            'Important': "important"
        })

        # 'Beschreibung': "description_en",
        # 'Description': "description",
        self.df['description_{}'.format('en')] = self.df['Description']
        self.df['description_{}'.format('de')] = self.df['Beschreibung']

        # Cleanse all strings
        for col in self.df.columns:
            if col in ("manufacturer_price", "manufacturer_stock", "weight_in_g", "changes"):
                continue
            self.df[col] = self.df[col].apply(self._cleanse_strings)

        self.df['price_currency'] = "EUR"
        self.df['manufacturer'] = "Union Special"
        self.df['manufacturer_abbreviation'] = "UNSP"

        # self.df[self.df.isna()] = ''
        # self.df = self.df.replace(np.nan, '', regex=True)

        # Turn numbers into negative numbers if not known
        self.df['manufacturer_price'] = self.df['manufacturer_price'].replace(np.nan, -1).apply(self._str_to_number)
        self.df['weight_in_g'] = self.df['weight_in_g'].replace(np.nan, -1).apply(self._str_to_number)
        self.df['manufacturer_stock'] = self.df['manufacturer_stock'].replace(np.nan, -1).apply(self._str_to_number)
        self.df['changes'] = self.df['changes'].replace(np.nan, -1).apply(self._str_to_number)

        self.df = self.df[[
            "part_external_identifier",
            "manufacturer_status",
            "manufacturer_price",
            "manufacturer_stock",
            "weight_in_g",
            "replaced_by",
            "changes",
            "shortcut",
            "hs_code",
            "important",
            'description_{}'.format('en'),
            'description_{}'.format('de'),
            'price_currency',
            'manufacturer',
            'manufacturer_abbreviation'
        ]]

        # sort df:
        self.df = self.df.sort_values(by="part_external_identifier")

        self._generate_searchstrings()
        print("Columns are: ", self.df.columns)

    def _replace_na_with_empty_string(self, x):
        if x == np.nan:
            return ''
        if not x:
            return ''
        if x is None:
            return ''
        if pd.isna(x):
            return ''
        return x

    def _generate_searchstrings(self):

        # print("Adding ", self.df['part_external_identifier'])
        self.df['searchstring'] = self.df['part_external_identifier'].apply(self._cleanse_strings)
        # print("Adding ", self.df['replaced_by'])
        self.df['searchstring'] += " " + self.df['replaced_by'].apply(self._cleanse_strings)
        self.df['searchstring'] += " " + self.df['manufacturer']
        self.df['searchstring'] += " " + self.df['manufacturer_abbreviation']

        # Put all descriptios into the identifiers
        for language in ['en', 'de']:
            # print("adding: ", self.df['description_{}'.format(language)])
            self.df['searchstring'] += " " + self.df['description_{}'.format(language)].apply(self._cleanse_strings)

        self.df['searchstring'] = self.df['searchstring'].apply(self._cleanse_strings)

        # Make all lowercase
        self.df['searchstring'] = self.df['searchstring'].apply(lambda x: x.lower())

        print("Search String", self.df['searchstring'].tolist()[:10])

    def _cleanse_strings(self, x):
        # Cleanse strings

        # Replace Nan by empty string
        x = self._replace_na_with_empty_string(x)
        # Remove redundant whitespaces
        x = re.sub(' +', ' ', x)
        x = " ".join(x.split())
        # Take out non-utf-8 characters
        return x

    def parts_list(self):
        return self.df


if __name__ == "__main__":
    print("Starting importer")
    importer = DataImporterUnionSpecial()
    # importer="xlrd-2.0.12"
