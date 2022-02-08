import aphreco as ap
import pytest


@pytest.mark.hybrid
class TestTypicalSolve:
    def test_outtime_format(self, phase1):
        step = 0.1
        startx10 = 0  # start = startx10 * step
        stopx10 = 600  # stop = stopx10 * step
        outtime = [float(i) * step for i in range(startx10, stopx10)]

        simulator = ap.Simulator()
        simres = simulator.run(phase1, outtime)
        assert simres.t == outtime

        import numpy as np

        outtime = np.linspace(0, 60, 601)
        simres = simulator.run(phase1, outtime)
        assert (simres.t == outtime).all()

    def test_simulate(self, phase1):
        step = 0.1
        startx10 = 0  # start = startx10 * step
        stopx10 = 600  # stop = stopx10 * step
        outtime = [float(i) * step for i in range(startx10, stopx10)]

        simulator = ap.Simulator()
        simres = simulator.run(phase1, outtime)

        assert simres.t == outtime
