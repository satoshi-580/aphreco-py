from collections import OrderedDict
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Tuple, Union


class Optimizer:
    def __init__(self, method):
        self.method = method

    def run(self):
        pass
