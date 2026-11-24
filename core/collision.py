"""Collision rules for the snake moving one grid cell at a time."""
def collision_reason(head, cols, rows, obstacle_cells, body, enemy_cells, grows):
    if not (0 <= head[0] < cols and 0 <= head[1] < rows):
        return "You ran into the edge of the world."
    # The tail vacates its last tile on a normal move, so that tile is safe to enter.
    occupied_body=body[1:] if grows else body[1:-1]
    if head in occupied_body:
        return "You ran into your own tail."
    if head in obstacle_cells:
        return "obstacle"
    if head in enemy_cells or any(segment in enemy_cells for segment in body):
        return "enemy"
    return None
