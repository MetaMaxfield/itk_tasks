class SingletonMetaclass(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class MetaSingleton(metaclass=SingletonMetaclass):
    pass


class NewSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance


class _SingletonModule:
    pass


singleton_obj = _SingletonModule()


if __name__ == "__main__":
    s1 = MetaSingleton()
    s2 = MetaSingleton()
    assert id(s1) == id(s2)

    s3 = NewSingleton()
    s4 = NewSingleton()
    assert id(s3) == id(s4)
