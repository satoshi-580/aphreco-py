import aphreco as ap
import pytest


@pytest.mark.hybrid
class TestTypicalSolve:
    def test_outtime_format(self, phase1):
        simulator = ap.Simulator()
        start = 0
        stop = 60
        step = 0.1
        simres = simulator.run(phase1, (start, stop, step))
        assert True

    def test_simulate(self, phase1):
        simulator = ap.Simulator()
        smptimes = [0.0, 10.0, 12.5, 25.75]
        simres = simulator.run(phase1, smptimes)
        assert True
