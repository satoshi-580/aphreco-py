from typing import Optional

from .fmin.base import BaseFminAlgorithm
from .fmin.serial import NelderMead


class Optimizer:
    def __init__(
        self,
        fmin: Optional[BaseFminAlgorithm] = NelderMead(),
        **options,
    ):
        if not isinstance(fmin, BaseFminAlgorithm):
            raise TypeError("invalid  type")

        self.fmin = fmin
        if options:
            self.fmin.set_options(**options)
