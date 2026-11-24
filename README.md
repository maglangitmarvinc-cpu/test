# Snake Game

A beginner-friendly Pygame Snake game with solo play, persistent SQLite scores, and two-player LAN play. The project uses only Python's standard library plus Pygame.

## Install and run

1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Install Pygame with `py -m pip install -r requirements.txt` (on systems without the Windows `py` launcher, use `python3 -m pip install -r requirements.txt`).
4. Start the game with `py app.py` (or `python3 app.py`).

The database `snake_game.db` is created beside `app.py` the first time the game starts. Usernames are local to each computer. Solo and multiplayer leaderboards are separate and show each player's best completed score.

## Solo play

Choose **Play Solo**, enter a username, then use arrow keys or WASD. Each red food item is worth 10 points. Speed increases as the score grows. Press P or Escape to pause/resume. Hitting a wall or your own body ends the game; the completed score is saved to SQLite.

## Play over a LAN

1. Both computers must be on the same Wi-Fi network or wired LAN. Install Python and this project on both.
2. On the host, start the game, choose **Local Multiplayer → Host Game**, enter a username and port (50505 by default), then choose Continue. Keep the host game open.
3. Find the host's LAN IPv4 address. On Windows, run `ipconfig` in Command Prompt and read the **IPv4 Address** under the active Wi-Fi or Ethernet adapter. Avoid VPN or virtual adapter addresses.
4. On the second computer, choose **Local Multiplayer → Join Game**, enter a username, the host's IPv4 address and the same port, then choose Continue.
5. Both players use arrow keys or WASD. The host's server is authoritative and runs the game state; scores and collisions are shared. A disconnect ends the session.

On Windows, allow Python through Windows Defender Firewall on **Private networks** when prompted. If no prompt appears, create an inbound TCP rule for port 50505 (or the port selected by the host), limited to Private profiles. Both machines should be on a trusted private network. The app does not contact an online service.

## Controls and screens

- Menu: Solo, LAN multiplayer, high scores, instructions, exit.
- Solo: Arrow keys/WASD to turn; P or Escape to pause/resume.
- Multiplayer: Arrow keys/WASD to turn; Escape returns to the menu.
- Press Tab in the host/join setup screen to cycle username, port, and host IP fields. You can also click a field. Backspace edits the selected field.

## Project files

- `app.py` — Pygame screens and application loop
- `snake.py` — shared snake and food rules
- `database.py` — SQLite schema and score queries
- `settings.py` — board and color settings
- `multiplayer/server.py` — authoritative threaded TCP host
- `multiplayer/client.py` — background-reading TCP client
- `multiplayer/network.py` — newline-delimited JSON protocol helpers
- `requirements.txt` — Pygame dependency
