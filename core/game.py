"""Playable five-stage Snake Adventure rules and timing."""
import random
from entities.enemy import Enemy
from entities.obstacle import Obstacle
from entities.snake import Snake
from core.level_manager import LEVELS
from core.collision import collision_reason
from settings import COLS, ROWS

class Game:
    def __init__(self, level_manager):
        self.level_manager=level_manager
        self.phase="menu"
        self.score=0
        self.total_apples=0
        self.level_index=0
        self.campaign=True
        self.particles=[]
        self.elapsed=0.0

    @property
    def config(self):
        return LEVELS[self.level_index]

    def start(self, level_index=0, campaign=True):
        self.score=0
        self.total_apples=0
        self.campaign=campaign
        self.elapsed=0.0
        self._load_level(level_index)

    def _load_level(self,index):
        self.level_index=index
        self.obstacles=[Obstacle(x,y,kind) for x,y,kind in self.config.obstacles]
        self.obstacle_cells={ob.cell for ob in self.obstacles}
        self.snake=Snake((2,ROWS//2))
        personalities=("RANDOM PATROL","WANDER","PATROL","CHASE")
        self.enemies=[]
        for i,kind in enumerate(self.config.enemies):
            cell=(COLS-4,(2+i*4) % ROWS)
            if cell in self.obstacle_cells or cell in self.snake.body: cell=(COLS-3,2+i*4)
            self.enemies.append(Enemy(kind,cell,self.config.enemy_speed*(1+index*.09),personalities[i%len(personalities)],i))
        self.apple_count=0
        self.step_timer=0.0
        self.apple=None
        self._spawn_apple()
        self.phase="playing"
        self.particles=[]

    def _spawn_apple(self):
        blocked=set(self.obstacle_cells)|set(self.snake.body)|{enemy.cell for enemy in self.enemies}
        choices=[(x,y) for x in range(COLS) for y in range(ROWS) if (x,y) not in blocked]
        self.apple=random.choice(choices) if choices else None

    def turn(self,direction):
        if self.phase=="playing": self.snake.turn(direction)

    def update(self,dt):
        self.elapsed+=dt
        self._update_particles(dt)
        if self.phase=="transition":
            self.transition_timer-=dt
            if self.transition_timer<=0:
                if self.campaign:
                    self.level_manager.unlock_next(self.level_index)
                if self.campaign and self.level_index==len(LEVELS)-1:
                    self.phase="victory"
                    self._burst(self.snake.body[0],(255,222,115),100)
                elif self.campaign:
                    self._load_level(self.level_index+1)
                    self.phase="playing"
                else:
                    self.phase="leveldone"
            return []
        if self.phase!="playing": return []
        self.step_timer+=dt
        events=[]
        while self.step_timer>=self.config.step_time and self.phase=="playing":
            self.step_timer-=self.config.step_time
            self._move_enemies(dt)
            head=self.snake.next_head()
            grow=head==self.apple
            reason=collision_reason(head,COLS,ROWS,self.obstacle_cells,self.snake.body,
                                    {enemy.cell for enemy in self.enemies},grow)
            if reason:
                if reason=="obstacle": reason="You hit a " + self._obstacle_name(head) + "."
                elif reason=="enemy": reason="A " + self._enemy_name(head) + " caught you."
                self._die(reason)
                events.append("death")
                break
            self.snake.advance(grow)
            events.append("move")
            if grow:
                self.apple_count+=1
                self.total_apples+=1
                self.score+=100
                events.append("apple")
                self._burst(head,self.config.accent,22)
                if self.apple_count==5:
                    self.score+=250
                    self.phase="transition"
                    self.transition_timer=2.6
                    self._burst(head,(255,218,115),60)
                    events.append("level")
                else:
                    self._spawn_apple()
        return events

    def _move_enemies(self,_dt):
        occupied=set(self.obstacle_cells)
        for enemy in self.enemies:
            enemy.update(self.config.step_time,self.elapsed,COLS,ROWS,occupied,self.snake.body[0])
            occupied.add(enemy.cell)

    def _obstacle_name(self,cell):
        kind=next((o.kind for o in self.obstacles if o.cell==cell),"obstacle")
        return {"tree":"tree trunk","rock":"rock","log":"fallen log","bush":"bush","root":"tree root","thorn":"thorn bush","stone":"stone","vine":"vine","car":"car","barrier":"road barrier","hydrant":"fire hydrant","coral":"coral","plant":"sea plant","mine":"sea mine","wreck":"shipwreck","lava":"lava pool","boulder":"boulder","crack":"cracked ground"}.get(kind,"obstacle")

    def _enemy_name(self,cell):
        enemy=next((e for e in self.enemies if e.cell==cell),None)
        return enemy.kind.lower() if enemy else "creature"

    def _die(self,reason):
        self.snake.alive=False
        self.death_reason=reason
        self._burst(self.snake.body[0],(255,113,88),34)
        self.phase="gameover"

    def restart_level(self):
        # Keep campaign credit for worlds already completed; the current
        # world's apple counter starts over with the fresh level.
        level=self.level_index
        if self.campaign:
            self.score=level*750
            self.total_apples=level*5
        else:
            self.score=0
            self.total_apples=0
        self._load_level(level)

    def _burst(self,cell,color,count):
        for _ in range(count):
            self.particles.append({"x":cell[0]+.5,"y":cell[1]+.5,"vx":random.uniform(-4,4),"vy":random.uniform(-4,4),"life":random.uniform(.4,1.3),"max":1.3,"color":color})

    def _update_particles(self,dt):
        for p in self.particles:
            p["x"]+=p["vx"]*dt
            p["y"]+=p["vy"]*dt
            p["life"]-=dt
        self.particles=[p for p in self.particles if p["life"]>0]
