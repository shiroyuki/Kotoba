from . import misc

def node_debug_message(node, message, ignore_indentation=False):
    if not misc.debug_mode: return
    print ignore_indentation and message or '%s%s' % (' ' * node.level() * 2, message)
    
def is_string(ref):
    return type(ref) in [unicode, str]