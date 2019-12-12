# -*- encoding: utf-8 -*-

from pycdi.utils import Singleton


@Singleton()
class FriendService:
    def startFriendshipWith(self):
        raise NotImplementedError("# TODO: Implement this missing method") 
    
    def breakFriendshipWith(self):
        raise NotImplementedError("# TODO: Implement this missing method") 
    
    def isFriendOf(self):
        raise NotImplementedError("# TODO: Implement this missing method") 
    
    def friends(self):
        raise NotImplementedError("# TODO: Implement this missing method") 
    