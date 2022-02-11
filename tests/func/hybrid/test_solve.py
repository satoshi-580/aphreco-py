import aphreco as ap
import pytest


@pytest.mark.hybrid
class TestTypicalSolve:
    def test_smptime_format(self, phase1):
        simulator = ap.Simulator()

        # tuple of (start, stop, step)
        start, stop, step = (0, 0.05, 0.01)
        simres = simulator.run(phase1, (start, stop, step))
        assert simres.t == [0.0, 0.01, 0.02, 0.03, 0.04]

        # list of [timepoints]
        smptimes = [0.0, 0.1, 0.2, 0.5, 1.0, 2.25, 5.0]
        simres = simulator.run(phase1, smptimes)
        assert simres.t == smptimes

        # list of [timepoints]
        smptimes = [0.0, 0.1, 0.2, 0.5, 1.0, 2.25]
        simres = simulator.run(phase1, smptimes)

        assert True

    def test_simulate(self, phase1):
        simulator = ap.Simulator()
        smptimes = [0.0, 10.0, 12.5, 25.75]
        simres = simulator.run(phase1, smptimes)
        assert True
