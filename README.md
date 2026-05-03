# Aphreco-Python
**A**ssembled **ph**ysiological **re**ctangles **co**llection (Aphreco) is a Python library for developing a small-scale physiologically-based kinetic model.

## Installation
```
$ git clone https://github.com/satoshi-580/aphreco-py.git
$ pip install ./aphreco-py/
```

Make cargo comand possible by installing [Rust](https://rust-lang.org/).
```
$ cargo --version
```

## Example
Jupyter Notebook:

```
import aphreco as ap
from matplotlib import pyplot as plt
```

```
cmpt2 = ap.Model("Cmpt2")
cmpt2.add([
    ap.P("initime", 0.0),
    ap.Y("X1", 100.0),
    ap.Y("X2"),
    ap.P("k12", 0.2),
    ap.P("k21", 0.05),
])
cmpt2.add(ap.Con({"X1": "-k12*X1", "X2": "k12*X1"}))
cmpt2.add(ap.Con({"X2": "-k21*X2", "X1": "k21*X2"}))
cmpt2.add([ap.P("ke"), ap.Con({"X1": "-ke*X1"})])
print(cmpt2)
```

```
out_time = [float(i) / 100 for i in range(1000)]
simulator = ap.Simulator()
simres = simulator.run(cmpt2, out_time)
```

```
fig, ax = plt.subplots(1, 1, figsize=(4, 4))
ax.plot(simres.t, simres.y.iloc[:, 0], "k", label="X1")
ax.plot(simres.t, simres.y.iloc[:, 1], "r", label="X2")
plt.legend()
plt.show()
```
