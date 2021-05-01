"""
    Union Special Data Importer
"""
import os
import random

import pandas as pd
import uuid
from dotenv import load_dotenv

from screaper_backend.importer.utils import _cleanse_strings

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
            'contact_nane (1)': 'contact_name',
            "address": "address",
            "city": "city",
            "country": "country"
        })

        for col in self.df.columns:
            if col in (
                    "user_name", "company_name", "domain_name",
                    "phone_number", "fax_number", "mobile_phone",
                    "email", "contact_name", "email_(2)",
                    "contact_nane (2)", "address", "city",
                    "country"):
                self.df[col] = self.df[col].apply(_cleanse_strings)

        self.df['email'] += self.df['email_(2)'].apply(lambda x: ", " + x if x else "")
        self.df['contact_name'] += self.df['contact_nane (2)'].apply(lambda x: " / " + x if x else "")

        self.df = self.df[[
            'user_name',
            'company_name',
            'domain_name',
            'phone_number',
            'fax_number',
            # 'mobile_phone',
            'email',
            'contact_name'
        ]]

        print("self df is: ")
        print(self.df.head())

        # Create the same kind of UUIDs each time by setting the random seed
        rd = random.Random()
        rd.seed(0)
        uuid.uuid4 = lambda: uuid.UUID(int=rd.getrandbits(128))

        self.df['user_name'] = self.df['user_name'].apply(lambda x: str(uuid.uuid4()))

        # Drop duplicates by email
        # TODO: Gotta remove this sometime in future!
        if len(self.df['email']) - len(self.df['email'].drop_duplicates()):
            print("DUPLICATES IN EMAILS DETECTED! MAKE SURE TO CLEANSE THE FILE!")

        self.df = self.df.drop_duplicates(subset="email")

        # For each test-user, gotta add some dummy-data
        dummy_df = [
            {
                'user_name': "yenicelik",
                'company_name': "ETH Zürich",
                'domain_name': "theaicompany.com",
                'phone_number': None,
                'fax_number': None,
                'email': "yedavid@ethz.ch",
                'contact_name': "David Yenicelik"
            },
            {
                'user_name': "rayan.armani@gmail.com",
                'company_name': "rayan.armani@gmail.com",
                'domain_name': "rayan.armani@gmail.com",
                'phone_number': None,
                'fax_number': None,
                'email': "rayan.armani@gmail.com",
                'contact_name': "rayan.armani@gmail.com"
            },
            {
                'user_name': "tiankongguangzi@gmail.com",
                'company_name': "tiankongguangzi@gmail.com",
                'domain_name': "tiankongguangzi@gmail.com",
                'phone_number': None,
                'fax_number': None,
                'email': "tiankongguangzi@gmail.com",
                'contact_name': "tiankongguangzi@gmail.com"
            },
            {
                'user_name': "spacephoton@gmail.com",
                'company_name': "spacephoton@gmail.com",
                'domain_name': "spacephoton@gmail.com",
                'phone_number': None,
                'fax_number': None,
                'email': "spacephoton@gmail.com",
                'contact_name': "spacephoton@gmail.com"
            },
            {
                'user_name': "ivan.hanselmann@sph.ethz.ch",
                'company_name': "ivan.hanselmann@sph.ethz.ch",
                'domain_name': "ivan.hanselmann@sph.ethz.ch",
                'phone_number': None,
                'fax_number': None,
                'email': "ivan.hanselmann@sph.ethz.ch",
                'contact_name': "ivan.hanselmann@sph.ethz.ch"
            },
            {
                'user_name': "anton.moritz@sph.ethz.ch",
                'company_name': "anton.moritz@sph.ethz.ch",
                'domain_name': "anton.moritz@sph.ethz.ch",
                'phone_number': None,
                'fax_number': None,
                'email': "anton.moritz@sph.ethz.ch",
                'contact_name': "anton.moritz@sph.ethz.ch"
            },
            {
                'user_name': "sven98@me.com",
                'company_name': "sven98@me.com",
                'domain_name': "sven98@me.com",
                'phone_number': None,
                'fax_number': None,
                'email': "sven98@me.com",
                'contact_name': "sven98@me.com"
            },
            {
                'user_name': "laurin.paech@gmail.com",
                'company_name': "laurin.paech@gmail.com",
                'domain_name': "laurin.paech@gmail.com",
                'phone_number': None,
                'fax_number': None,
                'email': "laurin.paech@gmail.com",
                'contact_name': "laurin.paech@gmail.com"
            },
            {
                'user_name': "ldisse@student.ethz.ch",
                'company_name': "ldisse@student.ethz.ch",
                'domain_name': "ldisse@student.ethz.ch",
                'phone_number': None,
                'fax_number': None,
                'email': "ldisse@student.ethz.ch",
                'contact_name': "ldisse@student.ethz.ch"
            },
            {
                'user_name': "mcyenicelik@hotmail.com",
                'company_name': "mcyenicelik@hotmail.com",
                'domain_name': "mcyenicelik@hotmail.com",
                'phone_number': None,
                'fax_number': None,
                'email': "mcyenicelik@hotmail.com",
                'contact_name': "mcyenicelik@hotmail.com"
            },
            {
                'user_name': "baker@bakermagnetics.com.tr",
                'company_name': "baker@bakermagnetics.com.tr",
                'domain_name': "baker@bakermagnetics.com.tr",
                'phone_number': None,
                'fax_number': None,
                'email': "baker@bakermagnetics.com.tr",
                'contact_name': "baker@bakermagnetics.com.tr"
            },
            {
                'user_name': "auguryenicelik@hotmail.com",
                'company_name': "auguryenicelik@hotmail.com",
                'domain_name': "auguryenicelik@hotmail.com",
                'phone_number': None,
                'fax_number': None,
                'email': "auguryenicelik@hotmail.com",
                'contact_name': "auguryenicelik@hotmail.com"
            },
            {
                'user_name': "mcyenicelik@bakermagnetics.com.tr",
                'company_name': "mcyenicelik@bakermagnetics.com.tr",
                'domain_name': "mcyenicelik@bakermagnetics.com.tr",
                'phone_number': None,
                'fax_number': None,
                'email': "mcyenicelik@bakermagnetics.com.tr",
                'contact_name': "mcyenicelik@bakermagnetics.com.tr"
            }
        ]
        dummy_df = pd.DataFrame(dummy_df)

        self.df = pd.concat([self.df, dummy_df], axis=0)

    def customers_list(self):
        return self.df


if __name__ == "__main__":
    print("Starting importer")
    importer = DataImporterBakerCustomers()
