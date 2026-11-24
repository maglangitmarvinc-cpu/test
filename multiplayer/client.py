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
        self.closed = threading.Event()

    def connect(self, timeout=5):
        """Start connecting in the background so the Pygame loop stays responsive."""
        threading.Thread(target=self._connect, args=(timeout,), daemon=True).start()

    def _connect(self, timeout):
        try:
            sock = socket.create_connection((self.host, self.port), timeout=timeout)
            if self.closed.is_set():
                sock.close()
                return
            sock.settimeout(None)
            self.sock = sock
            self.stream = sock.makefile("rb")
            send_json(sock, {"type":"join", "username":self.username})
            self.connected = True
            threading.Thread(target=self._read_loop, daemon=True).start()
        except Exception as exc:
            self.error = str(exc)
            self.messages.put({"type": "disconnected", "message": self.error})

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
            try:
                message = self.messages.get_nowait()
            except queue.Empty:
                return result
            # A final game state can arrive immediately before the socket closes.
            # Keep it instead of letting the following disconnect notice hide it.
            if message.get("type") == "over":
                result = message
            elif result is None:
                result = message

    def close(self):
        self.connected = False
        self.closed.set()
        if self.sock:
            try: self.sock.shutdown(socket.SHUT_RDWR)
            except OSError: pass
            try: self.sock.close()
            except OSError: pass
