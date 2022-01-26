from collections import OrderedDict

SOURCE_LINES = OrderedDict(
    t="",
    y="",
    p="",
    ode="",
    rec="",
    cond="",
    beat="",
    cre="",
    x_index="",
    x_bounds="",
    stepper="",
    stepper_options="",
    optimizer=list(),
    optimizer_options=list(),
    obs="",
)


class Source:
    def __init__(self):
        self.lines = SOURCE_LINES.copy()


class ReplacedSource(Source):
    def __init__(self):
        super().__init__()
