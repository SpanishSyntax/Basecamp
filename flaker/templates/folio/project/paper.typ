// ========================================================
// FOLIO IEEE ACADEMIC PAPER TEMPLATE
// Powered by @preview/charged-ieee:0.1.4 with Markdown Interop
// ========================================================
#import "@preview/charged-ieee:0.1.4": ieee
#import "packages.typ": *

#let horizontalrule = line(length: 100%, stroke: 0.5pt + rgb("#a1a1aa"))

#let paper(
  title: "Untitled IEEE Paper",
  author: none,
  authors: (),
  dependency: none,
  email: none,
  abstract: none,
  keywords: none,
  index-terms: (),
  paper: "us-letter",
  paper-size: none,
  bibliography: none,
  date: none,
  doc,
  ..sink,
) = {
  let final-title = title
  let final-author = author
  let final-dep = dependency
  let final-email = email
  let final-abstract = abstract
  let final-paper-size = if paper-size != none { paper-size } else { paper }
  let final-bibliography = bibliography

  let final-index-terms = if index-terms.len() > 0 {
    index-terms
  } else if keywords != none and keywords != "" {
    keywords.split(",").map(k => k.trim())
  } else {
    ()
  }

  let final-authors = if authors.len() > 0 {
    authors
  } else if final-author != none {
    (
      (
        name: final-author,
        department: final-dep,
        organization: final-dep,
        email: final-email,
      ),
    )
  } else {
    (
      (
        name: "Author",
        department: "Department",
        organization: "Organization",
        email: none,
      ),
    )
  }

  show: ieee.with(
    title: final-title,
    authors: final-authors,
    abstract: if final-abstract != none [ #final-abstract ] else { [] },
    index-terms: final-index-terms,
    paper-size: final-paper-size,
    bibliography: final-bibliography,
  )

  // Markdown code block formatting
  show raw.where(block: true): it => block(
    fill: rgb("#f4f4f5"),
    inset: 8pt,
    radius: 3pt,
    width: 100%,
    stroke: 0.3pt + rgb("#d4d4d8"),
    it,
  )

  show raw.where(block: false): it => box(
    fill: rgb("#f4f4f5"),
    inset: (x: 3pt, y: 1pt),
    radius: 2pt,
    it,
  )

  doc
}

#let conf = paper

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

Hardware experiments across 6 quadrotor aerial platforms demonstrated sub-15cm absolute localization accuracy over a 45-minute continuous mission.

#align(center)[
  #table(
    columns: (auto, 1fr, 1fr, auto),
    inset: 6pt,
    align: (col, row) => if row == 0 { center } else { left },
    stroke: 0.4pt + rgb("#a1a1aa"),
    [*Trial ID*], [*Swarm Size*], [*RMSE Drift (m)*], [*Consensus Rate*],
    [`EXP-01`], [3 Agents], [0.082], [100 Hz],
    [`EXP-02`], [6 Agents], [0.124], [80 Hz],
    [`EXP-03`], [12 Agents], [0.149], [50 Hz],
  )
]

= Conclusions

We demonstrated fully decentralized cooperative localization with guaranteed drift bounds under intermittent inter-agent ranging constraints.
