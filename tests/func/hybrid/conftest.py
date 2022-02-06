import aphreco as ap
import pytest


@pytest.fixture()
def model():
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
def str_model():
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
