import aphreco as ap
import pytest
from aphreco.errors import DuplicatedNameError, UnregisteredNameError


@pytest.mark.hybrid
class TestTypicalUserExperience:
    def test_print_tree(self, model, str_model):
        tree = "\n".join(model.tree())
        assert tree == str_model

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
        assert model["V_hb"].name == "V_hb"
        assert type(model["deriv_X_hb=-Vmax*(X_hb/V_hb)/(Km+X_hb/V_hb) ->"]) == type(
            ap.Con(term={"_": "_"})
        )

        # fail Model.__getitem__() when a model does not have the designated name.
        with pytest.raises(KeyError):
            model["Nothing"]
            model["_V_cent"]  # underscore
            model["V_cent_"]  # underscore
            model["V_cent "]  # space
            model[" V_cent"]  # space

    def test_getitem_by_path(self, model):
        # success Model.__getitem__()
        assert model["\\V_cent"].name == "V_cent"
        assert model["\\Liver\\X_hb"].name == "X_hb"
        assert isinstance(
            model["delta_C_cent+=-C_cent*V_hb/V_cent -> delta_X_hb+=C_cent*V_hb"],
            ap.Reg,
        )

        # fail Model.__getitem__() when a model does not have the designated name.
        with pytest.raises(KeyError):
            model["\\Model"]  # self
            model["\\V_cent\\"]  # with separator at the end
            model["\\ Liver \\ X_hb"]  # with spaces

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

    def test_rename_model(self, model):
        # lower
        model["Liver"].name = "Box"
        assert model["Box"].name == "Box"
        with pytest.raises(KeyError):
            model["Liver"]

        # top
        model.name = "RenamedModel"
        assert model.tree()[0] == "RenamedModel" + "\\"
        assert model.name == "RenamedModel"
        assert model.name != "Model"

    def test_delete_var(self, model):
        # deletion of a variable leads to deletion of edge/variable
        # which have involved terms.
        model.delete("X_hb")
        with pytest.raises(KeyError):
            model["X_hb"]

        # fail delete a name which does not exist in a model.
        with pytest.raises(KeyError):
            model.delete("UnnecessaryName")

        tree = "\n".join(model.tree())
        expected_tree = """Model\\
  Times\\
    [ P ] starttime
    [ P ] endless
    [ P ] onlyonce
  [ Y ] C_cent
  [ X ] V_cent
  Liver\\
    [ P ] V_hb
    [ P ] Vf_hb
    HepElim\\
      [ X ] Km
      [ X ] Vmax
    [ P ] tau_hb
    [REG] delta_C_cent+=-C_cent*V_hb/V_cent ->
  Dosing\\
    [ P ] X_dose
    [REG] -> delta_C_cent+=X_dose/V_cent"""

        assert tree == expected_tree

    def test_delete_edge(self, model):
        edge_name = "deriv_X_hb=-Vmax*(X_hb/V_hb)/(Km+X_hb/V_hb) ->"
        assert type(model[edge_name]) == type(ap.Con(term={"_": "_"}))
        model.delete(edge_name)
        with pytest.raises(KeyError):
            model[edge_name]

        tree = "\n".join(model.tree())
        expected_tree = """Model\\
  Times\\
    [ P ] starttime
    [ P ] endless
    [ P ] onlyonce
  [ Y ] C_cent
  [ X ] V_cent
  Liver\\
    [ Y ] X_hb
    [ P ] V_hb
    [ Y ] C_hb = X_hb/V_hb
    [ P ] Vf_hb
    HepElim\\
      [ X ] Km
      [ X ] Vmax
    [ P ] tau_hb
    [REG] delta_C_cent+=-C_cent*V_hb/V_cent -> delta_X_hb+=C_cent*V_hb
    [REG] delta_X_hb+=-X_hb -> delta_C_cent+=X_hb/V_cent
  Dosing\\
    [ P ] X_dose
    [REG] -> delta_C_cent+=X_dose/V_cent"""

        assert tree == expected_tree

    def test_delete_model(self, model, str_model):
        # add a model with inside items
        model.add(ap.Model("Add"))
        model["Add"].add(ap.Y("y_in_box"))
        model["Add"].add(ap.P("p_in_box"))
        model["Add"].add(ap.X("x_in_box"))
        tree = "\n".join(model.tree())
        assert tree != str_model

        # deletion of a model leads to deletion of inside items.
        model.delete("Add")
        tree = "\n".join(model.tree())
        assert tree == str_model

    def test_copy_model(self, model, str_dose_escalation_model):
        model_10mg = model.copy(suffix="_10mg", exclusive=["X_dose"])
        model_50mg = model.copy(suffix="_50mg", exclusive=["X_dose"])
        model_200mg = model.copy(suffix="_200mg", exclusive=["X_dose"])

        escalate = ap.Model("DoseEscalation")
        escalate.add([model_10mg, model_50mg, model_200mg], duplicate="skip")

        tree = "\n".join(escalate.tree())
        assert tree == str_dose_escalation_model
