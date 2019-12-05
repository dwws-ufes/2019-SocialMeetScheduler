# -*- encoding: utf-8 -*-

class Objectify(object):
    def __init__(self, data=None):
        self.__dict__ = data if data is not None else dict()
