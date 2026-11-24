"""Grid movement with previous-position data for smooth visual interpolation."""
class Snake:
    DIRECTIONS = {"up": (0,-1), "down": (0,1), "left": (-1,0), "right": (1,0)}
    OPPOSITE = {"up":"down", "down":"up", "left":"right", "right":"left"}

    def __init__(self, start):
        self.body = [start, (start[0]-1,start[1]), (start[0]-2,start[1])]
        self.previous_body = list(self.body)
        self.direction = "right"
        self.pending = "right"
        self.alive = True
        self.growth = 0

    def turn(self, direction):
        if (self.pending == self.direction and direction in self.DIRECTIONS
                and direction != self.OPPOSITE[self.direction]):
            self.pending = direction

    def next_head(self):
        dx,dy = self.DIRECTIONS[self.pending]
        return self.body[0][0]+dx, self.body[0][1]+dy

    def advance(self, grow=False):
        self.previous_body = list(self.body)
        self.direction = self.pending
        self.body.insert(0, self.next_head())
        if grow or self.growth:
            if self.growth: self.growth -= 1
        else:
            self.body.pop()
