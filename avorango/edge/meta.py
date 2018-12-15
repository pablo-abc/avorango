from stringcase import snakecase


class EdgeMeta(type):
    def __init__(cls, name, bases, attrs, **kwargs):
        if cls._session is not None:
            cls._edge = cls._session.edge_collection(cls.edge_name)
        return super().__init__(name, bases, attrs)

    @property
    def edge_name(self):
        return self._edgename if self._edgename is not None \
            else snakecase(self.__name__)
