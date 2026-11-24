"""Authoritative two-player TCP game server. The game loop runs in a worker thread."""
import socket, threading, time, queue
from snake import Snake, random_food
from settings import BOARD_COLS, BOARD_ROWS
from .network import send_json, read_json_line

class SnakeServer:
    def __init__(self, port=50505, host_name="Host"):
        self.port = int(port)
        self.host_name = host_name
        self.listener = None
        self.thread = None
        self.clients = []
        self.inputs = ["right", "left"]
        self.input_queue = queue.Queue()
        self.state = {"type":"waiting", "message":"Waiting for player 2"}
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.error = None

    def start(self):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind(("0.0.0.0", self.port))
        self.listener.listen(1)
        self.listener.settimeout(0.5)
        self.thread = threading.Thread(target=self._serve, daemon=True)
        self.thread.start()

    def _serve(self):
        try:
            while not self.stop_event.is_set():
                try:
                    conn, addr = self.listener.accept()
                    break
                except socket.timeout:
                    continue
            else:
                return
            conn.settimeout(None)
            self.clients.append(conn)
            stream = conn.makefile("rb")
            hello = read_json_line(stream)
            if hello.get("type") != "join": raise ValueError("Invalid join message")
            self.names = [self.host_name, str(hello.get("username", "Player 2"))[:20]]
            send_json(conn, {"type":"joined", "slot":1})
            threading.Thread(target=self._read_inputs, args=(stream,), daemon=True).start()
            self._run_game()
        except Exception as exc:
            self.error = str(exc)
            self.state = {"type":"disconnected", "message":str(exc)}
        finally:
            self.stop_event.set()
            for client in self.clients:
                try: client.close()
                except OSError: pass
            if self.listener:
                try: self.listener.close()
                except OSError: pass

    def _read_inputs(self, stream):
        try:
            while not self.stop_event.is_set():
                message = read_json_line(stream)
                if message.get("type") == "move": self.input_queue.put(message.get("direction"))
        except Exception:
            if not self.stop_event.is_set(): self.error = "A player disconnected"; self.stop_event.set()

    def _run_game(self):
        snakes = [Snake([(8,13),(7,13),(6,13)], "right"), Snake([(31,13),(32,13),(33,13)], "left")]
        scores = [0,0]
        food = random_food(BOARD_COLS, BOARD_ROWS, set(sum((s.body for s in snakes), [])))
        tick = 0
        while not self.stop_event.is_set():
            start = time.monotonic()
            try:
                while True: self.inputs[1] = self.input_queue.get_nowait()
            except queue.Empty: pass
            heads = []
            for i,snake in enumerate(snakes):
                if snake.alive: snake.steer(self.inputs[i]); heads.append(snake.next_head())
            for i,snake in enumerate(snakes):
                if not snake.alive: continue
                head = heads[i]
                grows = head == food
                body_to_hit = snake.body if grows else snake.body[:-1]
                other = snakes[1-i].body
                if (head[0] < 0 or head[0] >= BOARD_COLS or head[1] < 0 or head[1] >= BOARD_ROWS
                    or head in body_to_hit or head in other or (heads[0] == heads[1] and i == 0)):
                    snake.alive = False
                else:
                    snake.advance(grows)
                    if grows:
                        scores[i] += 10
                        food = random_food(BOARD_COLS, BOARD_ROWS, set(sum((s.body for s in snakes), [])))
            tick += 1
            self.state = {"type":"state", "snakes":[s.body for s in snakes], "scores":scores,
                          "names":getattr(self,"names",["Host","Player 2"]), "food":food,
                          "alive":[s.alive for s in snakes], "tick":tick}
            for client in self.clients:
                try: send_json(client, self.state)
                except OSError: raise ConnectionError("A player disconnected")
            if not all(s.alive for s in snakes):
                self.state["type"] = "over"
                for client in self.clients: send_json(client, self.state)
                return
            self.stop_event.wait(max(0.07, 0.15 - min(scores)/3000) - (time.monotonic()-start))

    def stop(self):
        self.stop_event.set()
        for client in self.clients:
            try: client.shutdown(socket.SHUT_RDWR)
            except OSError: pass
            try: client.close()
            except OSError: pass
