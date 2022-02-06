import aphreco as ap
import pytest
from aphreco.errors import DuplicatedNameError, UnregisteredNameError


class TestTypicalUserExperience:
    @pytest.fixture()
    def model(self):
        model = ap.Model("model")
        model.add([ap.Y("C_cent"), ap.P("V_cent")])

        liver = ap.Model("liver")
        liver.add(
            [
                ap.Y("X_hb"),
                ap.P("V_hb"),
                ap.Y("C_hb", term="X_hb/V_hb"),
                ap.P("Vf_hb"),
            ]
        )
        liver.add(
            [
                ap.P("Km"),
                ap.P("Vmax"),
                ap.Con({"X_hb": "-Vmax*(X_hb/V_hb)/(Km+X_hb/V_hb)"}),
            ]
        )
        model.add(liver)

        model["liver"].add([ap.P("ini_t"), ap.P("end_t"), ap.P("tau_hb")])
        model["liver"].add(
            [
                ap.Reg(
                    beat=("ini_t", "end_t", "tau_hb"),
                    term={
                        "C_cent": "-C_cent*V_hb/V_cent",
                        "X_hb": "C_cent*V_hb",
                    },
                ),
                ap.Reg(
                    beat=("ini_t", "end_t", "tau_hb"),
                    term={
                        "X_hb": "-X_hb",
                        "C_cent": "X_hb/V_cent",
                    },
                ),
            ]
        )

        model.add(ap.P("X_dose"))
        model.add(
            ap.Reg(
                beat=("ini_t", "end_t", "end_t"),
                term={
                    "C_cent": "X_dose/V_cent",
                },
            )
        )

        model["Km"].type = ap.ItemType.X
        model["Vmax"].type = ap.ItemType.X
        model["V_cent"].type = ap.ItemType.X

        model["X_dose"].value = 1000.0
        return model

    @pytest.fixture()
    def str_model(self):
        return """model\\
  [ Y ] C_cent
  [ X ] V_cent
  liver\\
    [ Y ] X_hb
    [ P ] V_hb
    [ Y ] C_hb = X_hb/V_hb
    [ P ] Vf_hb
    [ X ] Km
    [ X ] Vmax
    [CON] X_hb:-Vmax*(X_hb/V_hb)/(Km+X_hb/V_hb) ->
    [ P ] ini_t
    [ P ] end_t
    [ P ] tau_hb
    [REG] C_cent:-C_cent*V_hb/V_cent -> X_hb:C_cent*V_hb
    [REG] X_hb:-X_hb -> C_cent:X_hb/V_cent
  [ P ] X_dose
  [REG] -> C_cent:X_dose/V_cent"""

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
        print(model["X_hb:-Vmax*(X_hb/V_hb)/(Km+X_hb/V_hb) ->"])
        assert type(model["X_hb:-Vmax*(X_hb/V_hb)/(Km+X_hb/V_hb) ->"]) == type(
            ap.Con(term={"_": "_"})
        )

        # fail Model.__getitem__() when a model does not have the designated name.
        with pytest.raises(KeyError):
            model["Nothing"]
            model["_k12"]  # underscore
            model["k12_"]  # underscore
            model["X1 "]  # space
            model[" X1"]  # space

    # @pytest.mark.skip(reason="unstable")
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
        repmap_y = {"X1": "A", "X2": "B"}  # repmap = replacement map
        model.rename(repmap_y)
        assert model["A"].name == repmap_y["X1"]
        assert model["B"].name == repmap_y["X2"]
        with pytest.raises(KeyError):
            model["X1"]
            model["X2"]

        # rename variable pd
        repmap_p = {"k12": "k_a2b", "k21": "k_b2a"}  # repmap: replacement map
        model.rename(repmap_p)
        assert model["k_a2b"].name == repmap_p["k12"]
        assert model["k_b2a"].name == repmap_p["k21"]
        with pytest.raises(KeyError):
            model["k12"]
            model["k21"]

    @pytest.mark.skip(reason="not implemnted yet")
    def test_rename_edge(self, model):
        pass

    def test_rename_model(self, model, str_model):
        # add a model with inside items
        model.add(ap.Model("box"))
        model["box"].add(ap.Y("y_in_box"))
        model["box"].add(ap.P("p_in_box"))
        model["box"].add(ap.X("x_in_box"))
        assert str(model) != str_model

        # lower
        repmap_m = {"box": "container"}
        model["box"].name = repmap_m["box"]
        with pytest.raises(KeyError):
            model["box"]

        # top
        repmap_m = {"model": "renamed_model"}
        model.name = repmap_m["model"]
        assert model.tree()[0] == repmap_m["model"] + "/"
        assert model.name == "renamed_model"
        assert model.name != "model"

    def test_delete_var(self, model):
        # deletion of a variable leads to deletion of edge/variable
        # which have involved terms.
        model.delete("X2")

        # if success, a deleted name must not exist.
        with pytest.raises(KeyError):
            model["X2"]

        # fail when a name does not exist in a model.
        with pytest.raises(KeyError):
            model.delete("UnnecessaryName")

        expected_tree = """model/
  [ Y ] X1
  [ P ] k12
  [ P ] k21
  [CON] X1:-k12*X1 ->
  [ P ] ke
  [CON] X1:-ke*X1 ->"""
        assert str(model) == expected_tree

    def test_delete_edge(self, model):
        model.delete("X1:-k12*X1 -> X2:k12*X1")

        # if success, a deleted name must not exist.
        with pytest.raises(KeyError):
            model["X1:-k12*X1 -> X2:k12*X1"]

        expected_tree = """model/
  [ Y ] X1
  [ Y ] X2
  [ P ] k12
  [ P ] k21
  [CON] X2:-k21*X2 -> X1:k21*X2
  [ P ] ke
  [CON] X1:-ke*X1 ->"""
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
