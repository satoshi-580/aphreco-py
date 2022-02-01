import aphreco as aph

"""Test for model construction"""


class TestSimulation:
    def test_add_variables_to_unit(self, capfd):
        # tested process
        x0 = aph.Variable("X0", 0.0, "y")
        v0 = aph.Variable("V0", 5000.0, "p")
        x_dose = aph.Variable("X_dose", 0.0, "p")
        ke = aph.Variable("ke", 0.01, "p")
        c0 = aph.Variable("C0", 0.0, "y", term="X0 / V0")

        model = aph.Model(name="cmpt1", items=[x0, v0])
        model.add(x_dose)
        model.add([ke, c0])

        print("\n".join(model.tree()))
        out, err = capfd.readouterr()  # get stdout and stderr

        # check answer
        expected_out = """cmpt1/
  X0[Y]
  V0[P]
  X_dose[P]
  ke[P]
  C0[Y]
"""
        expected_err = ""
        assert out == expected_out
        assert err == expected_err
