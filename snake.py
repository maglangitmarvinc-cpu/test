"""Grid-based snake rules shared by solo and network play."""
import random

class Snake:
    DIRECTIONS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
    OPPOSITE = {"up": "down", "down": "up", "left": "right", "right": "left"}

    def __init__(self, body, direction="right"):
        self.body = list(body)
        self.direction = direction
        self.pending = direction
        self.alive = True

    def steer(self, direction):
        if direction in self.DIRECTIONS and direction != self.OPPOSITE[self.direction]:
            self.pending = direction

    def next_head(self):
        dx, dy = self.DIRECTIONS[self.pending]
        x, y = self.body[0]
        return x + dx, y + dy

    def advance(self, grow=False):
        self.direction = self.pending
        self.body.insert(0, self.next_head())
        if not grow:
            self.body.pop()

def random_food(cols, rows, occupied):
    spaces = [(x,y) for x in range(cols) for y in range(rows) if (x,y) not in occupied]
    return random.choice(spaces) if spaces else None

