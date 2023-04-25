
from pymize.proto import Item, Message
import websocket
import json
import asyncio
from threading import Thread
from multiprocessing import Process
from queue import Queue
from websockets.sync.client import connect

class Client():
    def __init__(self, server="localhost:9432"):
        self.items = {} # the item cache

        print("init of Client")
        self.url = server + "/api/socket"

        self.items = {}
        self.get_item_queues = {}
        self.sock = connect("ws://" + self.url)

        thread = Process(target=self.run)
        thread.start()

    #def run(self):
        #asyncio.run(self.sock.run())
        #loop = asyncio.get_running_loop()
        #loop.stop()
        #print("before run_until_complete")
        #loop.run_until_complete(self.sock.run(self.url))

        #self.sock.set_callback("item.give", self.on_give_message)

    def on_give_message(self, msg):
        pass
        #if msg.id in self.get_item_callbacks:
    
    def add_get_item_queue(self, ID, queue):
        if not ID in self.get_item_queues:
            self.get_item_queues[ID] = []
        self.get_item_queues[ID].append(queue)

    def rem_get_item_queue(self, ID, queue):
        if not ID in self.get_item_queues:
            return
        self.get_item_queues[ID].remove(queue)

    def get_item(self, ID):
        if ID in self.items:
            return self.items[ID]

        q = Queue()
        self.add_get_item_queue(ID, q)

        msg = {
                "cmd": "item.get",
                "id": "0",
        }
        self.send(msg)

        print("before queue")
        hi = q.get()
        print("after queue: ", hi)
        return hi

    def run(self):
        for message in self.sock:
            if type(message) == str:
                print("GOT: ", message)
                self.handle_msg(json.loads(message))

    def send(self, msg):
        self.sock.send(json.dumps(msg))
    
    def handle_msg(self, msg):
        match msg["cmd"]:
            case "item.give":
                item = Item(msg["item"])
                for queue in self.get_item_queues[msg["id"]]:
                    print("queue: ", queue)
                    queue.put(item)

                # set item in the cache
                self.items[msg["id"]] = item











