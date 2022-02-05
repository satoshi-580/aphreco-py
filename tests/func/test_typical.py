import aphreco as ap
import pytest
from aphreco.errors import DuplicatedNameError, UnregisteredNameError


class TestSimpleUserExperience:
    @pytest.fixture()
    def cmpt2(self):
        # model
        cmpt2 = ap.Model("cmpt2")

        # dep/indep parameters
        cmpt2.add(
            [
                ap.Y("X1", value=100.0),
                ap.Y("X2"),
                ap.P("k12"),
                ap.P("k21"),
            ]
        )

        # distribution
        cmpt2.add(ap.Con({"X1": "-k12*X1", "X2": "k12*X1"}))
        cmpt2.add(ap.Con({"X2": "-k21*X2", "X1": "k21*X2"}))

        # elimination
        cmpt2.add([ap.P("ke"), ap.Con({"X1": "-ke*X1"})])
        return cmpt2

    @pytest.fixture()
    def str_cmpt2(self):
        return """cmpt2/
  [ Y ] X1
  [ Y ] X2
  [ P ] k12
  [ P ] k21
  [CON] X1:-k12*X1 -> X2:k12*X1
  [CON] X2:-k21*X2 -> X1:k21*X2
  [ P ] ke
  [CON] X1:-ke*X1 ->"""

    def test_print_tree(self, cmpt2, str_cmpt2):
        assert str(cmpt2) == str_cmpt2

    def test_name_check(self, cmpt2):
        with pytest.raises(DuplicatedNameError):
            cmpt2.add(ap.P("X1"))
        with pytest.raises(DuplicatedNameError):
            cmpt2.add(ap.Y("k21"))

        with pytest.raises(UnregisteredNameError):
            cmpt2.rename({"NotExistingName": "MeaninglessName"})

    def test_getitem(self, cmpt2):
        # success Model.__getitem__()
        assert cmpt2["X1"].name == "X1"
        assert cmpt2["X1"].value == 100.0
        assert type(cmpt2["X1:-k12*X1 -> X2:k12*X1"]) == type(
            ap.Con(term={"dummy": "nothing"})
        )

        # fail Model.__getitem__() when a model does not have the designated name.
        with pytest.raises(KeyError):
            cmpt2["Nothing"]
            cmpt2["_k12"]  # underscore
            cmpt2["k12_"]  # underscore
            cmpt2["X1 "]  # space
            cmpt2[" X1"]  # space

    def test_rename(self, cmpt2):
        repmap_var = {"X1": "A", "X2": "B"}
        cmpt2.rename(repmap_var)
        repmap_edge = {"k12": "k_a2b", "k21": "k_b2a"}
        cmpt2.rename(repmap_edge)
        assert cmpt2["A"].name == repmap_var["X1"]
        assert cmpt2["B"].name == repmap_var["X2"]

        # renamed name does not exist.
        with pytest.raises(KeyError):
            cmpt2["X1"]
            cmpt2["k12"]

    def test_delete_var(self, cmpt2):
        # deletion of a variable leads to deletion of edge/variable
        # which have involved terms.
        cmpt2.delete("X2")

        # if success, a deleted name must not exist.
        with pytest.raises(KeyError):
            cmpt2["X2"]

        # fail when a name does not exist in a model.
        with pytest.raises(KeyError):
            cmpt2.delete("UnnecessaryName")

        expected_tree = """cmpt2/
  [ Y ] X1
  [ P ] k12
  [ P ] k21
  [CON] X1:-k12*X1 ->
  [ P ] ke
  [CON] X1:-ke*X1 ->"""
        assert str(cmpt2) == expected_tree

    def test_delete_edge(self, cmpt2):
        cmpt2.delete("X1:-k12*X1 -> X2:k12*X1")

        # if success, a deleted name must not exist.
        with pytest.raises(KeyError):
            cmpt2["X1:-k12*X1 -> X2:k12*X1"]

        expected_tree = """cmpt2/
  [ Y ] X1
  [ Y ] X2
  [ P ] k12
  [ P ] k21
  [CON] X2:-k21*X2 -> X1:k21*X2
  [ P ] ke
  [CON] X1:-ke*X1 ->"""
        assert str(cmpt2) == expected_tree

    def test_delete_model(self, cmpt2, str_cmpt2):
        # add model with inside items
        cmpt2.add(ap.Model("box"))
        cmpt2["box"].add(ap.Y("y_in_box"))
        cmpt2["box"].add(ap.P("p_in_box"))
        cmpt2["box"].add(ap.X("x_in_box"))
        assert str(cmpt2) != str_cmpt2

        # deletion of a model leads to deletion of inside items.
        cmpt2.delete("box")
        assert str(cmpt2) == str_cmpt2

    @pytest.mark.skip(reason="not implemented yet")
    def test_simulation(self, cmpt2):
        out_time = [float(i) / 100 for i in range(1000)]
        simulator = ap.Simulator()
        simres = simulator.run(cmpt2, out_time)

        assert simres.out_t == out_time
        # assert simres.out_y == data of cmpt2 simulation loaded by fixture
