"""Non-blocking-from-the-UI LAN client; socket reads happen in a daemon thread."""
import socket, threading, queue
from .network import send_json, read_json_line

class SnakeClient:
    def __init__(self, host, port, username):
        self.host, self.port, self.username = host, int(port), username
        self.sock = None
        self.messages = queue.Queue()
        self.error = None
        self.connected = False

    def connect(self, timeout=5):
        sock = socket.create_connection((self.host, self.port), timeout=timeout)
        sock.settimeout(None)
        self.sock = sock
        self.stream = sock.makefile("rb")
        send_json(sock, {"type":"join", "username":self.username})
        self.connected = True
        threading.Thread(target=self._read_loop, daemon=True).start()

    def _read_loop(self):
        try:
            while True: self.messages.put(read_json_line(self.stream))
        except Exception as exc:
            self.error = str(exc)
            self.connected = False
            self.messages.put({"type":"disconnected", "message":self.error})

    def move(self, direction):
        if self.connected:
            try: send_json(self.sock, {"type":"move", "direction":direction})
            except OSError as exc: self.error = str(exc); self.connected = False

    def latest(self):
        result = None
        while True:
            try: result = self.messages.get_nowait()
            except queue.Empty: return result

    def close(self):
        self.connected = False
        if self.sock:
            try: self.sock.shutdown(socket.SHUT_RDWR)
            except OSError: pass
            try: self.sock.close()
            except OSError: pass
