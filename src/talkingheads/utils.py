"""Utility functions of talkingheads library"""
import re
import subprocess
import logging
from typing import List, Union, Optional

import filetype
import validators


def check_filetype(filepath, extensions: List[str]) -> Optional[str]:
    """Checks if the given file is expected, return False if the extension
    is not included in expected extensions

    Args:
        filepath (str): the path to file
        extensions (List[str]): accepted file extensions

    Returns:
        Optional[str]: extension name if file extension exists in extension list, None otherwise
    """

    extension = filetype.guess_extension(filepath)
    return extension if extension in extensions else None


def is_url(possible_url: str) -> bool:
    """Checks if the given string is a valid url

    Args:
        possible_url (str): A string, possibly a url

    Returns:
        bool: True if possible_url is a valid url, false otherwise 
    """
    return validators.url(possible_url)


save_func_map = {
    "csv": "to_csv",
    "h5": "to_hdf",
    "html": "to_html",
    "json": "to_json",
    "orc": "to_orc",
    "pkl": "to_pkl",
    "xlsx": "to_xlsx",
    "xml": "to_xml",
}
