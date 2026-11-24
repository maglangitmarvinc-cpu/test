"""Length-independent newline-delimited JSON helpers for TCP sockets."""
import json

def send_json(sock, message):
    sock.sendall((json.dumps(message, separators=(",", ":")) + "\n").encode("utf-8"))

def read_json_line(file_obj):
    line = file_obj.readline()
    if not line:
        raise ConnectionError("Peer disconnected")
    return json.loads(line.decode("utf-8"))
