from os.path           import exists
from xml.dom.minidom   import parse, parseString
from xml.parsers.expat import ExpatError

from .common import is_string
from .kotoba import Kotoba

__version__ = '3.0-DEV'

def __load(data, from_file=True):
    if not is_string(data):
        raise InvalidDataSourceError
    
    domDocument = from_file and parse(data) or parseString(data)
    
    return domDocument.documentElement

def load_from_file(filename):
    """
    Load from the *filename*.
        
    :param `filename`: the location of the data.
        
    :return: :class `kotoba.kotoba.Kotoba`: if the parser can parse the data.
    """ 
    if not exists(filename):
        return None
    
    try:
        node = __load(filename)
    except ExpatError:
        return None
        
    return Kotoba(node)
    
def load_from_string(self, content):
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
