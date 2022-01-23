import abc


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
