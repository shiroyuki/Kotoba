from codecs  import open as fopen
from os.path import exists

from .exception import *

def read(location):
    if not exists(location):
        raise FileNotFoundError
    
    with fopen(location) as fp:
        content = fp.read()
    
    fp.close()
    
    return content