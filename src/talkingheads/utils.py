"""Utility functions of talkingheads library"""
import re
import subprocess
import logging
from typing import List, Union

import filetype
from undetected_chromedriver import find_chrome_executable
import validators


def check_filetype(filepath, extensions: List[str]) -> bool:
    """Checks if the given file is expected, return False if the extension
    is not included in expected extensions

    Args:
        filepath (str): the path to file
        extensions (List[str]): accepted file extensions

    Returns:
        bool: True if file extension exists in extension list, False otherwise
    """

    extension = filetype.guess_extension(filepath)

    return extension in extensions


def detect_chrome_version(version_num: int = None) -> Union[int, None]:
    """
    Detects the Google Chrome version on Linux and macOS machines.

    Args
        version_num (int, optional): The chromedriver version number. Default: None.

    Returns:
        int: The detected Google Chrome version number.

    Note:
    - If version_num is provided, it will be returned without any detection.

    - Uses subprocess to execute the 'google-chrome --version' command for detection.

    - If the command output doesn't match the expected format, it returns None.

    - Logs information about the detected or default version using the logging module.
    """

    if version_num:
        logging.debug("Version number is provided: %d", version_num)
        return version_num

    chrome_path = find_chrome_executable()

    out = subprocess.check_output([chrome_path, "--version"])
    out = re.search(r"Google\s+Chrome\s+(\d{3})", out.decode())

    if not out:
        logging.error("There was an error obtaining Chrome version")
        return None

    version_num = int(out.group(1))
    logging.info("The version is %d", version_num)
    return version_num


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
