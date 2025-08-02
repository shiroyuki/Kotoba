import codecs
import json
import os
import re
from xml.dom.minidom   import parse, parseString

from .common    import is_string
from .driver    import JSONDriver, XMLDriver
from .kotoba    import Kotoba
from .exception import *

__all__ = ['Kotoba', 'load_from_file']

__version__ = (3, 2, 0)

def __load_xml(file_path):
    domDocument = parse(file_path)

    return XMLDriver(domDocument.documentElement)

def __load_json(file_path):
    with codecs.open(file_path) as f:
        obj = json.load(f)

    return JSONDriver(obj, 'root')

def load_from_file(file_path):
    """
    Load from the *filename*.

    :param file_path: the location of the data.

    :return: :class `kotoba.kotoba.Kotoba`: if the parser can parse the data.
    """
    if not os.path.exists(file_path):
        raise InvalidDataSourceError('The path {} is not found.'.format(file_path))

    if os.path.isdir(file_path):
        raise InvalidDataSourceError('The path {} is not a file.'.format(file_path))

    if re.search(r'\.json$', file_path, re.I):
        return Kotoba(__load_json(file_path))

    # default to XML
    return Kotoba(__load_xml(file_path))
