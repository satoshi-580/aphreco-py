import abc

from aphreco.solve.utils import set_option


class BaseStepMethod(abc.ABC):
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
