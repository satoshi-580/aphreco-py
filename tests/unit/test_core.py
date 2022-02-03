from collections import OrderedDict

import aphreco as ap
import pytest


class TestInstanciation:
    def test_Variable_init(self, capfd):
        # creates Variable instances
        with pytest.raises(TypeError):
            ap.Variable()

        var1 = ap.Variable("var1")
        assert var1.name == "var1"
        assert var1.value == 0.0
        assert var1.type == ap.ItemType.Y

        var2 = ap.Variable("__PARAMETER_NAME__", 123.456, "p")
        assert var2.name == "__PARAMETER_NAME__"
        assert var2.value == 123.456
        assert var2.type == ap.ItemType.P

    def test_Model_init(self):
        # creates Model instances
        model1 = ap.Model()
        assert model1.name == ""
        assert model1.type == ap.ItemType.MODEL
        assert model1.hide == False
        assert model1.children == OrderedDict()

        model2 = ap.Model("model2")
        assert model2.name == "model2"
        assert model2.type == ap.ItemType.MODEL

        model3 = ap.Model(name="BODY", hide=True)
        assert model3.name == "BODY"
        assert model3.hide == True
