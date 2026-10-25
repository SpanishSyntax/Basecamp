// ========================================================
// FOLIO PRESENTATION TEMPLATE (16:9 Widescreen / 1080p)
// Apple Keynote-Inspired Minimalist Design System for Typst
// ========================================================
#import "/packages.typ": *

#let themes = (
  dark: (
    bg: rgb("#000000"),
    text: rgb("#f5f5f7"),
    heading: rgb("#ffffff"),
    subheading: rgb("#a1a1a6"),
    muted: rgb("#86868b"),
    subtle: rgb("#424245"),
    accent: rgb("#2997ff"),
    card-bg: rgb("#161618"),
    border: rgb("#2c2c2e"),
    code-bg: rgb("#121214"),
    inserted: rgb("#30d158"),
    highlight: rgb("#ffd60a"),
  ),
  light: (
    bg: rgb("#fbfbfd"),
    text: rgb("#1d1d1f"),
    heading: rgb("#000000"),
    subheading: rgb("#515154"),
    muted: rgb("#86868b"),
    subtle: rgb("#d2d2d7"),
    accent: rgb("#0071e3"),
    card-bg: rgb("#f5f5f7"),
    border: rgb("#e5e5ea"),
    code-bg: rgb("#f0f0f2"),
    inserted: rgb("#248a3d"),
    highlight: rgb("#ffdf33"),
  ),
)

#let fonts = (
  sans: (
    "SF Pro Display",
    "SF Pro Text",
    "Inter Display",
    "Inter",
    "Helvetica Neue",
    "Liberation Sans",
    "FreeSans",
  ),
  display: (
    "SF Pro Display",
    "Inter Display",
    "Inter",
    "Helvetica Neue",
    "FreeSans",
  ),
  mono: (
    "SF Mono",
    "Iosevka NF",
    "Source Code Pro",
    "Menlo",
    "Consolas",
  ),
)

// In Markdown presentations, horizontal rules (---) create slide breaks
#let horizontalrule = pagebreak(weak: true)

#let slides(
  title: "Folio Presentation",
  subtitle: none,
  author: "Author",
  dependency: none,
  date: none,
  theme: "dark",
  doc,
  ..sink,
) = {
  let final-title = title
  let final-subtitle = subtitle
  let final-author = author
  let final-dep = dependency
  let final-date = date
  let t = themes.at(theme, default: themes.dark)

  // ==========================================
  // PAGE SETUP (16:9 Aspect Ratio)
  // ==========================================
  set page(
    paper: "presentation-16-9",
    fill: t.bg,
    margin: (
      top: 2.4cm,
      bottom: 1.8cm,
      x: 2.8cm,
    ),
    footer: context {
      set text(
        font: fonts.sans,
        size: 9.5pt,
        fill: t.muted,
      )
      let cur = counter(page).get().first()
      let tot = counter(page).final().first()
      if cur > 1 {
        grid(
          columns: (1fr, 1fr),
          align(left)[
            #if final-author != none [#final-author]
            #if final-title != none [ #h(6pt)•#h(6pt) #final-title]
          ],
          align(right)[
            #str(cur) #h(4pt)/#h(4pt) #str(tot)
          ],
        )
      }
    },
  )

  // ==========================================
  // TYPOGRAPHY
  // ==========================================
  set text(
    font: fonts.sans,
    size: 17pt,
    fill: t.text,
    lang: "en",
  )

  set par(
    justify: false,
    leading: 0.85em,
    spacing: 1.4em,
  )

  // ==========================================
  // SLIDE HEADINGS
  // ==========================================
  show heading.where(level: 1): it => {
    pagebreak(weak: true)
    v(0.4em)
    block(
      width: 100%,
      below: 1.4em,
      text(
        font: fonts.display,
        size: 30pt,
        weight: "bold",
        fill: t.heading,
        tracking: -0.035em,
        it.body,
      ),
    )
  }

  show heading.where(level: 2): it => block(
    above: 1.3em,
    below: 0.8em,
    text(
      font: fonts.display,
      size: 20pt,
      weight: "semibold",
      fill: t.at("subheading", default: t.text),
      tracking: -0.02em,
      it.body,
    ),
  )

  show heading.where(level: 3): it => block(
    above: 1.0em,
    below: 0.6em,
    text(
      font: fonts.sans,
      size: 16pt,
      weight: "medium",
      fill: t.muted,
      tracking: -0.01em,
      it.body,
    ),
  )

  // Lists with Apple-grade spacing and subtle markers
  set list(
    spacing: 1.25em,
    marker: text(fill: t.muted, size: 12pt)[•],
  )
  set enum(
    spacing: 1.25em,
  )

  // Links
  show link: it => text(
    fill: t.accent,
    underline(offset: 2pt, it),
  )

  // Code Blocks (Xcode / macOS Terminal Aesthetic)
  show raw.where(block: true): it => block(
    fill: t.code-bg,
    inset: 16pt,
    radius: 8pt,
    width: 100%,
    stroke: 0.5pt + t.border,
    outset: 0pt,
    [
      #set text(
        font: fonts.mono,
        size: 13pt,
        fill: t.text,
      )
      #it
    ],
  )

  // Inline Code (Discreet pill badge)
  show raw.where(block: false): it => box(
    fill: t.card-bg,
    inset: (x: 6pt, y: 2pt),
    radius: 4pt,
    stroke: 0.4pt + t.border,
    text(
      font: fonts.mono,
      size: 13.5pt,
      fill: t.text,
      it,
    ),
  )

  // Blockquotes & Callouts (Sleek Keynote Card)
  show quote.where(block: true): it => block(
    fill: t.card-bg,
    inset: (x: 18pt, y: 14pt),
    radius: 8pt,
    stroke: (left: 3pt + t.accent),
    width: 100%,
    text(
      fill: t.text,
      it.body,
    ),
  )

  // Math equations
  show math.equation.where(block: true): it => block(
    width: 100%,
    inset: (y: 10pt),
    align(center, text(size: 21pt, it)),
  )

  // ==========================================
  // TITLE SLIDE HERO (Slide 1 - Apple Keynote Style)
  // ==========================================
  align(center + horizon)[
    #text(
      font: fonts.sans,
      size: 11pt,
      weight: "semibold",
      tracking: 0.16em,
      fill: t.muted,
    )[KEYNOTE]

    #v(1.4em)

    #text(
      font: fonts.display,
      size: 38pt,
      weight: "bold",
      fill: t.heading,
      tracking: -0.04em,
    )[#final-title]

    #if final-subtitle != none [
      #v(0.8em)
      #text(
        font: fonts.display,
        size: 19pt,
        weight: "regular",
        fill: t.muted,
        tracking: -0.015em,
      )[#final-subtitle]
    ]

    #v(3.0em)

    #if final-author != none [
      #text(
        size: 15pt,
        weight: "medium",
        fill: t.text,
      )[#final-author]
    ]

    #if final-dep != none [
      #v(0.35em)
      #text(
        size: 12.5pt,
        fill: t.muted,
      )[#final-dep]
    ]

    #if final-date != none [
      #v(0.35em)
      #text(
        size: 11pt,
        fill: t.subtle,
      )[#final-date]
    ]
  ]

  doc
}

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

The decentralized framework converges to bounded error envelopes under arbitrary topology switching.

#bibliography("/library.bib", title: "References")
