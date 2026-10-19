#import "/packages.typ": *
#import "/report.typ": *

#show: report.with(
  title: [__TITLE__],
  author: "__AUTHOR__",
  dependency: "__DEPENDENCY__",
  date: "__DATE__",
)

This document uses strictly native Typst markup and imports modular packages from `/packages.typ`.

= Executive Summary

Modern engineering systems demand rigorous specification, reproducible documentation, and verified analytical models. This report outlines the operational envelope, hardware-in-the-loop verification, and dynamic state-space models.

= Mathematical Formulation

Consider the state-space dynamic model characterized by:

$
  dot(bold(x))(t) &= bold(A) bold(x)(t) + bold(B) bold(u)(t) \
  bold(y)(t)       &= bold(C) bold(x)(t) + bold(D) bold(u)(t)
$

Under stabilizability conditions, there exists a state-feedback gain $bold(K)$ such that the closed-loop eigenvalues of $(bold(A) - bold(B) bold(K))$ lie strictly in the left half of the complex plane $CC^-$.

= Subsystem Benchmarks

Performance across distributed nodes was validated against official benchmarks.

#align(center)[
  #table(
    columns: (auto, 1.5fr, 1fr, auto),
    inset: 9pt,
    align: (col, row) => if row == 0 { center + horizon } else { left + horizon },
    stroke: (x, y) => if y == 0 { (bottom: 1.5pt + black) } else { (bottom: 0.5pt + gray) },
    [*Node ID*], [*Component Name*], [*Status*], [*Throughput*],
    [*NODE-01*], [Ingestion Pipeline], [`Nominal`], [420.5 MB/s],
    [*NODE-02*], [Consensus Engine], [`Nominal`], [180.2 MB/s],
    [*NODE-03*], [Matrix Solver Core], [`Optimal`], [950.0 MB/s],
  )
]

= Algorithm Implementation

```python
def update_state(x, u, dt=0.01):
    """Computes single-step state propagation."""
    return x + (A @ x + B @ u) * dt
```

= Conclusions

The architecture satisfies all real-time requirements with zero dynamic memory allocations in the inner loop.

#bibliography("/library.bib", title: "References")
