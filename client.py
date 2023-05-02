
from pymize.proto import Item, Message
import websocket
import json
import asyncio
from threading import Thread
from multiprocessing import Process
from multiprocessing import Queue as MPQueue
from queue import Queue
#from websockets.sync.client import connect
from time import sleep
from copy import deepcopy



class ClientProcess():
    def __init__(self, server="localhost:9432"):
        self.items = {} # the item cache

        self.url = server + "/api/socket"

        self.items = {}
        self.get_item_queues = {}
        self.get_item_callbacks = {}
        self.update_callbacks = {}
        self.sock = websocket.WebSocket()
        self.sock.connect("ws://" + self.url)

        self.send_queue = MPQueue()
        self.recv_queue = MPQueue()

        self.proc = Process(target=self.proc)
        self.proc.start()

        self.thread = Thread(target=self.run, daemon=True)
        self.thread.start()

    def proc(self):
        import signal
        import sys

        #sock = websocket.WebSocket()
        #sock.connect("ws://" + url)

        thread = Thread(target=self.recv_from_sock)
        thread.start()

        while True:
            try:
                msg = self.send_queue.get()
                self.sock.send(json.dumps(msg, sort_keys=False))
                print("SENT", msg)
            except Exception as e:
                print("Couldn't send Message: ", e)
                return

        return

        def signal_handler(sig, frame):
            print("signal handler")
            sock.send_close(status=1000, reason=b"Closing")
            sys.exit(0)

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)


    def recv_from_sock(self):
        try:
            while True:
                message = self.sock.recv()
                if type(message) == str:
                    print("GOT: ", message)
                    self.recv_queue.put(json.loads(message))
        except Exception as e:
            print("The WebSocket Connection was closed: ", e)
            return

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
                "id": ID,
        }
        self.send(msg)

        hi = q.get()
        print("after queue: ", hi)
        return hi

    def terminate(self, status=1000, reason = b"Closing"):
        self.sock.send_close(status=staus, reason=reason)

    def run(self):
        while True:
            msg = self.recv_queue.get()
            self.handle_msg(msg)


    def send(self, msg):
        self.send_queue.put(msg)
    
    def handle_msg(self, msg):
        print("GOT: ", msg)
        match msg["cmd"]:
            case "item.give":
                item = Item(msg["item"])
                if msg["id"] in self.get_item_queues:
                    for queue in self.get_item_queues[msg["id"]]:
                        queue.put(item)

                if msg["id"] in self.get_item_callbacks:
                    for callback in self.get_item_callbacks[msg["id"]]:
                        callback(item)

                # set item in the cache
                self.items[msg["id"]] = item

            case "item.update":
                #vim.async_call(write_buffer, "CBs: " + self.update_callbacks)
                #print("UPDATE: ", self.update_callbacks)
                delta = msg["delta"]
                ID = msg["id"]
                
                if ID in self.update_callbacks:
                    old_item = self.items[ID]
                    new_item = self.apply_delta(old_item, delta)
                    update = {
                                "new": new_item,
                                "old": old_item,
                                "src": "got_update_msg",
                            }
                    #print("OLD", old_item)
                    #print("NEW", new_item)

                    for callback in self.update_callbacks[ID]:
                        callback(update)

    def add_get_item_callback(self, ID, callback):
        if not ID in self.get_item_callbacks:
            self.get_item_callbacks[ID] = []
        self.get_item_callbacks[ID].append(callback)


    def rem_get_item_callback(self, ID, callback):
        print("removed???")
        if not ID in self.get_item_callbacks:
            return
        self.get_item_callbacks[ID].remove(callback)


    def update_item(self, new_item, update_src):
        old_item = self.items[new_item.id]
        update = {
                    "new": new_item,
                    "old": old_item,
                    "src": update_src,
                }

        if new_item.id in self.update_callbacks:
            for callback in self.update_callbacks[str(new_item.id)]:
                callback(update)

        if update["src"] != "got_update_msg":
            # send update msg
            delta = self.get_delta(old_item, new_item)
            msg = {
                    "cmd": "item.update-req",
                    "id": new_item.id,
                    "delta": delta,
                }

        self.send(msg)


    def get_delta(self, old_item, new_item):
        
        if type(old_item) == Item:
            old_item = old_item.main

        if type(new_item) == Item:
            new_item = new_item.main

        ##vim.async_call(print, "get delta 1", old_item, new_item)

        deltas = []

        keys = list(old_item.keys()) + list(new_item.keys())
        keys = list(dict.fromkeys(keys))

        for key in keys:

            if key not in old_item:
                #if key is not found on old_item it must have been added
                #pr("added", key, old_item.main[key])
                deltas.append([[key], new_item[key]])

            elif key not in new_item:
                #if key is not found on new_item it must have been deleted
                deltas.append([[key]])

            elif type(new_item[key]) == dict or type(new_item[key]) == list:
                # if that path was not a object or array in the old item
                if type(old_item[key]) != dict or type(old_item[key]) != list:
                    deltas.append([[key], new_item[key]])
                    continue

                #if values are objects call recursivly on inner objects
                if type(new_item[key]) == list:
                    old = enumerate(old_item[key])
                    new = enumerate(new_item[key])
                else:
                    old = old_item[key]
                    new = new_item[key]

                vim.async_call(print, "get delta", old, new)
                
                inner_deltas = self.get_delta(old, new)

                #extend the path
                for inner in inner_deltas:
                    #change: [path, new_obj], path is an array of keys
                    inner[0] = [key] + inner[0]

                #and add to deltas
                deltas += inner_deltas

            elif old_item[key] != new_item[key]:
                #values are different 
                deltas.append([[key], new_item[key]])

            else:
                #values are the same
                #//do nothing
                pass

        return deltas
    
    def apply_delta_recursive(self, obj, path, val):
        #print("apply recursive")
        #print(obj)
        #print(path)
        #print(val)
        key = path[0]

        if len(path) == 1:
            if type(obj) == dict:
                obj[key] = val
            elif type(obj) == list:
                obj[key] = val
            else:
                obj = val

        else: 
            if type(obj) == dict:
                inner_obj = obj[key]
                path.pop(0)
                obj[key] = apply_delta_recursive(inner_obj, path, val)

            elif type(obj) == list:
                inner_obj = obj[key]
                path.pop(0)
                obj[key] = apply_delta_recursive(inner_obj, path, val)

            else:
                obj = val

        #print("NEW: ", obj)
        #print("##########################")
        return obj

    def apply_delta(self, item, delta):
        old_item = deepcopy(item.main)
        for [path, new_val] in delta:
            new_item = self.apply_delta_recursive(old_item, path, new_val)

        #print("apply delta", delta, old_val, new_val, sep="\n")
        return Item(new_item)
    
    def add_update_callback(self, ID, callback):
        if ID not in self.update_callbacks:
            self.update_callbacks[ID] = []

        self.update_callbacks[ID].append(callback)
            

def write_buffer(content):
    vim.current.buffer[:] = content






