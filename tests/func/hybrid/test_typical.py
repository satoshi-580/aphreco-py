import aphreco as ap
import pytest
from aphreco.errors import DuplicatedNameError, UnregisteredNameError


class TestTypicalUserExperience:
    def test_print_tree(self, model, str_model):
        assert str(model) == str_model

    def test_name_check(self, model):
        with pytest.raises(DuplicatedNameError):
            model.add(ap.P("C_cent"))
        with pytest.raises(DuplicatedNameError):
            model.add(ap.Y("V_hb"))

        with pytest.raises(UnregisteredNameError):
            model.rename({"NotExistingName": "MeaninglessName"})

    def test_getitem_by_name(self, model):
        # success Model.__getitem__()
        assert model["V_cent"].name == "V_cent"
        assert model["V_hb"].value == 0.0
        assert type(model["X_hb:-Vmax*(X_hb/V_hb)/(Km+X_hb/V_hb) ->"]) == type(
            ap.Con(term={"_": "_"})
        )

        # fail Model.__getitem__() when a model does not have the designated name.
        with pytest.raises(KeyError):
            model["Nothing"]
            model["_V_cent"]  # underscore
            model["V_cent_"]  # underscore
            model["V_cent "]  # space
            model[" V_cent"]  # space

    @pytest.mark.skip(reason="unstable")
    def test_getitem_by_path(self, model):
        # success Model.__getitem__()
        # assert model["/model/X1"].name == "X1"
        # assert model["X1"].value == 100.0
        # assert type(model["X1:-k12*X1 -> X2:k12*X1"]) == type(
        #     ap.Con(term={"dummy": "nothing"})
        # )
        pass
        # # fail Model.__getitem__() when a model does not have the designated name.
        # with pytest.raises(KeyError):
        #     model["Nothing"]
        #     model["_k12"]  # underscore
        #     model["k12_"]  # underscore
        #     model["X1 "]  # space
        #     model[" X1"]  # space

    def test_rename_var(self, model):
        # rename variable y
        repmap_y = {"C_cent": "C0", "C_hb": "Ch"}  # repmap = replacement map
        model.rename(repmap_y)
        assert model["C0"].name == repmap_y["C_cent"]
        assert model["Ch"].name == repmap_y["C_hb"]
        with pytest.raises(KeyError):
            model["C_cent"]
            model["C_hb"]

        # rename variable pd
        repmap_p = {"Km": "Km_tp", "V_cent": "V0"}  # repmap: replacement map
        model.rename(repmap_p)
        assert model["Km_tp"].name == repmap_p["Km"]
        assert model["V0"].name == repmap_p["V_cent"]
        with pytest.raises(KeyError):
            model["Km"]
            model["V_cent"]

    @pytest.mark.skip(reason="not implemnted yet")
    def test_rename_edge(self, model):
        pass

    @pytest.mark.skip(reason="unstable")
    def test_rename_model(self, model):
        # lower
        repmap_m = {"liver": "container"}
        model["liver"].name = repmap_m["liver"]
        assert model["container"].name == repmap_m["liver"]
        with pytest.raises(KeyError):
            model["liver"]

        # top
        repmap_m = {"model": "renamed_model"}
        model.name = repmap_m["model"]
        assert model.tree()[0] == repmap_m["model"] + "\\"
        assert model.name == "renamed_model"
        assert model.name != "model"

    def test_delete_var(self, model):
        # deletion of a variable leads to deletion of edge/variable
        # which have involved terms.
        model.delete("X_hb")
        with pytest.raises(KeyError):
            model["X_hb"]

        # fail delete a name which does not exist in a model.
        with pytest.raises(KeyError):
            model.delete("UnnecessaryName")

        expected_tree = """model\\
  [ Y ] C_cent
  [ X ] V_cent
  liver\\
    [ P ] V_hb
    [ P ] Vf_hb
    [ X ] Km
    [ X ] Vmax
    [ P ] ini_t
    [ P ] end_t
    [ P ] tau_hb
    [REG] C_cent:-C_cent*V_hb/V_cent ->
  [ P ] X_dose
  [REG] -> C_cent:X_dose/V_cent"""

        assert str(model) == expected_tree

    def test_delete_edge(self, model):
        assert type(model["X_hb:-Vmax*(X_hb/V_hb)/(Km+X_hb/V_hb) ->"]) == type(
            ap.Con(term={"_": "_"})
        )
        model.delete("X_hb:-Vmax*(X_hb/V_hb)/(Km+X_hb/V_hb) ->")
        with pytest.raises(KeyError):
            model["X_hb:-Vmax*(X_hb/V_hb)/(Km+X_hb/V_hb) ->"]

        expected_tree = """model\\
  [ Y ] C_cent
  [ X ] V_cent
  liver\\
    [ Y ] X_hb
    [ P ] V_hb
    [ Y ] C_hb = X_hb/V_hb
    [ P ] Vf_hb
    [ X ] Km
    [ X ] Vmax
    [ P ] ini_t
    [ P ] end_t
    [ P ] tau_hb
    [REG] C_cent:-C_cent*V_hb/V_cent -> X_hb:C_cent*V_hb
    [REG] X_hb:-X_hb -> C_cent:X_hb/V_cent
  [ P ] X_dose
  [REG] -> C_cent:X_dose/V_cent"""

        assert str(model) == expected_tree

    def test_delete_model(self, model, str_model):
        # add a model with inside items
        model.add(ap.Model("box"))
        model["box"].add(ap.Y("y_in_box"))
        model["box"].add(ap.P("p_in_box"))
        model["box"].add(ap.X("x_in_box"))
        assert str(model) != str_model

        # deletion of a model leads to deletion of inside items.
        model.delete("box")
        assert str(model) == str_model

    @pytest.mark.skip(reason="not implemented yet")
    def test_simulation(self, model):
        out_time = [float(i) / 100 for i in range(1000)]
        simulator = ap.Simulator()
        simres = simulator.run(model, out_time)

        assert simres.out_t == out_time
        # assert simres.out_y == data of model simulation loaded by fixture
