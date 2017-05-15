from collections import defaultdict


class A:

    callbacks = defaultdict(dict)

    def process(self, value):
        class_name = self.__class__.__name__
        for condition, func in self.callbacks[class_name].items():
            if condition(value):
                func(self, value)

    @classmethod
    def add_process(cls, condition):
        def decorator(func):
            class_name = func.__qualname__.split('.')[0]
            cls.callbacks[class_name][condition] = func
            return func
        return decorator


class B(A):

    @A.add_process(lambda value: value > 5)
    def greater_than_five(self, value):
        print('greater than five')


class C(A):

    @A.add_process(lambda value: value % 2)
    def is_odd(self, value):
        print('is odd')


foo = B()
print(1)
foo.process(1)
print(10)
foo.process(10)
