import re
import subprocess
import logging

def detect_chrome_version():
    '''
        Detects chrome version, only supports linux and mac machines.
        If the command return something else than expected output, it uses the default version 112.
    '''
    out = subprocess.check_output(['google-chrome', '--version'])
    out = re.search(r'Google\s+Chrome\s+(\d{3})', out.decode())
    _v = 112
    if not out:
        logging.info('Could\'nt locate chrome version, using default value: 112')
    else:
        _v = int(out.group(1))
        logging.info(f'The version is {_v}')

    return _v
