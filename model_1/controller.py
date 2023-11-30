def test_script(controllable_model, metrics):
    if metrics["t"] > 1.5:
        controllable_model.controllable["engines"][0].setThrustLevel(1)


class ScriptBase:
    def update(self, model, metrics):
        pass

    def __call__(self, model, metrics, log):
        self.update(model, metrics, log)


class Controller:
    def __init__(self, controllable_model, scripts, needLog):
        self.scripts = scripts
        self.controllable_model = controllable_model

        self.logFunc = lambda *x: print(*x)
        if not needLog:
            self.logFunc = lambda x: x

    def update(self, **metrics):
        for script in self.scripts:
            script(self.controllable_model, metrics, self.logFunc)