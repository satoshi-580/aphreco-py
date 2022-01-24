from .core import Beat, Box, EdgeC, EdgeR, Obs, P, Var, X, Y
from .solve import Dopri45, GeneticAlgorithm, NelderMead, Optimizer, Rk4, Simulator
from .unit import Unit

__version__ = "0.1.0"
print(f"aphreco {__version__}")
