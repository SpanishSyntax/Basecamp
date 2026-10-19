---
title: "__TITLE__"
subtitle: "__SUBTITLE__"
author: "__AUTHOR__"
dependency: "__DEPENDENCY__"
date: "__DATE__"
mode: "slides"
# Engine options: typst | latex
engine: "__ENGINE__"
theme: "__THEME__"
aspect-ratio: "16-9"
---

# Problem Formulation

Autonomous aerial swarms operating in GPS-denied environments (tunnels, sub-surface mines, planetary caves) face severe drift.

- **Sensor limitations**: IMU bias drifts quadratically over time $O(t^2)$
- **Communication constraints**: Bandwidth drops sharply through rock strata
- **Scalability bottlenecks**: Centralized state estimators fail beyond $N > 10$ agents

---

# System Architecture

We employ a decentralized factor graph formulation over dynamic communication topology $\mathcal{G} = (\mathcal{V}, \mathcal{E})$.

- **Local Odometry**: Visual-Inertial Odometry running at 200 Hz
- **Inter-Agent Ranging**: Asynchronous Ultra-Wideband (UWB) two-way ranging
- **Distributed Consensus**: Distributed Gauss-Newton optimization

---

# Mathematical Model

Each agent $i \in \mathcal{V}$ solves a constrained optimization problem:

$$
\min_{\mathbf{x}_i} \sum_{j \in \mathcal{N}_i} \|\mathbf{x}_i - \mathbf{x}_j - \mathbf{d}_{ij}\|_{\mathbf{\Sigma}_{ij}}^2
$$

> **Key Guarantee**: Under graph connectivity $\lambda_2(\mathcal{L}) > 0$, consensus converges with exponential rate $\rho < 1$.

---

# Edge Implementation

```python
def compute_consensus_step(x_local, neighbors, weights):
    """Computes distributed consensus gradient descent step."""
    gradient = sum(w * (x_local - x_n) for x_n, w in zip(neighbors, weights))
    return x_local - 0.05 * gradient
```

- Zero memory allocations in inner loop
- Deterministic sub-millisecond compute budget

---

# Conclusion & Next Steps

1. **Hardware-in-the-loop validation** on 16 crazyflie nano-quadrotors
2. **Resilience under jamming**: Byzantine-tolerant consensus protocols [@ieee_evans]
3. **Open-source release**: Package available under MIT license
