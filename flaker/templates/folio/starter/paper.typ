#import "/packages.typ": *
#import "/ieee.typ": *

#show: paper.with(
  title: text(
    size: 24pt,
    weight: "bold",
  )[__TITLE__],
  authors: (
    (
      name: "__AUTHOR__",
      department: [__DEPENDENCY__],
      organization: [Delft University of Technology],
      location: [Delft, Netherlands],
      email: "author@tudelft.nl",
    ),
  ),
  abstract: [
    Autonomous robotic swarms offer transformative potential in subterranean exploration, disaster response, and planetary speleology. In these scenarios, the absence of global navigation satellite systems (GNSS) presents a fundamental challenge. Individual agents equipped solely with visual-inertial odometry (VIO) inevitably experience unbounded dead-reckoning drift over prolonged mission horizons. We formulate a decentralized factor graph framework with inter-agent ultra-wideband ranging constraints to bound global localization drift.
  ],
  paper-size: "a4",
  index-terms: (
    "Decentralized Estimation",
    "Factor Graph Optimization",
    "Autonomous Swarms",
    "Ultra-Wideband",
  ),
  bibliography: bibliography("/library.bib", title: auto),
)

#v(1em)

= Introduction

Autonomous robotic swarms operating in GNSS-denied environments require real-time state estimation with rigorous spatial drift bounds. Centralized servers introduce catastrophic single points of failure, while raw local odometry experiences quadratic variance growth $O(t^2)$.

= System Formulation

Consider a swarm comprising $N$ autonomous aerial agents indexed by $cal(V) = {1, dots, N}$. The time-varying communication topology is represented by an undirected graph $cal(G)(t) = (cal(V), cal(E)(t))$.

== Agent Kinematics & States

Each agent $i in cal(V)$ tracks its state vector $bold(x)_i in "SE"(3) times RR^3$:

$ bold(x)_i = mat(bold(p)_i; bold(R)_i; bold(v)_i) $

The discrete-time state propagation follows nonlinear IMU kinematics driven by accelerometer and gyroscope measurements subject to Gaussian noise $bold(w)_i tilde.op cal(N)(bold(0), bold(Q)_i)$.

== Distributed Factor Graph Optimization

Relative range measurements acquired via Ultra-Wideband (UWB) ranging provide metric distance constraints:

$ z_(i j) = ||bold(p)_i - bold(p)_j|| + eta_(i j), quad (i,j) in cal(E)(t) $

The objective minimizes the negative log-likelihood across the edge set:

$ min_(bold(x)) sum_(i in cal(V)) f_i (bold(x)_i) + sum_((i,j) in cal(E)) g_(i j) (bold(x)_i, bold(x)_j) $

= Experimental Verification

Evaluation across subterranean mine simulation benchmarks confirms exponential consensus convergence whenever $lambda_2(cal(L)) > 0$.

#align(center)[
  #table(
    columns: (auto, 1fr, 1fr, auto),
    inset: 8pt,
    align: (col, row) => if row == 0 { center + horizon } else { left + horizon },
    stroke: (x, y) => if y == 0 { (bottom: 1.5pt + black) } else { (bottom: 0.5pt + gray) },
    [*Node*], [*Algorithm Tier*], [*Status*], [*ATE (m)*],
    [*MAV-01*], [Distributed ADMM], [`Converged`], [0.042],
    [*MAV-02*], [Decoupled Consensus], [`Converged`], [0.038],
    [*MAV-03*], [Decentralized EKF], [`Legacy`], [0.185],
  )
]

= Conclusion

We formulated a decentralized estimation architecture for autonomous MAV swarms. By combining local odometry with inter-agent UWB ranging, the swarm bounds localization drift without centralized coordination.
