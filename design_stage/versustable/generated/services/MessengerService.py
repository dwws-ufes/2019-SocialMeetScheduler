# -*- encoding: utf-8 -*-

from pycdi.utils import Singleton


@Singleton()
class MessengerService:
    def sendMessageToMailbox(self):
        raise NotImplementedError("# TODO: Implement this missing method")

    def sendMessageToUser(self):
        raise NotImplementedError("# TODO: Implement this missing method")

    def sendMessageTo(self):
        raise NotImplementedError("# TODO: Implement this missing method")
