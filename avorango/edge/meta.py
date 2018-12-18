from stringcase import snakecase


class EdgeMeta(type):
    def __init__(cls, name, bases, attrs, **kwargs):
        if cls._session is not None:
            cls._collection = cls._session.collection(cls.collection_name)
        return super().__init__(name, bases, attrs)

    @property
    def collection_name(self):
        return self._collectionname if self._collectionname is not None \
            else snakecase(self.__name__)
