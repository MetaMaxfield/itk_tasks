class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton1(metaclass=MetaSingleton):
    pass


class Singleton2:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance


class _Singleton3:
    pass


singleton_obj = _Singleton3()


if __name__ == "__main__":
    s1 = Singleton1()
    s2 = Singleton1()
    assert id(s1) == id(s2)

    s3 = Singleton2()
    s4 = Singleton2()
    assert id(s3) == id(s4)
