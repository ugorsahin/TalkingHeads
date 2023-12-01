'''Utility functions of talkingheads library'''
import re
import subprocess
import logging
import platform

def detect_chrome_version(version_num : int = None):
    '''
    Detects the Google Chrome version on Linux and macOS machines.
    
    Parameters:
        version_num (int, optional): The chromedriver version number. Default: None.

    Returns:
        int: The detected Google Chrome version number.

    Note:
    - If version_num is provided, it will be returned without any detection.
    - For Windows machines, if version_num is not provided, a warning is logged, and the default version 112 is returned.
    - Uses subprocess to execute the 'google-chrome --version' command for detection.
    - If the command output doesn't match the expected format, it defaults to the version 112.
    - Logs information about the detected or default version using the logging module.
    '''
    default_version = 112

    if version_num:
        logging.debug('Version number is provided: %d', version_num)
        return version_num

    if platform.system() == 'Windows':
        if not version_num:
            logging.warning('Windows detected, no version number is provided, default: 112')
            return default_version
        return version_num

    out = subprocess.check_output(['google-chrome', '--version'])
    out = re.search(r'Google\s+Chrome\s+(\d{3})', out.decode())

    if not out:
        logging.info('Could\'nt locate chrome version, using default value: 112')
        version_num = default_version
    else:
        version_num = int(out.group(1))
        logging.info(f'The version is {version_num}')

    return version_num

save_func_map = {
    'csv' : 'to_csv',
    'h5' : 'to_hdf',
    'html' : 'to_html',
    'json' : 'to_json',
    'orc' : 'to_orc',
    'pkl' : 'to_pkl',
    'xlsx' : 'to_xlsx',
    'xml' : 'to_xml'
}
