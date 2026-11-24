"""Level order and local unlock persistence."""
import json
from pathlib import Path
from levels.forest import LEVEL as FOREST
from levels.jungle import LEVEL as JUNGLE
from levels.city import LEVEL as CITY
from levels.sea import LEVEL as SEA
from levels.volcano import LEVEL as VOLCANO

LEVELS=(FOREST,JUNGLE,CITY,SEA,VOLCANO)
PROGRESS_PATH=Path(__file__).resolve().parents[1] / "adventure_progress.json"

class LevelManager:
    def __init__(self, path=PROGRESS_PATH):
        self.path=Path(path)
        self.unlocked=0
        try:
            data=json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data,dict):
                raise ValueError("Progress data must be an object")
            self.unlocked=max(0,min(len(LEVELS)-1,int(data.get("unlocked",0))))
        except (OSError,ValueError,TypeError,AttributeError,json.JSONDecodeError):
            self.unlocked=0

    def get(self,index):
        return LEVELS[index]

    def unlock_next(self,completed_index):
        self.unlocked=max(self.unlocked,min(len(LEVELS)-1,completed_index+1))
        try:
            self.path.write_text(json.dumps({"unlocked":self.unlocked}),encoding="utf-8")
        except OSError:
            # Progress still works for this session if the folder is read-only.
            pass
