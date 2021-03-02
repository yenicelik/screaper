"""
    Union Special Data Importer
"""
import os
import pandas as pd
from dotenv import load_dotenv

from screaper_backend.importer.utils import _cleanse_strings, _strip_first_dollar

load_dotenv()

class DataImporterFischbein:

    def __init__(self):

        path = os.getenv("FischbeinPartList")
        df = pd.read_csv(path)

        print("df is: ", df.head())
        print("Cols: ", df.columns)
        print("Length: ", len(df))

        # Implement description in another language
        self.df = df.rename(columns={
            'Part': "part_external_identifier",
            'Unit Price': 'manufacturer_price'
        })

        for col in self.df.columns:
            if col in ("part_external_identifier", "Description", "Product Group", "Sub Group"):
                continue
            self.df[col] = self.df[col].apply(_cleanse_strings)

        self.df['description_{}'.format('en')] = self.df['Description'] + " " + self.df['Product Group'] + " " + self.df['Sub Group']

        self.df['price_currency'] = "USD"
        self.df['manufacturer'] = "Fischbein"
        self.df['manufacturer_abbreviation'] = "FSBN"

        self.df = self.df[[
            "part_external_identifier",
            "manufacturer_price",
            'description_{}'.format('en'),
            'price_currency',
            'manufacturer',
            'manufacturer_abbreviation'
        ]]

        self.df['manufacturer_price'] = self.df['manufacturer_price'].apply(_strip_first_dollar)

        self.df = self.df.sort_values(by=["part_external_identifier"])

        self._generate_searchstrings()

        print("Prices are: ", self.df['manufacturer_price'])

    def _generate_searchstrings(self):

        # print("Adding ", self.df['part_external_identifier'])
        # Put more weight to the partnumber
        self.df['searchstring'] = self.df['part_external_identifier'].apply(_cleanse_strings)
        self.df['searchstring'] += " " + self.df['part_external_identifier'].apply(_cleanse_strings)
        self.df['searchstring'] += " " + self.df['part_external_identifier'].apply(_cleanse_strings)

        # print("Adding ", self.df['replaced_by'])
        self.df['searchstring'] += " " + self.df['manufacturer']
        self.df['searchstring'] += " " + self.df['manufacturer_abbreviation']

        # Put all descriptios into the identifiers
        for language in ['en']:
            # print("adding: ", self.df['description_{}'.format(language)])
            self.df['searchstring'] += " " + self.df['description_{}'.format(language)].apply(_cleanse_strings)

        self.df['searchstring'] = self.df['searchstring'].apply(_cleanse_strings)

        # Make all lowercase
        self.df['searchstring'] = self.df['searchstring'].apply(lambda x: x.lower())

        print("Search String", self.df['searchstring'].tolist()[:10])

    def parts_list(self):
        return self.df


if __name__ == "__main__":
    print("Starting importer")
    importer = DataImporterFischbein()
