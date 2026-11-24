"""Menu, HUD, and modal screens kept outside the game loop."""
import pygame
from settings import WIDTH,HEIGHT,WHITE,MUTED,GOLD,PANEL

class Screens:
    def __init__(self):
        self.font=pygame.font.Font(None,32)
        self.small=pygame.font.Font(None,23)
        self.title=pygame.font.Font(None,82)
        self.large=pygame.font.Font(None,58)

    def text(self,surface,value,pos,color=WHITE,font=None,center=False):
        image=(font or self.font).render(str(value),True,color)
        rect=image.get_rect(center=pos) if center else image.get_rect(topleft=pos)
        surface.blit(image,rect)
        return rect

    def button(self,surface,label,rect,mouse,disabled=False):
        hover=rect.collidepoint(mouse) and not disabled
        fill=(47,79,88) if hover else (28,43,54)
        edge=(91,211,187) if hover else (61,91,101)
        if disabled: fill=(25,34,41); edge=(46,57,63)
        pygame.draw.rect(surface,fill,rect,border_radius=12)
        pygame.draw.rect(surface,edge,rect,2,border_radius=12)
        self.text(surface,label,rect.center,(120,132,138) if disabled else WHITE,self.font,True)
        return rect

    def panel(self,surface,title,subtitle=None):
        rect=pygame.Rect(WIDTH//2-250,120,500,HEIGHT-180)
        pygame.draw.rect(surface,(8,14,20),(rect.x+7,rect.y+12,rect.w,rect.h),border_radius=24)
        pygame.draw.rect(surface,PANEL,rect,border_radius=24)
        pygame.draw.rect(surface,(60,94,103),rect,2,border_radius=24)
        self.text(surface,title,(WIDTH//2,166),GOLD,self.large,True)
        if subtitle: self.text(surface,subtitle,(WIDTH//2,207),MUTED,self.small,True)
        return rect

    def main_menu(self,surface,mouse,unlocked):
        rects={}
        self.text(surface,"SNAKE",(WIDTH//2,130),(83,231,177),self.title,True)
        self.text(surface,"ADVENTURE",(WIDTH//2,201),WHITE,self.large,True)
        self.text(surface,"A five-world journey through the wild",(WIDTH//2,250),MUTED,self.small,True)
        labels=(("start","START GAME"),("levels","LEVEL SELECTION"),("settings","SETTINGS"),("exit","EXIT"))
        for i,(key,label) in enumerate(labels):
            rect=pygame.Rect(WIDTH//2-170,320+i*66,340,52)
            rects[key]=self.button(surface,label,rect,mouse)
        self.text(surface,f"{unlocked+1} / 5 worlds unlocked",(WIDTH//2,650),MUTED,self.small,True)
        self._ornament(surface)
        return rects

    def _ornament(self,surface):
        x=WIDTH//2+280; y=410
        for i in range(8):
            pygame.draw.circle(surface,(23+i*4,92+i*9,81+i*4),(x+(i%2)*8,y+i*29),15-i//3)
        pygame.draw.circle(surface,(97,238,182),(x+4,y-13),19)

    def level_select(self,surface,mouse,unlocked):
        self.panel(surface,"CHOOSE A WORLD","Unlocked worlds are ready to explore")
        rects={}
        names=("FOREST","JUNGLE","CITY","SEA","VOLCANO")
        for i,name in enumerate(names):
            rect=pygame.Rect(WIDTH//2-190,240+i*64,380,50)
            rects[f"level_{i}"]=self.button(surface,f"{i+1:02d}   {name}" if i<=unlocked else f"LOCKED   {name}",rect,mouse,i>unlocked)
        rects["back"]=self.button(surface,"BACK",pygame.Rect(WIDTH//2-100,590,200,48),mouse)
        return rects

    def settings(self,surface,mouse,sound_enabled):
        self.panel(surface,"SETTINGS","Personalize your adventure")
        rects={}
        rects["sound"]=self.button(surface,"SOUND: ON" if sound_enabled else "SOUND: OFF",pygame.Rect(WIDTH//2-170,300,340,54),mouse)
        self.text(surface,"Arrow keys or WASD to move",(WIDTH//2,410),WHITE,self.font,True)
        self.text(surface,"P / ESC pauses   |   Collect 5 apples per world",(WIDTH//2,450),MUTED,self.small,True)
        rects["back"]=self.button(surface,"BACK",pygame.Rect(WIDTH//2-100,570,200,48),mouse)
        return rects

    def hud(self,surface,game,mouse,sound_enabled):
        c=game.config
        rect=pygame.Rect(190,35,800,82)
        pygame.draw.rect(surface,(8,15,22),rect,border_radius=17)
        pygame.draw.rect(surface,(63,89,98),rect,1,border_radius=17)
        self.text(surface,f"WORLD {game.level_index+1} / 5",(212,48),c.accent,self.small)
        self.text(surface,c.name,(212,74),WHITE,self.font)
        self.text(surface,f"APPLES  {game.apple_count}/5",(490,55),GOLD,self.font,True)
        self.text(surface,f"SCORE  {game.score}",(684,55),WHITE,self.font,True)
        rects={"pause":pygame.Rect(873,49,48,48),"sound":pygame.Rect(931,49,48,48)}
        self.button(surface,"II",rects["pause"],mouse)
        self.button(surface,"S" if sound_enabled else "X",rects["sound"],mouse)
        self.text(surface,f"SNAKE  {len(game.snake.body)}",(WIDTH-188,55),MUTED,self.small,True)
        return rects

    def modal(self,surface,title,lines,buttons,mouse,accent=GOLD):
        shade=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        shade.fill((3,8,13,192)); surface.blit(shade,(0,0))
        box=pygame.Rect(WIDTH//2-260,HEIGHT//2-210,520,420)
        pygame.draw.rect(surface,(13,23,31),box,border_radius=24)
        pygame.draw.rect(surface,accent,box,2,border_radius=24)
        self.text(surface,title,(WIDTH//2,box.y+66),accent,self.large,True)
        for i,line in enumerate(lines): self.text(surface,line,(WIDTH//2,box.y+135+i*36),WHITE if i==0 else MUTED,self.font if i==0 else self.small,True)
        rects={}
        for i,(key,label) in enumerate(buttons):
            rect=pygame.Rect(WIDTH//2-155,box.y+250+i*58,310,46)
            rects[key]=self.button(surface,label,rect,mouse)
        return rects
