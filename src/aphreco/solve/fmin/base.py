import abc
from typing import List, Union


def set_option(options, key, value):
    if key in options.keys():
        check_option_type(options[key], value)
        options[key] = value
    else:
        raise KeyError(f"invalid option key: {key}")
    return options


def check_option_type(old_value, new_value):
    if type(old_value) != type(new_value):
        raise TypeError(
            f"invalid option value: {new_value}\nexpected {type(old_value)}"
        )


class BaseOptimizeMethod(abc.ABC):
    @property
    def name(self):
        return self._name

    @property
    def is_default(self):
        return self._is_default

    @is_default.setter
    def is_default(self, value):
        self._is_default = value

    def set_options(self, **options):
        if options:
            self.is_default = False
            for key, value in options.items():
                self.options = set_option(self.options, key, value)

    def collect_options(self):
        return str(self.options)


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
