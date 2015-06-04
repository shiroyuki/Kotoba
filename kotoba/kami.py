class Kami(list):
    """ The list of :class:`kotoba.kotoba.Kotoba`. """
    def __init__(self):
        self.__registered_nodes = []

    def children(self, selector=None):
        result = Kami()

        for item in self:
            result.extend(item.children(selector))

        return result

    def find(self, selector):
        result = Kami()

        for item in self:
            result.extend(item.find(selector))

        return result

    def data(self):
        output = []

        for kotoba in self:
            output.append(kotoba.data())

        try:
            return ''.join(output)
        except TypeError as e:
            if len(output) == 0:
                return None

            if len(output) == 1:
                return output[0]

            return output

    def append(self, kotoba):
        if kotoba.guid() in self.__registered_nodes:
            return

        self.__registered_nodes.append(kotoba.guid())

        super(Kami, self).append(kotoba)

    def extend(self, other_kami):
        for kotoba in other_kami:
            self.append(kotoba)