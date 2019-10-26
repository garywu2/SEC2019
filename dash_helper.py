"""Helper functions for dash layout and callbacks."""
import base64
import io
import re

import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd


def parse_contents(contents, filename):
    df_json = []
    filename_valid, filename = _check_filename(filename)
    if filename_valid is False:
        return None

    try:
        df = _get_ds_dataframe(contents)
        df_json = df.to_json(orient="split", date_format="iso", date_unit="ns")

    except Exception as e:
        print(e)
        print("There was an error processing this file.")

    return df_json


def read_json(json_list):
    df_list = []
    try:
        for json in json_list:
            df = pd.read_json(json, orient="split", date_unit="ns")
            df_list.append(df)
    except Exception as e:
        print("Failed to read dataframe from json")
        print(e)
    return df_list


def lv_form(list_labels, list_values=None):
    if list_values is None:
        list_values = list_labels
    return [{'label': label, 'value': value} for label, value in zip(list_labels,
                                                                     list_values)]

def name_ID_form(list_labels, list_values=None):
    if list_values is None:
        list_values = list_labels
    return [{'name': label, 'id': value} for label, value in zip(list_labels,
                                                                     list_values)]



def duplicate_filename_check(filenames):
    seen = set()
    for filename in filenames:
        filename = filename[0:31]
        if filename in seen:
            return True
        seen.add(filename)
    return False



def remove_bad_files(children, filenames):
    indices_to_remove = [index for index, child in enumerate(children) if child is None]
    for index in sorted(indices_to_remove, reverse=True):
        del filenames[index]
    children = list(filter(None, children))
    return children, filenames


def _get_ds_dataframe(contents):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    return df


def remove_file_extension(filenames):
    """ Removes .csv extension.

    Args:
        filenames: A list of filenames ending with .csv.

    Returns: A list of filenames without their .csv extension.

    """
    return [re.sub(r"\.csv$", "", filename) for filename in filenames]


def _check_filename(filename):
    # Check file type
    if 'csv' not in filename:
        return False, filename

    # Check for duplicate csv names
    # It compares the first 31 characters since they are used for the excel sheet name.
    # If there was duplicates then the excel sheet in the export would be overwritten
    # for each duplicate drill schedule.
    filename = re.sub(r"\.csv$", "", filename)
    return True, filename
