"""
    Union Special Data Importer

    # TODO: Implement typed input (should be for database anyways).
    # TODO: Introduce UUIDs for each item (should be done once we push into the database)
"""
import os
import pandas as pd
from dotenv import load_dotenv

from screaper_backend.importer.utils import _cleanse_strings, _strip_first_dollar

load_dotenv()

class DataImporterBakerCustomers:

    def __init__(self):

        path = os.getenv("BakerCustomerList")
        df = pd.read_csv(path)

        pd.set_option("display.max_rows", None, "display.max_columns", None)

        print("df is: ", df.head())
        print("Cols: ", df.columns)
        print("Length: ", len(df))

        self.df = df.rename(columns={
            'user_name': 'user_name',
            'company_name': 'company_name',
            'domain_name': 'domain_name',
            'phone_number': 'phone_number',
            'fax_number': 'fax_number',
            'mobil_phone': 'mobile_phone',
            'email_(1)': 'email',
            'contact_nane (1)': 'contact_name'
        })

        for col in self.df.columns:
            if col in (
                    "user_name", "company_name", "domain_name",
                    "phone_number", "fax_number", "mobile_phone",
                    "email", "contact_name", "email_(2)", "contact_nane (2)"):
                self.df[col] = self.df[col].apply(_cleanse_strings)

        self.df['email'] += self.df['email_(2)'].apply(lambda x: ", " + x if x else "")
        self.df['contact_name'] += self.df['contact_nane (2)'].apply(lambda x: " / " + x if x else "")

        self.df = self.df[[
            'user_name',
            'company_name',
            'domain_name',
            'phone_number',
            'fax_number',
            'mobile_phone',
            'email',
            'contact_name'
        ]]

        print("self df is: ")
        print(self.df.head())

        self.df['user_name'] = self.df['email']

    def customers_list(self):
        return self.df


if __name__ == "__main__":
    print("Starting importer")
    importer = DataImporterBakerCustomers()
