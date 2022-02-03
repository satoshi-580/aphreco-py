import aphreco as ap
import pytest


class TestTypicalUserExperience:
    @pytest.fixture()
    def setup_model(self):
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

    def test_add_items_to_model(self, setup_model):
        print(setup_model)

        # check answer
        expected_out = """model/
  [ Y ] C_cent
  [ X ] V_cent
  liver/
    [ Y ] X_hb
    [ P ] V_hb
    [ Y ] C_hb
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
  [REG]  -> C_cent:X_dose/V_cent"""
        assert str(setup_model) == expected_out

    def test_copy_model(self, setup_model):

        model_10mg = setup_model.copy(suffix="_10mg", exclusive=["X_dose"])
        assert "X_dose" not in model_10mg.children.keys()
        assert "X_dose_10mg" in model_10mg.children.keys()
        assert "C_cent" not in model_10mg.children.keys()
        assert "C_cent_10mg" in model_10mg.children.keys()
        assert "V_cent" in model_10mg.children.keys()
        assert "V_cent_10mg" not in model_10mg.children.keys()
        model_10mg["X_dose_10mg"].value = 10.0
        assert model_10mg["X_dose_10mg"].value == 10.0

        # assert "X0_10mg" in model["con_edge_2"].term.keys()

        model_50mg = setup_model.copy(suffix="_50mg", exclusive=["X_dose"])
        assert "X_dose" not in model_50mg.children.keys()
        assert "X_dose_50mg" in model_50mg.children.keys()
        assert "C_cent" not in model_50mg.children.keys()
        assert "C_cent_50mg" in model_50mg.children.keys()
        assert "V_cent" in model_50mg.children.keys()
        assert "V_cent_50mg" not in model_50mg.children.keys()
        model_50mg["X_dose_50mg"].value = 50.0
        assert model_50mg["X_dose_50mg"].value == 50.0

    def test_integrate_models(self):
        # phase1 = ap.Model("phase1")
        # phase1.add([model_10mg, model_50mg], duplicate="skip")
        # print(phase1)
        assert True
