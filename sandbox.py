import xml.dom

for const in dir(xml.dom.Node):
    if '__' in const: continue
    key = 'xml.dom.Node.%s' % const
    print '%2d => %s' % (eval(key), key)

from kotoba import misc, load_from_file

misc.debug_mode = True
kotoba = load_from_file('sandbox_data.xml')
nodes  = kotoba.find('created_at')

for node in nodes:
    node.dump('RESULT / A', True, True)
    print node.data()
    print

nodes  = kotoba.children('status')

for node in nodes:
    node.dump('RESULT / B', True, True)
    print
