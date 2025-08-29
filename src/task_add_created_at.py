from datetime import datetime


class MetaAddAttribute(type):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.created_at = str(datetime.now())


class RandomClass(metaclass=MetaAddAttribute):
    pass


if __name__ == "__main__":
    class_obj = RandomClass()
    print(class_obj.created_at)
