'''Initialization file of talkingheads library'''
import logging

from .base_browser import *
from .object_map import *
from .utils import *
from .model_library import *

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.WARNING
)
