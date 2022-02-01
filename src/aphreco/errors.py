class NameDuplicationError(Exception):
    """Exception class for alert that a name has already been used in a model."""

    def __init__(self, arg=""):
        self.arg = arg

    def __str__(self):
        return f"name duplication found: {self.arg}"
