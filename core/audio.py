"""Tiny synthesized arcade sounds; no bundled audio assets are required."""
import math
from array import array

class Audio:
    def __init__(self):
        self.enabled=True
        self.ready=False
        self.music=None
        try:
            import pygame
            pygame.mixer.init(frequency=22050,size=-16,channels=1,buffer=512)
            self.pygame=pygame
            self.ready=True
            self.effects={name:self._tone(freq,.035 if name=="move" else (.12 if name=="apple" else .32)) for name,freq in
                          (("move",235),("apple",740),("level",520),("death",145),("victory",880))}
            self.effects["move"].set_volume(.12)
            self.melodies={}
        except Exception:
            self.ready=False

    def _tone(self,frequency,duration):
        rate=22050
        samples=array("h")
        count=int(rate*duration)
        for i in range(count):
            envelope=min(1,i/(rate*.015),max(0,(count-i)/(rate*.05)))
            samples.append(int(9000*envelope*math.sin(2*math.pi*frequency*i/rate)))
        return self.pygame.mixer.Sound(buffer=samples.tobytes())

    def effect(self,name):
        if self.ready and self.enabled:
            try: self.effects[name].play()
            except (KeyError,RuntimeError): pass

    def set_music(self,config):
        if not self.ready: return
        try:
            key=(config.name,config.music_notes)
            if key not in self.melodies:
                rate=22050; samples=array("h")
                for frequency in config.music_notes:
                    length=int(rate*.20)
                    for i in range(length):
                        fade=min(1,i/(rate*.025),max(0,(length-i)/(rate*.04)))
                        samples.append(int(950*fade*math.sin(2*math.pi*frequency*i/rate)))
                self.melodies[key]=self.pygame.mixer.Sound(buffer=samples.tobytes())
            if self.music is not self.melodies[key]:
                if self.music: self.music.stop()
                self.music=self.melodies[key]
                if self.enabled: self.music.play(-1)
        except Exception:
            pass

    def toggle(self):
        self.enabled=not self.enabled
        if self.ready:
            if self.enabled and self.music: self.music.play(-1)
            elif self.music: self.music.stop()

    def stop_music(self):
        if self.music:
            self.music.stop()
            self.music=None
