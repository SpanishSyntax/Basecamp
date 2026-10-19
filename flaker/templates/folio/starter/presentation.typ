#import "/packages.typ": *
#import "/slides.typ": *

#show: slides.with(
  title: [__TITLE__],
  subtitle: [__SUBTITLE__],
  author: [__AUTHOR__],
  dependency: [__DEPENDENCY__],
  date: [__DATE__],
  theme: "__THEME__",
)

= Problem Formulation

Autonomous aerial swarms operating in GPS-denied environments face severe drift.

- *Sensor limitations*: IMU bias drifts quadratically over time $O(t^2)$
- *Communication constraints*: Bandwidth drops sharply through rock strata
- *Scalability bottlenecks*: Centralized state estimators fail beyond $N > 10$ agents

---

= System Architecture

We employ a decentralized factor graph formulation over dynamic communication topology $cal(G) = (cal(V), cal(E))$.

- *Local Odometry*: Visual-Inertial Odometry running at 200 Hz
- *Inter-Agent Ranging*: Asynchronous Ultra-Wideband (UWB) two-way ranging
- *Distributed Consensus*: Distributed Gauss-Newton optimization

---

= Mathematical Model

Each agent $i in cal(V)$ solves a constrained optimization problem:

$ min_(bold(x)_i) sum_(j in cal(N)_i) ||bold(x)_i - bold(x)_j - bold(d)_(i j)||_bold(Sigma)_(i j)^2 $

#quote(block: true)[
  *Key Guarantee*: Under graph connectivity $lambda_2(cal(L)) > 0$, consensus converges with exponential rate $rho < 1$.
]

---

= Edge Implementation

```python
def compute_consensus_step(x_local, neighbors, weights):
    """Computes distributed consensus gradient descent step."""
    gradient = sum(w * (x_local - x_n) for x_n, w in zip(neighbors, weights))
    return x_local - 0.05 * gradient
```

- Zero memory allocations in inner loop
- Deterministic sub-millisecond compute budget

---

= Conclusions & References

1. *Hardware-in-the-loop validation* on 16 nano-quadrotors
2. *Resilience under jamming*: Byzantine-tolerant consensus protocols
3. *Scholarly References*: Citations compiled from bibliography

#bibliography("/library.bib", title: "References")
