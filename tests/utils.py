"""Utility functions"""

import os
from typing import Any, Dict
from datetime import datetime

def get_driver_arguments(name: str, incognito: bool = False) -> Dict[str, Any]:
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
        "auto_save": True,
        "save_path": f"artifacts/{name}_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S.csv')}",
        "driver_arguments": [
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--enable-logging",
            "--v=1",
            f"--log-file=artifacts/{name}_chrome.log",
            "--password-store=basic"
        ],
        "incognito": incognito,
        "user_data_dir": os.getenv('CHROME_USER_DATA_DIR')
    }
