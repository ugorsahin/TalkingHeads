"""Utility functions for screen saving"""

from typing import Dict, Any

def get_driver_arguments(name: str, incognito: bool = True) -> Dict[str, Any]:
    """Returns the parameters to start client

    Args:
        name (str): name of the client
        incognito (bool, optional): Defaults to True.

    Returns:
        Dict[str, Any]: Arguments to the client
    """

    return {
        "headless": True,
        "verbose": True,
        "driver_arguments": [
            "--disable-dev-shm-usage",
            "--enable-logging",
            "--v=1",
            f"--log-file=artifacts/{name}_chrome.log",
            "--password-store=basic"
        ],
        "incognito" : incognito,
        "user_data_dir" : "/home/circleci/talkingheads_userprofile"
    }
