import aphreco as ap
import pytest


@pytest.fixture()
def model():
    model = ap.Model("Model")
    times = ap.Model("Times")
    times.add([ap.P("timezero", 0.0), ap.P("endless", 1e12), ap.P("onlyonce", 1e12)])
    model.add(times)
    model.add([ap.Y("C_cent"), ap.X("V_cent", 4000.0)])

    liver = ap.Model("Liver")
    liver.add(
        [
            ap.Y("X_hb"),
            ap.P("V_hb", 120),
            ap.Y("C_hb", term="X_hb/V_hb"),
            ap.P("Vf_hb", 120),
        ]
    )
    liver.add(ap.Model("HepElim"))
    liver["HepElim"].add(
        [
            ap.X("Km", 0.1),
            ap.X("Vmax", 2500.0),
            ap.Con({"X_hb": "-Vmax*(X_hb/V_hb)/(Km+X_hb/V_hb)"}),
        ]
    )

    model.add(liver)

    model["Liver"].add(ap.P("tau_hb", 0.025))
    model["Liver"].add(
        [
            ap.Reg(
                beat=("timezero", "endless", "tau_hb"),
                term={
                    "C_cent": "-C_cent*V_hb/V_cent",
                    "X_hb": "C_cent*V_hb",
                },
            ),
            ap.Reg(
                beat=("timezero", "endless", "tau_hb"),
                term={
                    "X_hb": "-X_hb",
                    "C_cent": "X_hb/V_cent",
                },
            ),
        ]
    )

    dosing = ap.Model("Dosing")
    model.add(dosing)
    model["Dosing"].add(ap.P("X_dose", 10000.0))
    model["Dosing"].add(
        ap.Reg(
            beat=("timezero", "endless", "onlyonce"),
            term={
                "C_cent": "X_dose/V_cent",
            },
        )
    )

    return model


@pytest.fixture()
def str_model():
    return """Model\\
  Times\\
    [ P ] timezero
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
      [CON] deriv_X_hb=-Vmax*(X_hb/V_hb)/(Km+X_hb/V_hb) ->
    [ P ] tau_hb
    [REG] delta_C_cent+=-C_cent*V_hb/V_cent -> delta_X_hb+=C_cent*V_hb
    [REG] delta_X_hb+=-X_hb -> delta_C_cent+=X_hb/V_cent
  Dosing\\
    [ P ] X_dose
    [REG] -> delta_C_cent+=X_dose/V_cent"""


@pytest.fixture()
def str_dose_escalation_model():
    return """DoseEscalation\\
  Model_10mg\\
    Times\\
      [ P ] timezero
      [ P ] endless
      [ P ] onlyonce
    [ Y ] C_cent_10mg
    [ X ] V_cent
    Liver\\
      [ Y ] X_hb_10mg
      [ P ] V_hb
      [ Y ] C_hb_10mg = X_hb_10mg/V_hb
      [ P ] Vf_hb
      HepElim\\
        [ X ] Km
        [ X ] Vmax
        [CON] deriv_X_hb_10mg=-Vmax*(X_hb_10mg/V_hb)/(Km+X_hb_10mg/V_hb) ->
      [ P ] tau_hb
      [REG] delta_C_cent_10mg+=-C_cent_10mg*V_hb/V_cent -> delta_X_hb_10mg+=C_cent_10mg*V_hb
      [REG] delta_X_hb_10mg+=-X_hb_10mg -> delta_C_cent_10mg+=X_hb_10mg/V_cent
    Dosing\\
      [ P ] X_dose_10mg
      [REG] -> delta_C_cent_10mg+=X_dose_10mg/V_cent
  Model_50mg\\
    Times\\
    [ Y ] C_cent_50mg
    Liver\\
      [ Y ] X_hb_50mg
      [ Y ] C_hb_50mg = X_hb_50mg/V_hb
      HepElim\\
        [CON] deriv_X_hb_50mg=-Vmax*(X_hb_50mg/V_hb)/(Km+X_hb_50mg/V_hb) ->
      [REG] delta_C_cent_50mg+=-C_cent_50mg*V_hb/V_cent -> delta_X_hb_50mg+=C_cent_50mg*V_hb
      [REG] delta_X_hb_50mg+=-X_hb_50mg -> delta_C_cent_50mg+=X_hb_50mg/V_cent
    Dosing\\
      [ P ] X_dose_50mg
      [REG] -> delta_C_cent_50mg+=X_dose_50mg/V_cent
  Model_200mg\\
    Times\\
    [ Y ] C_cent_200mg
    Liver\\
      [ Y ] X_hb_200mg
      [ Y ] C_hb_200mg = X_hb_200mg/V_hb
      HepElim\\
        [CON] deriv_X_hb_200mg=-Vmax*(X_hb_200mg/V_hb)/(Km+X_hb_200mg/V_hb) ->
      [REG] delta_C_cent_200mg+=-C_cent_200mg*V_hb/V_cent -> delta_X_hb_200mg+=C_cent_200mg*V_hb
      [REG] delta_X_hb_200mg+=-X_hb_200mg -> delta_C_cent_200mg+=X_hb_200mg/V_cent
    Dosing\\
      [ P ] X_dose_200mg
      [REG] -> delta_C_cent_200mg+=X_dose_200mg/V_cent"""
