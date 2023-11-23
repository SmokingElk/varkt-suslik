class ControllableModel:
    def __init__(self, **controllable):
        self.controllable = controllable


def test_script(controllable_model, metrics):
    if metrics["t"] > 1.5:
        controllable_model.controllable["engines"][0].setThrustLevel(1)

class Controller:
    def __init__(self, controllable_model, scripts):
        self.scripts = scripts
        self.controllable_model = controllable_model

    def update(self, **metrics):
        for script in self.scripts:
            script(self.controllable_model, metrics)