import re
import subprocess
import logging
import platform

def detect_chrome_version(version_num=None):
    '''
        Detects chrome version, only supports linux and mac machines.
        If the command return something else than expected output, it uses the default version 112.
    '''

    if platform.system() == 'Windows':
        if not version_num:
            logging.warning('Windows detected, no version number is provided, default: 112')
            return 112
        return version_num or 112

    out = subprocess.check_output(['google-chrome', '--version'])
    out = re.search(r'Google\s+Chrome\s+(\d{3})', out.decode())
    _v = 112
    if not out:
        logging.info('Could\'nt locate chrome version, using default value: 112')
    else:
        _v = int(out.group(1))
        logging.info(f'The version is {_v}')

    return _v
