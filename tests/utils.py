"""Utility functions"""

import os
from typing import Any, Dict
from datetime import datetime

def get_driver_arguments(name: str, no_user_data_dir: bool = False) -> Dict[str, Any]:
    """Returns the parameters to start client

    Args:
        name (str): name of the client
        no_user_data_dir (bool, optional): Sets user data dir to None. Defaults to True.

    Returns:
        Dict[str, Any]: Arguments to the client
    """

    return {
        "headless": True,
        "verbose": True,
        "auto_save": True,
        "save_path": f"artifacts/{name}_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S.csv')}",
        "user_data_dir": os.getenv('CHROME_USER_DATA_DIR') if not no_user_data_dir else None
    }
