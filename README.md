# Snake Adventure

Snake Adventure is a five-world arcade game built with Python and Pygame CE. The board, snake, fruit, enemies, lighting, and scenery are drawn procedurally, so no art or audio downloads are required. The graphics use a raised-board, faux-3D style in Pygame; they are not a real-time 3D renderer.

## Install and launch on Windows

Install Python 3, open PowerShell in this folder, and run these commands (type only the commands, not the `PS ...>` prompt):

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

The project uses the Pygame CE distribution, imported in Python as `pygame`. A virtual environment keeps it separate from any previously installed Pygame package. Pygame CE publishes Windows wheels for current CPython versions. If pip still tries to build from source, check `py --version` and share the full install error.

## Play

- **Start Game** begins a campaign at the Forest. Gather five apples in each world to advance; all five worlds require 25 apples total.
- **Level Selection** lets you replay worlds already unlocked. Practice runs do not count as a full campaign victory.
- Use the arrow keys or WASD to steer. The snake cannot reverse directly into itself.
- Avoid the walls, themed obstacles, and roaming enemies. Enemies use scatter, wandering, patrol, and occasional chase behavior.
- Press P or Escape to pause/resume. In pause, restart the current world or return to the menu.
- The HUD buttons pause the game and toggle sound. Music and short effects are synthesized locally.

## Worlds

Forest, Jungle, City, Sea, and Volcano each have distinct colors, props, obstacle layouts, enemies, ambient particles, and generated music. Difficulty rises as snake movement speeds up and enemies move faster. Level unlocks are stored in `adventure_progress.json` beside the project.

## Project layout

- `app.py` — window, input, and screen flow
- `core/game.py` — level gameplay, scoring, progression, particles
- `core/level_manager.py` — level order and unlock persistence
- `core/collision.py` — grid collision rules
- `core/camera.py` — board-to-screen mapping
- `core/renderer.py` — procedural 2.5D world rendering
- `core/audio.py` — generated sound effects and ambient melodies
- `entities/` — snake, enemies, and obstacles
- `ai/enemy_ai.py` — patrol and scatter movement choices
- `levels/` — the five environment definitions
- `ui/screens.py` — menus, HUD, and overlays
- `requirements.txt` — Pygame CE dependency

The earlier LAN multiplayer modules and SQLite score database remain in the repository, but the new Adventure campaign currently runs as a single-player mode.
