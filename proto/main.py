
class Message():
    VERSION = 1

    MSG_GET = 1
    MSG_GIVE = 2
    MSG_GET_VAL = 3
    MSG_GIVE_VAL = 4
    MSG_UNAUTHORIZED = 5
    MSG_SUB = 6
    MSG_UNSUB = 7
    MSG_UPDATE_REQUEST = 8
    MSG_UPDATE_DENY = 9
    MSG_UPDATE = 10
    MSG_DELETE = 11
    MSG_CREATE = 12
    MSG_CREATED_ID = 13
    MSG_UNSUPPORTED_VERSION = 14
    MSG_GET_AND_SUB = 15
    MSG_GET_FIELDS = 16
    MSG_ERROR = 17
    MSG_GIVE_FIELDS = 18

    def __init__(self, raw):
        self.raw = raw
        self.index = 2;
        self.has_metadata = (raw[1] >= 128)

    def get_metadata(self):
        if self.has_metadata:
            meta = ""
            while self.raw[self.index] != "}":
                meta.append(self.raw[self.index])
                self.index += 1
            meta.append("}")
        else:
            print("msg has no Metadata")

    def get_id():
        pass

    def get_u64():
        pass
    
    def get_u32():
        pass

    @classmethod
    def give(self, item, meta):
        msg = bytearray([Message.VERSION, Message.MSG_GIVE])

        # answer:
        # u8: version
        # u8: cmd (2 for give)
        # id: terminated by "/"
        # u32: num_of_fields
        # as often as num_of_fields:
            # u64: key_len
            # key_len: key
            # u64: val_len
            # val_len: val

        print(meta)
        msg.append(bytes(meta, "utf-8"))
        msg.append(bytes(item.id + "/", "utf-8"))

        num_of_fields = len(item.raw)
        msg.append(num_of_fields.u32_to_be_bytes())

        for field in item.raw:
            key_len = len(field[0])
            msg.append(u32_to_be_bytes(key_len))
            msg.append(field[0])

            val_len = len(field[1])
            msg.append(u32_to_be_bytes(val_len))
            msg.append(field[1])

        return Message(msg)

    @classmethod
    def update(item):
        pass


class Item():
    def __init__(self, raw, id):
        this.raw = raw
        this.id = id

    @classmethod
    def from_str(self, string_arr):
        raw = []
        for (key, val) in string_arr:
            raw.append((bytes(key, "utf-8"), bytes(val, "utf-8")))


def from_be_bytes(my_bytes):
    my_bytes.reverse()

    count = 0
    num = 0
    for i in my_bytes:
        num += i * 256 ** count
        count += 1

    return num;

def u64_to_be_bytes(num):
    my_bytes = []

    #compute digits
    while (true):
        digit = num % 256

        if (digit == 0 ):
            break

        my_bytes.append(digit)
        num = (num - digit) / 256

	#fill array with 0s
    while (len(my_bytes) < 8):
        my_bytes.append(0)

    return bytearray(my_bytes)

def u32_to_be_bytes(num):
    my_bytes = []

	#compute digits
    while (true):
        digit = num % 256

        if (digit == 0 ):
            break

        my_bytes.append(digit)
        num = (num - digit) / 256

    #fill array with 0s
    while (my_bytes.length < 4):
        my_bytes.append(0)

    return bytearray(my_bytes)



