import aphreco as ap
import pytest


@pytest.fixture()
def cmpt1():
    cmpt1 = ap.Model("Cmpt1")
    cmpt1.add([ap.Y("X", 100.0), ap.P("ke", 0.1)])
    cmpt1.add(ap.Con({"X": "-ke*X"}))
    return cmpt1


@pytest.fixture()
def str_cmpt1():
    return """Cmpt1\\
  [ Y ] X
  [ P ] ke
  [CON] deriv_X=-ke*X ->"""


@pytest.fixture()
def cmpt2():
    # model
    cmpt2 = ap.Model("Cmpt2")

    # dep/indep parameters
    cmpt2.add(
        [
            ap.Y("X1", 100.0),
            ap.Y("X2"),
            ap.P("k12", 0.2),
            ap.P("k21", 0.05),
        ]
    )

    # distribution
    cmpt2.add(ap.Con({"X1": "-k12*X1", "X2": "k12*X1"}))
    cmpt2.add(ap.Con({"X2": "-k21*X2", "X1": "k21*X2"}))

    # elimination
    cmpt2.add([ap.P("ke"), ap.Con({"X1": "-ke*X1"})])
    return cmpt2


@pytest.fixture()
def str_cmpt2():
    return """Cmpt2\\
  [ Y ] X1
  [ Y ] X2
  [ P ] k12
  [ P ] k21
  [CON] deriv_X1=-k12*X1 -> deriv_X2=k12*X1
  [CON] deriv_X2=-k21*X2 -> deriv_X1=k21*X2
  [ P ] ke
  [CON] deriv_X1=-ke*X1 ->"""
