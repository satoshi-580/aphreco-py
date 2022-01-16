import aphreco as ap


class TestUnit:
    def test_add_variables_to_unit(self, capfd):
        # tested process
        unit = ap.Unit("me")
        unit.add(
            [
                ap.Variable("c0"),
                ap.Variable("c1"),
            ]
        )

        # print model structure as a tree in stdout
        unit.tree()
        out, err = capfd.readouterr()  # get stdout and stderr

        # check answer
        expected_out = "me:\n  y[c0]\n  y[c1]\n"
        expected_err = ""
        assert out == expected_out
        assert err == expected_err

    def test_add_models_to_unit(self, capfd):
        # tested process
        unit = ap.Unit("me")
        unit.add([ap.Variable("c0"), ap.Variable("c1")])
        liver = ap.Model("liver", [ap.Variable("c3"), ap.Variable("c4")])
        unit.add(liver)
        unit.add(ap.Variable("c2"))
        # print model structure as a tree in stdout
        unit.tree()
        out, err = capfd.readouterr()  # get stdout and stderr
        # check answer
        expected_out = """me:
  y[c0]
  y[c1]
  liver:
    y[c3]
    y[c4]
  y[c2]
"""
        expected_err = ""
        assert out == expected_out
        assert err == expected_err

    def test_add_change_to_unit(self, capfd):
        # tested process
        unit = ap.Unit("model")
        unit.add(
            [
                ap.Variable("X1"),
                ap.Variable("X2"),
                ap.Variable("k"),
                ap.Change({"X1": "-k*X1", "X2": "k*X1"}),
            ]
        )
        # print model structure as a tree in stdout
        unit.tree()
        out, err = capfd.readouterr()  # get stdout and stderr
        # check answer
        expected_out = """model:
  y[X1]
  y[X2]
  y[k]
  Ch[X1->k*X1->X2]
"""
        expected_err = ""
        assert out == expected_out
        assert err == expected_err

    def test_add_find_name(self):
        # tested process
        unit = ap.Unit("me")
        unit.add([ap.Variable("c0"), ap.Variable("c1")])
        liver = ap.Model("liver", [ap.Variable("c3"), ap.Variable("c4")])
        kidney = ap.Model("kidney", [ap.Variable("X_glm"), ap.Variable("V_glm")])
        unit.add([liver, kidney])
        unit.add(ap.Variable("c2"))
        # results
        result1 = unit.find("me")
        result2 = unit.find("c0")
        result3 = unit.find("liver")
        result4 = unit.find("c3")
        result5 = unit.find("kidney")
        result6 = unit.find("X_glm")
        result7 = unit.find("Nothing")
        # check answer
        expect1 = "me"
        expect2 = "me/c0"
        expect3 = "me/liver"
        expect4 = "me/liver/c3"
        expect5 = "me/kidney"
        expect6 = "me/kidney/X_glm"
        expect7 = None
        assert result1 == expect1
        assert result2 == expect2
        assert result3 == expect3
        assert result4 == expect4
        assert result5 == expect5
        assert result6 == expect6
        assert result7 == expect7

    def test_remove_by_name(self):
        unit = ap.Unit("model")
        unit.add(
            [
                ap.Variable("X1"),
                ap.Variable("X2"),
                ap.Variable("k12"),
                ap.Change({"X1": "-k12*X1", "X2": "k12*X1"}),
                ap.Change({"X1": "k21*X2", "X2": "-k21*X2"}),
            ]
        )
        expect = unit.model.components.copy()

        # tested process
        unit.remove("Ch[X1->k12*X1->X2]")
        unit.remove("X1")
        result = unit.model.components

        # delete components mannually
        del expect["Ch[X1->k12*X1->X2]"]
        del expect["X1"]

        assert result == expect
