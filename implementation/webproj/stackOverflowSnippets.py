class StackOverflowCopypaste:
    __doc__ = None
    __author__ = None
    __license__ = 'CC BY-SA 3.0'

    def __str__(self): return str(self.__call__)

    def __call__(self, module): pass


class StackOverflow21563930(StackOverflowCopypaste):
    __doc__ = 'https://stackoverflow.com/a/21563930'
    __author__ = 'piRSquared'

    def __call__(self, module):
        module_dict = module.__dict__
        return [
            defined_class for defined_class in module_dict.values() if (
                isinstance(defined_class, type) and defined_class.__module__ == module.__name__
            )
        ]


classes_in_module = StackOverflow21563930()
