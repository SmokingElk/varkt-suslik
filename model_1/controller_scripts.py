from controller import ScriptBase

class MainScript(ScriptBase):
    def __init__(self):
        self.stage = 0

    def update(self, model, metrics):
        mainEngine = model["main_engine"]
        thrusterLeft = model["thruster_left"]
        thrusterRight = model["thruster_right"]