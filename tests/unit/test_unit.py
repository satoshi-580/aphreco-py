import aphreco as ap


class TestUnit:
    def test_add_variables_to_unit(self, capfd):
        # tested process
        unit = ap.Unit()
        unit.add(
            [
                ap.Var("X1"),
                ap.Var("X2"),
            ]
        )

        # print model structure as a tree in stdout
        unit.tree()
        out, err = capfd.readouterr()  # get stdout and stderr

        # check answer
        expected_out = "[BOX]/\n  X1[Y]\n  X2[Y]\n"
        expected_err = ""
        assert out == expected_out
        assert err == expected_err
