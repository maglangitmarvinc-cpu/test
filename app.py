"""SNAKE GAME: beginner-friendly Pygame front end for solo and LAN play."""
import socket, sys, random
import pygame
from settings import *
from database import ScoreDatabase
from snake import Snake, random_food
from multiplayer.server import SnakeServer
from multiplayer.client import SnakeClient

pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
CLOCK = pygame.time.Clock()
DB = ScoreDatabase()
FONT = pygame.font.Font(None, 28)
SMALL = pygame.font.Font(None, 22)
TITLE = pygame.font.Font(None, 72)

def label(text, x, y, color=WHITE, font=FONT, center=False):
    image = font.render(str(text), True, color)
    rect = image.get_rect(center=(x,y)) if center else image.get_rect(topleft=(x,y))
    SCREEN.blit(image, rect)

def button(text, y, index, total=5):
    rect = pygame.Rect(WIDTH//2-155, y, 310, 48)
    hover = rect.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(SCREEN, (42,78,62) if hover else PANEL, rect, border_radius=9)
    pygame.draw.rect(SCREEN, GREEN if hover else (52,76,70), rect, 2, border_radius=9)
    label(text, WIDTH//2, y+24, WHITE, FONT, True)
    return rect

def background():
    SCREEN.fill(BG)
    for x in range(0,WIDTH,40): pygame.draw.line(SCREEN,(18,27,33),(x,0),(x,HEIGHT))
    for y in range(0,HEIGHT,40): pygame.draw.line(SCREEN,(18,27,33),(0,y),(WIDTH,y))

def draw_board():
    pygame.draw.rect(SCREEN, (10,15,20), (BOARD_LEFT,BOARD_TOP,BOARD_COLS*CELL,BOARD_ROWS*CELL), border_radius=5)

def render_snake(body, color):
    for i,(x,y) in enumerate(body):
        rect=pygame.Rect(BOARD_LEFT+x*CELL+1,BOARD_TOP+y*CELL+1,CELL-2,CELL-2)
        pygame.draw.rect(SCREEN, color if i else tuple(min(255,c+20) for c in color),rect,border_radius=5)

def main():
    state="menu"; username=""; message=""; mode="Solo"; score=0; best=0
    snake=None; food=None; last_step=0; paused=False; game_over=False
    server=None; client=None; host_name=""; join_ip="127.0.0.1"; port_text="50505"; net_state=None; setup_field="username"
    running=True

    def start_solo():
        nonlocal snake, food, score, last_step, paused, game_over
        snake = Snake([(10,13),(9,13),(8,13)], "right")
        food = random_food(BOARD_COLS, BOARD_ROWS, set(snake.body))
        score = 0
        last_step = pygame.time.get_ticks()
        paused = False
        game_over = False

    def start_host():
        nonlocal server, state, message, host_name
        try:
            host_name = DB.ensure_user(username)[1]
            server = SnakeServer(int(port_text), host_name)
            server.start()
            state = "host_wait"
            message = "Waiting for a player to join..."
        except Exception as exc:
            message = str(exc)
            state = "host_setup"

    def start_join():
        nonlocal client, state, message
        try:
            DB.ensure_user(username)
            client = SnakeClient(join_ip, int(port_text), username)
            client.connect()
            state = "network"
            message = "Connected"
        except Exception as exc:
            message = str(exc)
            state = "join_setup"

    while running:
        now=pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: running=False
            elif event.type==pygame.KEYDOWN:
                if state in ("username","host_setup","join_setup"):
                    if event.key==pygame.K_ESCAPE:
                        state="menu" if state=="username" else "multi_menu"
                    elif event.key==pygame.K_TAB:
                        setup_field={"username":"port","port":"ip","ip":"username"}.get(setup_field,"username")
                    elif event.key==pygame.K_BACKSPACE:
                        if state=="join_setup" and setup_field=="ip": join_ip=join_ip[:-1]
                        elif setup_field=="port": port_text=port_text[:-1]
                        else: username=username[:-1]
                    elif event.key==pygame.K_RETURN:
                        if state=="username":
                            try: DB.ensure_user(username); best=DB.best_score(username); start_solo(); state="solo"
                            except Exception as exc: message=str(exc)
                        elif state=="host_setup": start_host()
                        elif state=="join_setup": start_join()
                    elif event.unicode.isprintable() and event.unicode not in "\r\n":
                        if setup_field=="port" and event.unicode.isdigit() and len(port_text)<5:
                            if port_text=="50505": port_text=""
                            port_text+=event.unicode
                        elif state=="join_setup" and setup_field=="ip" and (event.unicode.isalnum() or event.unicode in ".:-_") and len(join_ip)<50:
                            if join_ip=="127.0.0.1": join_ip=""
                            join_ip+=event.unicode
                        elif setup_field=="username" and len(username)<20: username+=event.unicode
                elif state=="solo" and event.key in (pygame.K_ESCAPE,pygame.K_p): paused=not paused
                elif state=="solo" and not paused and snake and snake.alive:
                    keymap={pygame.K_UP:"up",pygame.K_w:"up",pygame.K_DOWN:"down",pygame.K_s:"down",pygame.K_LEFT:"left",pygame.K_a:"left",pygame.K_RIGHT:"right",pygame.K_d:"right"}
                    if event.key in keymap: snake.steer(keymap[event.key])
                elif state in ("host_wait","network"):
                    keymap={pygame.K_UP:"up",pygame.K_w:"up",pygame.K_DOWN:"down",pygame.K_s:"down",pygame.K_LEFT:"left",pygame.K_a:"left",pygame.K_RIGHT:"right",pygame.K_d:"right"}
                    if event.key in keymap:
                        if state=="host_wait" and server: server.inputs[0]=keymap[event.key]
                        if state=="network" and client: client.move(keymap[event.key])
                elif state=="network_over" and event.key==pygame.K_ESCAPE:
                    state="menu"
                elif event.key==pygame.K_ESCAPE:
                    if client: client.close(); client=None
                    if server: server.stop(); server=None
                    state="menu"
            elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                pos=event.pos
                if state=="menu":
                    if button_hit(pos,180): username=""; setup_field="username"; message="Enter your username"; state="username"
                    elif button_hit(pos,238): username=""; state="multi_menu"
                    elif button_hit(pos,296): mode="Solo"; state="scores"
                    elif button_hit(pos,354): state="instructions"
                    elif button_hit(pos,412): running=False
                elif state=="multi_menu":
                    if button_hit(pos,250): username=""; setup_field="username"; state="host_setup"
                    elif button_hit(pos,310): username=""; setup_field="username"; state="join_setup"
                    elif button_hit(pos,390): state="menu"
                elif state=="scores":
                    if button_hit(pos,575): mode="Multiplayer" if mode=="Solo" else "Solo"
                    elif button_hit(pos,625): state="menu"
                elif state in ("instructions",):
                    if button_hit(pos,600): state="menu"
                elif state=="username":
                    if button_hit(pos,430):
                        try: DB.ensure_user(username); best=DB.best_score(username); start_solo(); state="solo"
                        except Exception as exc: message=str(exc)
                    elif button_hit(pos,490): state="menu"
                elif state in ("solo",) and game_over:
                    if button_hit(pos,420): start_solo(); game_over=False
                    elif button_hit(pos,480): state="scores"
                    elif button_hit(pos,540): state="menu"; game_over=False
                elif state in ("host_setup","join_setup"):
                    if pygame.Rect(WIDTH//2-170,250,340,42).collidepoint(pos): setup_field="username"
                    elif pygame.Rect(WIDTH//2-170,340,160,42).collidepoint(pos): setup_field="port"; port_text=""
                    elif state=="join_setup" and pygame.Rect(WIDTH//2+20,340,210,42).collidepoint(pos): setup_field="ip"; join_ip=""
                    if button_hit(pos,420): start_host() if state=="host_setup" else start_join()
                    elif button_hit(pos,480): state="multi_menu"
                elif state in ("host_wait","network"):
                    if button_hit(pos,610):
                        if client: client.close(); client=None
                        if server: server.stop(); server=None
                        state="menu"
                elif state=="network_over" and button_hit(pos,400):
                    if client: client.close(); client=None
                    if server: server.stop(); server=None
                    net_state=None; state="menu"

        background()
        if state=="menu":
            label("SNAKE GAME",WIDTH//2,98,GREEN,TITLE,True); label("A classic arcade game",WIDTH//2,143,MUTED,SMALL,True)
            for i,name in enumerate(("Play Solo","Local Multiplayer","High Scores","Instructions","Exit")): button(name,180+i*58,i)
        elif state=="username":
            label("SOLO GAME",WIDTH//2,150,GREEN,TITLE,True); label("Enter a username (1–20 characters)",WIDTH//2,255,WHITE,FONT,True)
            pygame.draw.rect(SCREEN,PANEL,(WIDTH//2-170,290,340,48),border_radius=7); label(username+"▏",WIDTH//2-150,302,WHITE)
            label(message,WIDTH//2,365,RED if "must" in message else MUTED,SMALL,True); button("Start",430,0); button("Back",490,1)
        elif state=="multi_menu":
            label("LAN MULTIPLAYER",WIDTH//2,155,GREEN,TITLE,True); button("Host Game",250,0); button("Join Game",310,1); button("Back",390,2)
        elif state in ("host_setup","join_setup"):
            label("HOST A GAME" if state=="host_setup" else "JOIN A GAME",WIDTH//2,130,GREEN,TITLE,True)
            label("Username",WIDTH//2-170,225,MUTED,SMALL); pygame.draw.rect(SCREEN,PANEL,(WIDTH//2-170,250,340,42),border_radius=7); label(username+"▏",WIDTH//2-155,260)
            label("Port",WIDTH//2-170,315,MUTED,SMALL); pygame.draw.rect(SCREEN,PANEL,(WIDTH//2-170,340,160,42),border_radius=7); label(port_text,WIDTH//2-155,350)
            if state=="join_setup":
                label("Host IP",WIDTH//2+20,315,MUTED,SMALL); pygame.draw.rect(SCREEN,PANEL,(WIDTH//2+20,340,210,42),border_radius=7); label(join_ip,WIDTH//2+32,350,WHITE,SMALL)
                label("Click a field or press Tab to switch fields.",WIDTH//2,400,MUTED,SMALL,True)
            label(message,WIDTH//2,398,RED,SMALL,True); button("Continue",420,0); button("Back",480,1)
        elif state=="solo":
            if not paused and not game_over and now-last_step >= max(65,145-score//20):
                head=snake.next_head(); grow=head==food
                if head[0]<0 or head[0]>=BOARD_COLS or head[1]<0 or head[1]>=BOARD_ROWS or head in (snake.body if grow else snake.body[:-1]):
                    snake.alive=False; game_over=True
                    try: DB.save_score(username,score,"Solo"); best=max(best,score)
                    except Exception as exc: message="Could not save score: "+str(exc)
                else:
                    snake.advance(grow)
                    if grow: score+=10; food=random_food(BOARD_COLS,BOARD_ROWS,set(snake.body))
                last_step=now
            draw_board(); render_snake(snake.body,GREEN)
            if food: pygame.draw.circle(SCREEN,RED,(BOARD_LEFT+food[0]*CELL+10,BOARD_TOP+food[1]*CELL+10),8)
            label(f"{username}   Score: {score}   Best: {best}",50,35,GREEN); label("P / Esc: pause",720,35,MUTED,SMALL)
            if paused or game_over:
                shade=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); shade.fill((0,0,0,175)); SCREEN.blit(shade,(0,0))
                label("PAUSED" if paused else "GAME OVER",WIDTH//2,280,GREEN if paused else RED,TITLE,True)
                if paused: label("Press P or Esc to resume",WIDTH//2,345,WHITE,FONT,True)
                else:
                    label(f"Final score: {score}",WIDTH//2,345,WHITE,FONT,True); button("Play Again",420,0); button("High Scores",480,1); button("Main Menu",540,2)
        elif state in ("host_wait","network"):
            if state=="host_wait":
                if server and server.state.get("type")=="state": net_state=server.state
                elif server and server.state.get("type")=="disconnected":
                    message=server.state.get("message","Disconnected")
                    net_state=None
                elif server and server.error: message="Disconnected: "+server.error
            elif client:
                latest=client.latest()
                if latest: net_state=latest
                if client.error:
                    message="Disconnected: "+client.error
                    net_state=None
            if net_state and net_state.get("type") in ("state","over"):
                draw_board()
                colors=[GREEN,BLUE]
                for i,body in enumerate(net_state["snakes"]): render_snake(body,colors[i])
                f=net_state.get("food")
                if f: pygame.draw.circle(SCREEN,RED,(BOARD_LEFT+f[0]*CELL+10,BOARD_TOP+f[1]*CELL+10),8)
                names=net_state.get("names",["Host","Player 2"]); scores=net_state.get("scores",[0,0])
                label(f"{names[0]}: {scores[0]}",55,35,GREEN); label(f"{names[1]}: {scores[1]}",620,35,BLUE)
                if net_state["type"]=="over":
                    a,b=net_state["alive"]; winner="Draw!" if a==b else (names[0] if a else names[1])+" wins!"
                    label(winner,WIDTH//2,HEIGHT-35,GREEN,TITLE,True)
                    if state=="host_wait":
                        for i in range(2):
                            try: DB.save_score(names[i],scores[i],"Multiplayer")
                            except Exception as exc: message="Could not save scores: "+str(exc)
                        state="network_over"
                    elif state=="network":
                        try:
                            player_index = names.index(username)
                            DB.save_score(username, scores[player_index], "Multiplayer")
                        except Exception as exc:
                            message="Could not save score: "+str(exc)
                        state="network_over"
            else:
                screen_title = "DISCONNECTED" if (server and server.error) or (client and client.error) else ("HOSTING GAME" if state=="host_wait" else "CONNECTING")
                label(screen_title,WIDTH//2,170,GREEN if screen_title!="DISCONNECTED" else RED,TITLE,True)
                label(message,WIDTH//2,255,WHITE,FONT,True)
                if state=="host_wait":
                    try: ip=socket.gethostbyname(socket.gethostname())
                    except OSError: ip="Check your network settings"
                    label(f"Host IP: {ip}     Port: {port_text}",WIDTH//2,310,GREEN,FONT,True)
                    if server and server.clients: label("Player connected!",WIDTH//2,365,BLUE,FONT,True)
                label("WASD / arrows to move   •   Esc to leave",WIDTH//2,HEIGHT-50,MUTED,SMALL,True)
            button("Return to Menu",610,0)
        elif state=="network_over":
            label("MATCH COMPLETE",WIDTH//2,160,GREEN,TITLE,True)
            if net_state:
                names=net_state.get("names",["Player 1","Player 2"])
                scores=net_state.get("scores",[0,0])
                alive=net_state.get("alive",[False,False])
                winner="Draw!" if alive[0]==alive[1] else (names[0] if alive[0] else names[1])+" wins!"
                label(winner,WIDTH//2,260,WHITE,FONT,True)
                label(f"{names[0]}: {scores[0]}     {names[1]}: {scores[1]}",WIDTH//2,320,GREEN,FONT,True)
            button("Return to Menu",400,0)
        elif state=="scores":
            label(f"{mode.upper()} HIGH SCORES",WIDTH//2,90,GREEN,TITLE,True); rows=DB.leaderboard(mode)
            label("RANK      PLAYER                         BEST SCORE",170,160,MUTED,SMALL)
            for i,row in enumerate(rows): label(f"{i+1:>2}             {row[0]:<24} {row[1]:>6}",185,200+i*30,WHITE if i else GREEN)
            if not rows: label("No completed games yet.",WIDTH//2,245,MUTED,FONT,True)
            button("Switch Mode",575,0); button("Main Menu",625,1)
        elif state=="instructions":
            label("HOW TO PLAY",WIDTH//2,95,GREEN,TITLE,True)
            lines=["Move with arrow keys or WASD. Eat red food to grow.","Each food adds 10 points; speed increases as your score grows.","Press P or Esc during solo play to pause and resume.","Walls and your own body end a solo game.","For LAN play, one computer hosts and shares its IP and port.","The other player chooses Join and enters that IP and port.","Allow TCP port 50505 through the host's firewall if prompted.","In multiplayer both snakes share one board; a collision eliminates you."]
            for i,line in enumerate(lines): label(line,115,205+i*39,WHITE,SMALL)
            button("Main Menu",600,0)
        pygame.display.flip(); CLOCK.tick(FPS)
    if client: client.close()
    if server: server.stop()
    pygame.quit(); return 0

def button_hit(pos,y): return pygame.Rect(WIDTH//2-155,y,310,48).collidepoint(pos)

if __name__=="__main__": sys.exit(main())
