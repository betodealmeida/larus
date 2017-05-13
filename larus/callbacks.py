class Callbacks:

    def __init__(self):
        self.callbacks = {}

    def add_process(self, condition):
        def decorator(func):
            self.callbacks[condition] = func
            return func
        return decorator


class A:

    callbacks = Callbacks()

    def process(self, value):
        for condition, func in self.callbacks.callbacks.items():
            if condition(value):
                func(self, value)


class B(A):

    callbacks = Callbacks()

    @callbacks.add_process(lambda value: value > 5)
    def greater_than_five(self, value):
        print('greater than five')


class C(A):

    callbacks = Callbacks()

    @callbacks.add_process(lambda value: value % 2)
    def is_odd(self, value):
        print('is odd')


foo = B()
print(1)
foo.process(1)
print(10)
foo.process(10)
