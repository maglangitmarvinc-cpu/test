"""Scatter-first enemy steering inspired by arcade maze patrols."""
import random

DIRECTIONS = {"up": (0,-1), "down": (0,1), "left": (-1,0), "right": (1,0)}
OPPOSITE = {"up":"down", "down":"up", "left":"right", "right":"left"}

def valid_directions(cell, direction, cols, rows, blocked):
    choices=[]
    for name,(dx,dy) in DIRECTIONS.items():
        if name == OPPOSITE[direction]: continue
        target=(cell[0]+dx,cell[1]+dy)
        if 0 <= target[0] < cols and 0 <= target[1] < rows and target not in blocked:
            choices.append(name)
    if not choices:
        for name,(dx,dy) in DIRECTIONS.items():
            target=(cell[0]+dx,cell[1]+dy)
            if 0 <= target[0] < cols and 0 <= target[1] < rows and target not in blocked:
                choices.append(name)
    return choices

def choose_direction(enemy, choices, player_cell, now):
    if not choices: return enemy.direction
    if enemy.personality == "PATROL":
        preferred = enemy.route[enemy.route_index % len(enemy.route)]
        if preferred in choices:
            enemy.route_index += 1
            return preferred
    # Brief pursuit is occasional; scatter and roaming remain the usual behavior.
    chase = enemy.personality == "CHASE" and now % 9.0 < 1.4
    if chase:
        best=[]
        distance=max(0,abs(player_cell[0]-enemy.cell[0])+abs(player_cell[1]-enemy.cell[1]))
        for name in choices:
            dx,dy=DIRECTIONS[name]
            if abs(player_cell[0]-(enemy.cell[0]+dx))+abs(player_cell[1]-(enemy.cell[1]+dy)) < distance:
                best.append(name)
        if best and random.random() < .55: return random.choice(best)
    if enemy.personality == "WANDER":
        local=[name for name in choices if abs(enemy.cell[0]+DIRECTIONS[name][0]-enemy.home[0]) <= 6
               and abs(enemy.cell[1]+DIRECTIONS[name][1]-enemy.home[1]) <= 5]
        if local: choices=local
    return random.choice(choices)
