class IDriver(object):
    pass

class XMLDriver(IDriver):
    def __init__(self, node):
        self.node = node

    def name(self):
        return self.node.nodeName

    def attributes(self):
        keys = self.node.attributes.keys()

        return {
            k: self.node.attributes[k].value
            for k in keys
        }

    def children(self):
        for cnode in self.node.childNodes:
            yield cnode

    def value(self):
        return self.node.nodeValue

    def kind(self):
        return self.node.nodeType

    def is_element(self):
        return self.kind() == self.node.ELEMENT_NODE

    def is_comment(self):
        return self.kind() == self.node.COMMENT_NODE

    def is_data(self):
        return self.kind() in [self.node.CDATA_SECTION_NODE, self.node.TEXT_NODE]