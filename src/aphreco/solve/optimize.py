from click import option


class OptOptions:
    def __init__(self):
        pass


class Optimizer:
    def __init__(self, options: OptOptions = OptOptions()):
        self.options = options
