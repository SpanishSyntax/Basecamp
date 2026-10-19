---
title: "__TITLE__"
author: "__AUTHOR__"
dependency: "__DEPENDENCY__"
email: ""
abstract: ""
keywords: ""
mode: "paper"
preset: "ieee"
engine: "typst" # Options: typst | latex
---

# Introduction

Autonomous robotic swarms offer transformative potential in subterranean exploration, disaster response, and planetary speleology. In these scenarios, the absence of global navigation satellite systems (GNSS) presents a fundamental challenge. Individual agents equipped solely with visual-inertial odometry (VIO) inevitably experience unbounded dead-reckoning drift over prolonged mission horizons.

While centralized estimation servers achieve high accuracy, they introduce single points of failure and require high-bandwidth communication that cannot be sustained through rock strata and reinforced concrete structures. Consequently, fully decentralized cooperative estimation is essential.

# System Architecture & Formulation

Consider a swarm comprising $N$ autonomous agents indexed by $\mathcal{V} = \{1, \dots, N\}$. The time-varying communication topology is characterized by an undirected graph $\mathcal{G}(t) = (\mathcal{V}, \mathcal{E}(t))$.

## Agent Kinematics

Each agent $i \in \mathcal{V}$ tracks its state vector $\mathbf{x}_i \in \mathrm{SE}(3) \times \mathbb{R}^3$, consisting of position $\mathbf{p}_i$, orientation $\mathbf{R}_i$, and linear velocity $\mathbf{v}_i$:

$$
\mathbf{x}_i = \begin{bmatrix} \mathbf{p}_i \\ \mathbf{R}_i \\ \mathbf{v}_i \end{bmatrix}
$$

The discrete-time state propagation follows nonlinear IMU kinematics driven by accelerometer and gyroscope measurements subject to zero-mean Gaussian noise $\mathbf{w}_i \sim \mathcal{N}(\mathbf{0}, \mathbf{Q}_i)$.

## Distributed Factor Graph Optimization

Inter-agent distance measurements acquired via Ultra-Wideband (UWB) two-way ranging provide relative metric constraints between neighboring agents:

$$
z_{ij} = \|\mathbf{p}_i - \mathbf{p}_j\| + \eta_{ij}, \quad (i,j) \in \mathcal{E}(t)
$$

The global objective corresponds to minimizing the joint negative log-likelihood:

$$
\min_{\mathbf{x}} \sum_{i \in \mathcal{V}} f_i(\mathbf{x}_i) + \sum_{(i,j) \in \mathcal{E}} g_{ij}(\mathbf{x}_i, \mathbf{x}_j)
$$

We decouple this optimization using the Alternating Direction of Multipliers (ADMM), enabling parallel, locally decoupled consensus iterations.

# Experimental Results

We evaluate the proposed framework across both high-fidelity ROS 2 Gazebo simulations of subterranean mine shafts and real-world flight trials utilizing custom nano-quadrotor platforms.

The convergence rate of consensus iterations remains exponential as long as the second smallest eigenvalue of the graph Laplacian satisfies $\lambda_2(\mathcal{L}) > 0$.

# Conclusion

We presented a decentralized estimation architecture for autonomous MAV swarms in GPS-denied environments. By combining local VIO with inter-agent UWB ranging within a distributed factor graph, the swarm bounds localization drift without central coordination. Future work will investigate Byzantine-fault-tolerant consensus under active communication jamming.
