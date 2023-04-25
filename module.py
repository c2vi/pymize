

#print("here in module/main.py, the name is: ", __name__)

#import sys
#sys.path.append("..")

from pymize.proto import Message

import websocket
#import rel


class Module():
    def __init__(self, module_name):
        print("version", Message.VERSION)
        self.module_name = module_name
        self.funcs = {}

    def run(self, url):
        # connect to socket
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp("ws://" + url,
                                    on_open=self.on_open,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close,
                                    header={"mize-module": "testing"}
                                )
        self.ws = ws

        ws.run_forever()  # Set dispatcher to automatic reconnection, 2 second reconnect delay if connection closed unexpectedly
        #rel.signal(2, rel.abort)  # Keyboard Interrupt
        #rel.dispatch()

        # listen for messages
        #on message call self.handle_mesage(message: bytes)

    def send(message):
        this.ws.send(message.bytes(), binary=True)

    def msg_get(self, func):
        self.msg_get_func = func

    def msg_update(self, func):
        self.msg_update_func = func
    
    #def msg_update(self, typ):
        #x = "hello"
        #def function_wrapper(func):
            #print("Before calling " + func.__name__)
            #self.funcs[typ] = func
            #print("After calling " + func.__name__)

        #return function_wrapper

    def on_message(self, ws, message):
        print("GOT MESSAGE")
        if type(message) == bytes:
            # if else all cmds
            msg = Message.from_bytes(message.data)
            if Message.raw[1] == Message.MSG_GET or Message.raw[1] == Message.MSG_GET_AND_SUB:
                self.msg_get_func("hi")
        else:
            print("This message is not of Type Binary")

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket closed")

    def on_open(self, ws):
        print("WebSocket Connection opened")




