import abc
from typing import Dict, Tuple

from aphreco.enums import ItemType


class BaseSolver(abc.ABC):
    @property
    def formatter(self):
        return self._formatter

    @formatter.setter
    def formatter(self, formatter):
        self._formatter = formatter

    @property
    def replacer(self):
        return self._replacer

    @replacer.setter
    def replacer(self, replacer):
        self._replacer = replacer

    @property
    def writer(self):
        return self._writer

    @writer.setter
    def writer(self, writer):
        self._writer = writer

    @property
    def exporter(self):
        return self._exporter

    @exporter.setter
    def exporter(self, exporter):
        self._exporter = exporter

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, command):
        self._command = command

    @property
    def reader(self):
        return self._reader

    @reader.setter
    def reader(self, reader):
        self._reader = reader

    def _execute(self, release):
        if release:
            self.command.release()
        else:
            self.command.compile()
