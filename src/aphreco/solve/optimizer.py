from typing import List, Union

from .optimize.base import BaseOptimizeMethod


class Optimizer:
    def __init__(
        self,
        methods: Union[None, BaseOptimizeMethod, List[BaseOptimizeMethod]] = None,
    ):
        if methods is None:
            self.methods = methods
        elif isinstance(methods, list):
            self.methods = methods
        elif isinstance(methods, BaseOptimizeMethod):
            self.methods = [methods]
        else:
            raise TypeError("invalid methods type")

    def collect_method_and_options(self):
        for method in self.methods:
            print(method.write_options)
