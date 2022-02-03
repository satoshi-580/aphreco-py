class DuplicatedNameError(Exception):
    """Exception class for alert that a name has already been used in a model."""

    def __init__(self, arg=""):
        self.arg = arg

    def __str__(self):
        return f"name duplication found: {self.arg}"


class UnregisteredNameError(Exception):
    """Exception class for alert that a name used in a new edge/var term is not in a current model."""

    def __init__(self, arg=set()):
        self.arg = arg

    def __str__(self):
        return f"unregistered name found: {self.arg}"
