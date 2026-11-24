"""Launch the five-world Snake Adventure."""
import sys
import pygame
from settings import WIDTH, HEIGHT, FPS, WHITE, MUTED, GOLD
from core.game import Game
from core.level_manager import LevelManager, LEVELS
from core.renderer import Renderer
from core.audio import Audio
from ui.screens import Screens

KEY_DIRECTIONS={pygame.K_UP:"up",pygame.K_w:"up",pygame.K_DOWN:"down",pygame.K_s:"down",
                pygame.K_LEFT:"left",pygame.K_a:"left",pygame.K_RIGHT:"right",pygame.K_d:"right"}

def main():
    pygame.init()
    screen=pygame.display.set_mode((WIDTH,HEIGHT))
    pygame.display.set_caption("Snake Adventure | Five Worlds")
    clock=pygame.time.Clock()
    game=Game(LevelManager())
    renderer=Renderer()
    ui=Screens()
    audio=Audio()
    audio.set_music(game.config)
    page="menu"
    running=True
    while running:
        dt=min(clock.tick(FPS)/1000.0,.05)
        mouse=pygame.mouse.get_pos()
        screen.fill((12,22,29))
        if page=="menu":
            buttons=ui.main_menu(screen,mouse,game.level_manager.unlocked)
        elif page=="levels":
            buttons=ui.level_select(screen,mouse,game.level_manager.unlocked)
        elif page=="settings":
            buttons=ui.settings(screen,mouse,audio.enabled)
        else:
            renderer.draw_world(screen,game)
            hud=ui.hud(screen,game,mouse,audio.enabled)
            if page=="game": buttons=hud
            elif page=="pause":
                buttons=ui.modal(screen,"PAUSED",["Take a breath, adventurer."],
                                 (("resume","RESUME"),("restart","RESTART LEVEL"),("menu","MAIN MENU")),mouse)
            elif page=="gameover":
                buttons=ui.modal(screen,"GAME OVER",[game.death_reason,f"Score: {game.score}  |  Apples: {game.total_apples}"],
                                 (("retry","RETRY LEVEL"),("menu","MAIN MENU")),mouse,(255,104,94))
            elif page=="victory":
                buttons=ui.modal(screen,"CONGRATULATIONS!",["YOU COMPLETED SNAKE ADVENTURE!",f"Total score: {game.score}  |  Apples: {game.total_apples}/25"],
                                 (("restart","RESTART GAME"),("menu","MAIN MENU")),mouse,GOLD)
            elif page=="leveldone":
                buttons=ui.modal(screen,"WORLD COMPLETE",[f"You conquered {game.config.name}.","Choose another unlocked world from the menu."],
                                 (("levels","LEVEL SELECTION"),("menu","MAIN MENU")),mouse,game.config.accent)
            elif page=="transition":
                next_name=LEVELS[game.level_index+1].name if game.level_index<len(LEVELS)-1 else "FINAL VICTORY"
                buttons=ui.modal(screen,"LEVEL COMPLETED",[f"{game.config.name} is safe!",f"Next environment: {next_name}"],(),mouse,game.config.accent)
            else:
                buttons={}

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE or (page=="game" and event.key==pygame.K_p):
                    if page=="game": page="pause"
                    elif page=="pause": page="game"
                    elif page not in ("menu",): page="menu"
                elif page=="game" and event.key in KEY_DIRECTIONS:
                    game.turn(KEY_DIRECTIONS[event.key])
            elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                action=next((name for name,rect in buttons.items() if rect.collidepoint(event.pos)),None)
                if page=="menu":
                    if action=="start": game.start(0,True); page="game"; audio.set_music(game.config)
                    elif action=="levels": page="levels"
                    elif action=="settings": page="settings"
                    elif action=="exit": running=False
                elif page=="levels":
                    if action=="back": page="menu"
                    elif action and action.startswith("level_"):
                        index=int(action.split("_")[1])
                        if index<=game.level_manager.unlocked:
                            game.start(index,False); page="game"; audio.set_music(game.config)
                elif page=="settings":
                    if action=="sound": audio.toggle()
                    elif action=="back": page="menu"
                elif page=="game":
                    if action=="pause": page="pause"
                    elif action=="sound": audio.toggle()
                elif page=="pause":
                    if action=="resume": page="game"
                    elif action=="restart": game.restart_level(); page="game"; audio.set_music(game.config)
                    elif action=="menu": page="menu"
                elif page=="gameover":
                    if action=="retry": game.restart_level(); page="game"; audio.set_music(game.config)
                    elif action=="menu": page="menu"
                elif page=="victory":
                    if action=="restart": game.start(0,True); page="game"; audio.set_music(game.config)
                    elif action=="menu": page="menu"
                elif page=="leveldone":
                    if action=="levels": page="levels"
                    elif action=="menu": page="menu"

        if page in ("game","transition","gameover","victory"):
            events=game.update(dt)
            for name in events:
                if name in ("move","apple","level","death"): audio.effect(name)
            if game.phase=="transition": page="transition"
            elif game.phase=="victory":
                if page!="victory":
                    page="victory"
                    audio.stop_music()
                    audio.effect("victory")
            elif game.phase=="gameover": page="gameover"
            elif game.phase=="leveldone": page="leveldone"
            elif page=="transition": page="game"; audio.set_music(game.config)
        pygame.display.flip()
    audio.toggle() if audio.enabled else None
    pygame.quit()
    return 0

if __name__=="__main__":
    sys.exit(main())
