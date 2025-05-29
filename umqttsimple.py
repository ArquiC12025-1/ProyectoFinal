import usocket as socket
import ustruct as struct
from ubinascii import hexlify

class MQTTClient:
    def __init__(self, client_id, server, port=1883, user=None, password=None, keepalive=0):
        self.client_id = client_id
        self.sock = None
        self.addr = socket.getaddrinfo(server, port)[0][-1]
        self.server = server
        self.port = port
        self.user = user
        self.pswd = password
        self.keepalive = keepalive
        self.cb = None
        self.last_ping = 0

    def set_callback(self, f):
        self.cb = f

    def connect(self):
        self.sock = socket.socket()
        self.sock.connect(self.addr)
        packet = bytearray()
        packet.extend(b"\x10\x00\x00\x00\x00\x00\x00\x00")
        self.sock.send(packet)

    def disconnect(self):
        if self.sock:
            self.sock.close()
            self.sock = None

    def publish(self, topic, msg):
        pkt = bytearray(b"\x30")
        pkt.append(len(topic) + len(msg) + 2)
        pkt.extend(struct.pack("!H", len(topic)))
        pkt.extend(topic)
        pkt.extend(msg)
        self.sock.send(pkt)

    def subscribe(self, topic):
        pkt = bytearray(b"\x82")
        pkt.append(len(topic) + 5)
        pkt.extend(b"\x00\x01")  # Packet identifier
        pkt.extend(struct.pack("!H", len(topic)))
        pkt.extend(topic)
        pkt.append(0)  # QoS 0
        self.sock.send(pkt)

    def check_msg(self):
        self.sock.settimeout(0.1)
        try:
            res = self.sock.recv(1)
            if res == b'\x30':  # PUBLISH packet
                length = self.sock.recv(1)[0]
                topic_length = struct.unpack("!H", self.sock.recv(2))[0]
                topic = self.sock.recv(topic_length)
                msg = self.sock.recv(length - topic_length - 2)
                if self.cb:
                    self.cb(topic, msg)
        except:
            pass
