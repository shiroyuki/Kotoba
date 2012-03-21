from re        import sub, split
from .selector import Attribute, PathType, Selector

class MemoryBuffer(list):
    ''' Memory buffer for parser '''
    def flush(self):
        ''' Flush the buffer out as a string. '''
        flushed_string = []
        
        while self:
            flushed_string.append(self.pop())
        
        flushed_string.reverse()
        
        return ''.join(flushed_string)

class TokenizedSelectorBlock(object):
    ''' Template for Tokenized Selector Block '''
    def __init__(self):
        self.name           = None
        self.attributes     = set()
        self.pseudo_classes = set()

def selector(path):
    '''
    Parse a given *path* as the list of selector.
    '''
    
    selector = None
    path     = split(' ', sub('\s{2,}', ' ', path.strip()))
    
    previous_selector = None
    combinator        = None
    
    for p in path:
        if p in PathType.registered:
            combinator = PathType.registered.index(p)
            continue
        
        parsed_selector = selector_block(p)
        new_selector    = Selector(parsed_selector, combinator)
        combinator      = None
        
        if previous_selector:
            previous_selector.next(new_selector)
        
        previous_selector = new_selector
        
        if not selector:
            selector = new_selector
    
    return selector

def selector_block(raw_selector_block):
    '''
    Parse the *raw selector block*.
    
    .. note::
        This is a prototype code. The improvement is required.
    '''
    TOKENIZE_NAME         = 'name'
    TOKENIZE_ATTRIBUTE    = 'attr'
    TOKENIZE_PSEUDO_CLASS = 'pcls'
    
    token  = TokenizedSelectorBlock()
    memory = MemoryBuffer()
    current_step = TOKENIZE_NAME
    
    # Tokenized the raw block data.
    for ch in raw_selector_block:
        if ch == '[' and current_step == TOKENIZE_NAME:
            token.name   = memory.flush()
            current_step = TOKENIZE_ATTRIBUTE
        elif ch == ':' and current_step == TOKENIZE_NAME:
            token.name   = memory.flush()
            current_step = TOKENIZE_PSEUDO_CLASS
        elif ch == '[' and current_step == TOKENIZE_ATTRIBUTE:
            token.attributes.add(memory.flush())
        elif ch == ':' and current_step == TOKENIZE_ATTRIBUTE:
            token.attributes.add(memory.flush())
            current_step = TOKENIZE_PSEUDO_CLASS
        elif ch == ':' and current_step == TOKENIZE_PSEUDO_CLASS:
            token.pseudo_classes.add(memory.flush())
        
        memory.append(ch)
    
    # Finish the tokenization.
    if memory:
        leftover_buffer = memory.flush()
        
        if current_step == TOKENIZE_NAME:
            token.name = leftover_buffer
        elif current_step == TOKENIZE_ATTRIBUTE:
            token.attributes.add(leftover_buffer)
        elif current_step == TOKENIZE_PSEUDO_CLASS:
            token.pseudo_classes.add(leftover_buffer)
    
    return token
