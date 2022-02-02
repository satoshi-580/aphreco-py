import aphreco as aph


class TestTypicalUserExperience:
    def test_add_items_to_model(self, capfd):
        # tested process
        x0 = aph.Variable("X0", 0.0, "y")
        v0 = aph.Variable("V0", 5000.0, "p")
        x_dose = aph.Variable("X_dose", 0.0, "p")
        ke = aph.Variable("ke", 0.01, "p")
        c0 = aph.Variable("C0", 0.0, "y", term="X0 / V0")
        elim = aph.Con({"X0": "-ke * X0"})

        model = aph.Model(name="cmpt1", items=[x0, v0, elim])
        model.add(x_dose)
        model.add([ke, c0])
        print(model)
        out, err = capfd.readouterr()  # get stdout and stderr

        # check answer
        expected_out = """cmpt1/
  X0[Y]
  V0[P]
  con_edge_1[CON]{'X0'}
  X_dose[P]
  ke[P]
  C0[Y]
"""
        expected_err = ""
        assert out == expected_out
        assert err == expected_err

    def test_copy_model(self):

        x0 = aph.Variable("X0", 0.0, "y")
        v0 = aph.Variable("V0", 5000.0, "p")
        x_dose = aph.Variable("X_dose", 0.0, "p")
        ke = aph.Variable("ke", 0.01, "p")
        c0 = aph.Variable("C0", 0.0, "y", term="X0 / V0")
        elim = aph.Con({"X0": "-ke * X0"})

        model = aph.Model(name="cmpt1", items=[x0, v0, elim])
        model.add(x_dose)
        model.add([ke, c0])

        model_10mg = model.copy(suffix="_10mg", exclusive=["X_dose"])
        assert "X_dose" not in model_10mg.children.keys()
        assert "X_dose_10mg" in model_10mg.children.keys()
        assert "X0" not in model_10mg.children.keys()
        assert "X0_10mg" in model_10mg.children.keys()
        assert "V0" in model_10mg.children.keys()
        assert "V0_10mg" not in model_10mg.children.keys()
        model_10mg["X_dose_10mg"].value = 10.0
        assert model_10mg["X_dose_10mg"].value == 10.0

        model_50mg = model.copy(suffix="_50mg", exclusive=["X_dose"])
        assert "X_dose" not in model_50mg.children.keys()
        assert "X_dose_50mg" in model_50mg.children.keys()
        assert "X0" not in model_50mg.children.keys()
        assert "X0_50mg" in model_50mg.children.keys()
        assert "V0" in model_50mg.children.keys()
        assert "V0_50mg" not in model_50mg.children.keys()
        model_50mg["X_dose_50mg"].value = 50.0
        assert model_50mg["X_dose_50mg"].value == 50.0

    def test_integrate_models(self):
        # phase1 = aph.Model("phase1")
        # phase1.add([model_10mg, model_50mg], duplicate="skip")
        # print(phase1)
        assert True
