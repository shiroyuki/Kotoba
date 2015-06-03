from os.path           import exists
from xml.dom.minidom   import parse, parseString
from xml.parsers.expat import ExpatError

from .common    import is_string
from .driver    import XMLDriver
from .kotoba    import Kotoba
from .exception import *

__version__ = (3, 1, 0)

def __load_xml(data, from_file=True):
    if not is_string(data):
        raise InvalidDataSourceError('Expected a string.')

    domDocument = from_file and parse(data) or parseString(data)

    return XMLDriver(domDocument.documentElement)

def load_from_file(filename):
    """
    Load from the *filename*.

    :param `filename`: the location of the data.

    :return: :class `kotoba.kotoba.Kotoba`: if the parser can parse the data.
    """
    if not exists(filename):
        raise InvalidDataSourceError('File not found at {}'.format(filename))

    node = __load_xml(filename)

    return Kotoba(node)

# Disabled until the API is stable.
def __load_from_string(self, content):
    """
    Load from the *content*.

    :param `content`: the content of the data.

    :return: :class `kotoba.kotoba.Kotoba`: if the parser can parse the data.
    """
    try:
        node = __load(content, False)
    except ExpatError:
        return None

    return Kotoba(node)
