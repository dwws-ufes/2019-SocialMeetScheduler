class StackOverflowCopypaste:
    __doc__ = None
    __author__ = None
    __license__ = 'CC BY-SA 3.0'

    def __str__(self): return str(self.__call__)

    def __call__(self, module): pass


class stackoverflow_a_21563930(StackOverflowCopypaste):
    __doc__ = 'https://stackoverflow.com/a/21563930'
    __author__ = 'piRSquared'

    def __call__(self, module):
        moduleDict = module.__dict__
        return [
            definedClass for definedClass in moduleDict.values() if (
                isinstance(definedClass, type) and definedClass.__module__ == module.__name__
            )
        ]


classesInModule = stackoverflow_a_21563930()
