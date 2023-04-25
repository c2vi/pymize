
from websockets.sync.client import connect
import json

class Message():
    pass

class Item():
    def __init__(self, main):
        self.main = main
        self.id = main["__item__"]










