"""A roaming level creature with a distinct scatter-style personality."""
from ai.enemy_ai import DIRECTIONS, valid_directions, choose_direction

class Enemy:
    PERSONALITIES=("RANDOM PATROL","WANDER","PATROL","CHASE")
    def __init__(self, kind, cell, speed, personality, index=0):
        self.kind=kind
        self.cell=cell
        self.previous_cell=cell
        self.home=cell
        self.speed=speed
        self.personality=personality
        self.direction=("left","down","up","left")[index % 4]
        self.route=("up","left","down","right")
        self.route_index=index % len(self.route)
        self.timer=0.0

    def update(self, dt, now, cols, rows, blocked, player_cell):
        self.timer += dt
        moved=False
        interval=1.0 / self.speed
        while self.timer >= interval:
            self.timer -= interval
            choices=valid_directions(self.cell,self.direction,cols,rows,blocked)
            if not choices: continue
            # Random scatter movement dominates; turns at intersections prevent sticking.
            at_junction=len(choices)>1
            if at_junction or self.personality in ("WANDER","RANDOM PATROL") or self.timer >= interval:
                self.direction=choose_direction(self,choices,player_cell,now)
            dx,dy=DIRECTIONS[self.direction]
            target=(self.cell[0]+dx,self.cell[1]+dy)
            if target in blocked or not (0 <= target[0] < cols and 0 <= target[1] < rows):
                self.direction=choose_direction(self,choices,player_cell,now)
                dx,dy=DIRECTIONS[self.direction]
                target=(self.cell[0]+dx,self.cell[1]+dy)
            self.previous_cell=self.cell
            self.cell=target
            moved=True
        return moved
