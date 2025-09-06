from datetime import datetime


class MetaAddAttribute(type):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls._created_at = datetime.now()

    @property
    def created_at(cls):
        return cls._created_at.isoformat()


class RandomClass(metaclass=MetaAddAttribute):
    pass


if __name__ == "__main__":
    print(RandomClass.created_at)
