import re

import pandas as pd
import numpy as np


def _cleanse_strings(x):
    # Cleanse strings

    # Replace Nan by empty string
    x = _replace_na_with_empty_string(x)
    # Remove redundant whitespaces
    x = re.sub(' +', ' ', x)
    x = " ".join(x.split())
    # Take out non-utf-8 characters
    return x


def _str_to_number(x):
    if isinstance(x, str):
        x = x.replace(",", "").replace("'", "")
    return float(x)


def _str_to_number_with_comma(x):
    if isinstance(x, str):
        x = x.replace(".", "").replace(",", ".").replace("'", "")
    return float(x)


def _replace_na_with_empty_string(x):
    if x == np.nan:
        return ''
    if not x:
        return ''
    if x is None:
        return ''
    if pd.isna(x):
        return ''
    return x


def _strip_first_dollar(x):
    x = x[1:]
    return _str_to_number_with_comma(x)
