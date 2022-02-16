import abc


class BaseModule(abc.ABC):
    # Module class returns a pre-assembled Model object.
    def __new__(cls, **args):
        raise NotImplementedError


class BaseAdaptor(abc.ABC):
    # connects models via terms.
    def __new__(cls, terms, **model):
        raise NotImplementedError


class Inlet:
    pass


class Outlet:
    pass
