class IDriver(object):
    def name(self):
        raise NotImplementedError('Interface method not implemented')

    def attributes(self):
        raise NotImplementedError('Interface method not implemented')

    def children(self):
        raise NotImplementedError('Interface method not implemented')

    def value(self):
        raise NotImplementedError('Interface method not implemented')

    def is_element(self):
        raise NotImplementedError('Interface method not implemented')

    def is_comment(self):
        raise NotImplementedError('Interface method not implemented')

    def is_data(self):
        raise NotImplementedError('Interface method not implemented')

    @staticmethod
    def initialize_children(kotoba_node):
        raise NotImplementedError('Interface method not implemented')

class JSONDriver(IDriver):
    def __init__(self, node, name=None):
        self.node = node
        self._name = str(name)
        self._children = []

    def name(self):
        return self._name

    def attributes(self):
        return { str(k): str(v) for k, v in self.children() }

    def children(self):
        if self._children:
            return self._children

        if isinstance(self.node, list):
            children = []
            index    = 0

            for item in self.node:
                children.append((index, item))
                index += 1

            self._children = children

            return children

        if isinstance(self.node, dict):
            children = []

            for k in self.node:
                children.append((k, self.node[k]))

            self._children = children

            return children

        return [] # The node is not iterable.

    def value(self):
        return self.node

    def iterable(self):
        return len(self.children()) > 0

    def is_element(self):
        return True

    def is_comment(self):
        return False

    def is_data(self):
        return not self.iterable()

    @staticmethod
    def initialize_children(kotoba_node):
        for name, original_child_node in kotoba_node._node.children():
            node_wrapper = kotoba_node._node.__class__(original_child_node, name) # Instantiate the same node driver.
            child_node   = kotoba_node.__class__(node_wrapper, kotoba_node.level() + 1)

            child_node.parent(kotoba_node)
            kotoba_node.adjacents().append(child_node)

            if child_node.is_element():
                kotoba_node._children.append(child_node)

    @staticmethod
    def retrieve_data(kotoba_node):
        return kotoba_node.original_value()

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

    @staticmethod
    def initialize_children(kotoba_node):
        for original_child_node in kotoba_node._node.children():
            node_wrapper = kotoba_node._node.__class__(original_child_node) # Instantiate the same node driver.
            child_node   = kotoba_node.__class__(node_wrapper, kotoba_node.level() + 1)

            if (child_node.is_data() and not child_node.original_value()) or child_node.is_comment():
                continue

            child_node.parent(kotoba_node)
            kotoba_node.adjacents().append(child_node)

            if child_node.is_element():
                kotoba_node._children.append(child_node)

    @staticmethod
    def retrieve_data(kotoba_node):
        data_list = []

        for child in kotoba_node.children(None, True):
            if child.is_data():
                data = child.original_value()

                data_list.append(data)

                continue

            data_list.append(child.data())

        return ''.join(data_list)