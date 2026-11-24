"""Procedural 2.5D rendering: raised tiles, soft shadows, and lit sphere-like art."""
import math
import pygame
from settings import WIDTH, HEIGHT, COLS, ROWS, CELL, BOARD_LEFT, BOARD_TOP, BOARD_WIDTH, BOARD_HEIGHT, WHITE, MUTED, GOLD
from core.camera import grid_to_screen

def blend(a,b,t):
    return tuple(max(0,min(255,int(x+(y-x)*t))) for x,y in zip(a,b))

class Renderer:
    def __init__(self):
        self.small=pygame.font.Font(None,22)
        self.ambient=[[(i*71+19)%BOARD_WIDTH,(i*131+37)%BOARD_HEIGHT,(i%4)+1] for i in range(48)]

    def background(self,surface,game):
        c=game.config
        for y in range(0,HEIGHT,4):
            t=y/HEIGHT
            pygame.draw.rect(surface,blend(c.sky,c.floor,t*.42),(0,y,WIDTH,4))
        self._scenery(surface,game)
        self._board(surface,c)
        self._ambient(surface,game)

    def _scenery(self,surface,game):
        name=game.config.name
        if name in ("FOREST","JUNGLE"):
            base=(16,38,31) if name=="FOREST" else (8,31,27)
            for i in range(11):
                x=(i*139+27)%WIDTH
                h=90+(i*43)%140
                pygame.draw.rect(surface,base,(x,74,20,h),border_radius=8)
                crown=(32,79,48) if name=="FOREST" else (14,69,48)
                pygame.draw.circle(surface,crown,(x+8,75),34+(i*7)%20)
                pygame.draw.circle(surface,blend(crown,game.config.accent,.15),(x-13,90),20)
        elif name=="CITY":
            for i in range(13):
                x=i*96-10; w=70+(i*17)%30; h=105+(i*61)%130
                rect=pygame.Rect(x,145-h,w,h)
                pygame.draw.rect(surface,(24,31,59),rect,border_radius=4)
                pygame.draw.line(surface,(48,63,103),(x+4,145-h),(x+w-4,145-h),3)
                for wy in range(160-h,130,24):
                    for wx in range(x+10,x+w-8,23):
                        if (wx+wy+i)%3:
                            pygame.draw.rect(surface,(57,142,191) if (i+wx)%2 else (221,86,174),(wx,wy,5,8),border_radius=2)
        elif name=="SEA":
            for i in range(15):
                x=(i*89+21)%WIDTH
                pygame.draw.line(surface,(26,114,139),(x,80),(x+10,132),2)
                pygame.draw.circle(surface,(49,155,178),(x+8,104),10)
        else:
            pygame.draw.polygon(surface,(53,28,31),[(0,170),(145,65),(305,172),(415,81),(530,170),(760,69),(925,168),(1060,82),(1180,170),(1180,0),(0,0)])
            pygame.draw.circle(surface,(227,74,38),(930,87),43)
            pygame.draw.circle(surface,(255,133,45),(930,87),30)
        self._text(surface,game.config.name,40,42,blend(game.config.accent,(255,255,255),.15),30)
        self._text(surface,game.config.subtitle,42,74,(193,206,205),22)

    def _board(self,surface,config):
        x,y=BOARD_LEFT,BOARD_TOP
        shadow=pygame.Rect(x-12,y-6,BOARD_WIDTH+24,BOARD_HEIGHT+30)
        pygame.draw.rect(surface,(7,12,18),shadow.move(0,18),border_radius=22)
        pygame.draw.rect(surface,blend(config.floor,(8,12,18),.24),(x-11,y-10,BOARD_WIDTH+22,BOARD_HEIGHT+22),border_radius=18)
        pygame.draw.rect(surface,blend(config.accent,(10,14,19),.5),(x-6,y-5,BOARD_WIDTH+12,BOARD_HEIGHT+12),border_radius=14)
        for row in range(ROWS):
            for col in range(COLS):
                color=config.tile_a if (row+col)%2==0 else config.tile_b
                rect=pygame.Rect(x+col*CELL,y+row*CELL,CELL-1,CELL-1)
                pygame.draw.rect(surface,color,rect,border_radius=3)
                pygame.draw.line(surface,blend(color,(255,255,255),.045),(rect.x+3,rect.y+2),(rect.right-4,rect.y+2),1)
        pygame.draw.rect(surface,blend(config.accent,(255,255,255),.2),(x,y,BOARD_WIDTH,BOARD_HEIGHT),2,border_radius=6)

    def draw_world(self,surface,game):
        self.background(surface,game)
        self._obstacles(surface,game)
        self._apple(surface,game)
        self._enemies(surface,game)
        self._snake(surface,game)
        self._particles(surface,game)

    def _cell_center(self,cell):
        return grid_to_screen(*cell)

    def _orb(self,surface,center,radius,color,shadow=True):
        x,y=center
        if shadow:
            pygame.draw.ellipse(surface,(7,14,19),(x-radius,y+radius*.45,radius*2,radius*.7))
        pygame.draw.circle(surface,blend(color,(0,0,0),.34),(int(x),int(y+radius*.13)),int(radius))
        pygame.draw.circle(surface,color,(int(x-radius*.12),int(y-radius*.12)),int(radius*.86))
        pygame.draw.circle(surface,blend(color,(255,255,255),.46),(int(x-radius*.34),int(y-radius*.39)),max(2,int(radius*.23)))

    def _obstacles(self,surface,game):
        for ob in game.obstacles:
            x,y=self._cell_center(ob.cell); r=12; kind=ob.kind
            pygame.draw.ellipse(surface,(8,16,18),(x-14,y+8,29,10))
            if kind in ("tree","root","vine"):
                pygame.draw.rect(surface,(101,68,43),(x-8,y-10,16,23),border_radius=5)
                pygame.draw.circle(surface,(39,115,60),(x,y-8),14)
                pygame.draw.circle(surface,(83,157,72),(x-5,y-12),7)
            elif kind in ("rock","stone","boulder"):
                pygame.draw.ellipse(surface,(89,101,99),(x-14,y-10,28,24))
                pygame.draw.ellipse(surface,(147,157,145),(x-9,y-10,16,8))
            elif kind in ("log","wreck"):
                pygame.draw.ellipse(surface,(108,73,47),(x-15,y-8,31,17))
                pygame.draw.line(surface,(173,119,72),(x-9,y-3),(x+10,y-3),2)
            elif kind in ("bush","thorn","plant","coral"):
                color=(56,155,88) if kind!="coral" else (235,119,131)
                for off in (-8,0,8): pygame.draw.circle(surface,color,(x+off,y-3-abs(off)//2),8)
                pygame.draw.circle(surface,blend(color,(255,255,255),.34),(x-7,y-8),3)
            elif kind=="car":
                pygame.draw.rect(surface,(36,131,185),(x-14,y-8,28,17),border_radius=6)
                pygame.draw.rect(surface,(93,212,236),(x-7,y-7,14,7),border_radius=3)
                pygame.draw.circle(surface,(255,224,131),(x-9,y+7),3); pygame.draw.circle(surface,(255,224,131),(x+9,y+7),3)
            elif kind=="barrier":
                pygame.draw.rect(surface,(215,221,224),(x-13,y-8,26,16),border_radius=3)
                pygame.draw.line(surface,(246,104,82),(x-8,y+5),(x+1,y-5),4)
            elif kind=="hydrant":
                pygame.draw.rect(surface,(220,76,65),(x-7,y-10,14,21),border_radius=5)
                pygame.draw.circle(surface,(249,128,97),(x,y-9),6)
            elif kind=="mine":
                self._orb(surface,(x,y-1),10,(42,68,88))
                for a in range(0,360,60):
                    rad=math.radians(a); pygame.draw.circle(surface,(103,151,167),(int(x+math.cos(rad)*13),int(y+math.sin(rad)*13)),3)
            elif kind=="lava":
                pygame.draw.ellipse(surface,(255,84,27),(x-15,y-11,30,21))
                pygame.draw.ellipse(surface,(255,189,61),(x-9,y-6,17,11))
            elif kind=="crack":
                pygame.draw.line(surface,(255,98,38),(x-11,y+6),(x,y-8),3)
                pygame.draw.line(surface,(255,98,38),(x,y-8),(x+9,y+7),3)

    def _apple(self,surface,game):
        if game.apple is None: return
        x,y=self._cell_center(game.apple); r=11
        golden=game.apple_count==4
        color=(255,204,65) if golden else (235,57,63)
        pulse=1+(.06*math.sin(game.elapsed*8) if golden else .025*math.sin(game.elapsed*4))
        r=int(r*pulse)
        pygame.draw.ellipse(surface,(9,15,20),(x-12,y+8,25,9))
        pygame.draw.circle(surface,blend(color,(0,0,0),.35),(x,y+2),r)
        pygame.draw.circle(surface,color,(x-1,y-1),r-1)
        pygame.draw.circle(surface,blend(color,(255,255,255),.62),(x-4,y-5),3)
        pygame.draw.line(surface,(105,67,36),(x,y-r+2),(x+1,y-r-7),3)
        pygame.draw.ellipse(surface,(87,194,95),(x+2,y-r-7,10,5))
        if golden:
            for angle in range(0,360,60):
                px=x+int(math.cos(math.radians(angle))*17); py=y+int(math.sin(math.radians(angle))*17)
                pygame.draw.circle(surface,(255,226,119),(px,py),2)

    def _snake(self,surface,game):
        snake=game.snake
        t=max(0,min(1,game.step_timer/game.config.step_time))
        centers=[]
        for i,cell in enumerate(snake.body):
            old=snake.previous_body[min(i,len(snake.previous_body)-1)]
            px=old[0]+(cell[0]-old[0])*t
            py=old[1]+(cell[1]-old[1])*t
            mapped=grid_to_screen(px,py)
            centers.append((int(mapped[0]),int(mapped[1])))
        for a,b in zip(centers,centers[1:]): pygame.draw.line(surface,(16,103,89),a,b,20)
        for i,center in reversed(list(enumerate(centers))):
            color=(49,205,161) if i else (86,239,185)
            radius=11 if i else 14
            self._orb(surface,(center[0],center[1]+(1 if i else 0)),radius,color,shadow=False)
        if centers:
            hx,hy=centers[0]
            pygame.draw.circle(surface,(13,33,35),(hx+4,hy-3),2)
            pygame.draw.circle(surface,(13,33,35),(hx+4,hy+4),2)

    def _enemies(self,surface,game):
        colors={"FOX":(230,119,58),"HEDGEHOG":(156,115,73),"WOLF":(115,130,137),"OWL":(188,151,89),
                "MONKEY":(160,102,72),"SPIDER":(111,76,152),"SNAKE":(73,179,103),"PANTHER":(71,79,80),
                "DRONE":(70,174,211),"ROBOT":(151,175,187),"PATROL CAR":(221,88,78),"SENTINEL":(120,144,197),
                "SHARK":(99,157,193),"JELLYFISH":(199,109,206),"EEL":(84,207,173),"BARRACUDA":(105,175,195),
                "FIRE BAT":(151,69,75),"LAVA IMP":(242,89,43),"EMBER":(255,157,50),"FIRE SPIRIT":(254,124,52)}
        for enemy in game.enemies:
            t=min(1,enemy.timer*enemy.speed)
            x0,y0=self._cell_center(enemy.previous_cell); x1,y1=self._cell_center(enemy.cell)
            x=int(x0+(x1-x0)*t); y=int(y0+(y1-y0)*t)
            color=colors.get(enemy.kind,(205,112,89))
            pygame.draw.ellipse(surface,(8,15,19),(x-14,y+9,29,10))
            if enemy.kind in ("SPIDER","DRONE","FIRE BAT"):
                for side in (-1,1):
                    pygame.draw.line(surface,blend(color,(0,0,0),.3),(x+side*7,y+3),(x+side*14,y+10),2)
                    pygame.draw.line(surface,blend(color,(0,0,0),.3),(x+side*7,y-3),(x+side*14,y-10),2)
            if enemy.kind=="PATROL CAR":
                pygame.draw.rect(surface,blend(color,(0,0,0),.25),(x-15,y-9,30,18),border_radius=6)
                pygame.draw.rect(surface,(115,216,237),(x-7,y-7,14,8),border_radius=3)
                pygame.draw.circle(surface,(251,223,127),(x-10,y+8),3)
                pygame.draw.circle(surface,(251,223,127),(x+10,y+8),3)
                pygame.draw.circle(surface,(31,39,47),(x-9,y+9),3)
                pygame.draw.circle(surface,(31,39,47),(x+9,y+9),3)
            else:
                self._orb(surface,(x,y),12,color,shadow=False)
            if "FOX" in enemy.kind or enemy.kind=="LAVA IMP":
                pygame.draw.polygon(surface,color,[(x-9,y-7),(x-8,y-17),(x-1,y-9)])
                pygame.draw.polygon(surface,color,[(x+4,y-9),(x+10,y-17),(x+10,y-5)])
            pygame.draw.circle(surface,(247,240,214),(x-4,y-2),2)
            pygame.draw.circle(surface,(247,240,214),(x+4,y-2),2)
            pygame.draw.circle(surface,(22,28,35),(x-4,y-2),1)
            pygame.draw.circle(surface,(22,28,35),(x+4,y-2),1)

    def _particles(self,surface,game):
        for p in game.particles:
            x=BOARD_LEFT+int(p["x"]*CELL); y=BOARD_TOP+int(p["y"]*CELL)
            radius=max(1,int(4*p["life"]/p["max"]))
            pygame.draw.circle(surface,p["color"],(x,y),radius)
        accent=game.config.accent
        for i,(x,y,size) in enumerate(self.ambient):
            drift=(game.elapsed*(12+(i%5)*4))%BOARD_HEIGHT
            px=(x+math.sin(game.elapsed*.8+i)*16)%BOARD_WIDTH
            py=(y-drift)%BOARD_HEIGHT
            color=blend(game.config.floor,accent,.42)
            if game.config.ambient=="bubbles": pygame.draw.circle(surface,color,(BOARD_LEFT+int(px),BOARD_TOP+int(py)),size,1)
            elif game.config.ambient in ("sparks","leaves"): pygame.draw.polygon(surface,color,[(BOARD_LEFT+int(px),BOARD_TOP+int(py)-size),(BOARD_LEFT+int(px)+size,BOARD_TOP+int(py)),(BOARD_LEFT+int(px),BOARD_TOP+int(py)+size),(BOARD_LEFT+int(px)-size,BOARD_TOP+int(py))])
            else: pygame.draw.circle(surface,color,(BOARD_LEFT+int(px),BOARD_TOP+int(py)),size)

    def _text(self,surface,text,x,y,color,size=24):
        font=pygame.font.Font(None,size)
        surface.blit(font.render(str(text),True,color),(x,y))
