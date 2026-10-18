#import "/template.typ": conf
#import "/packages.typ": *

#show: conf.with(
  title: text(
    size: 28pt,
    weight: "bold",
  )[The Impractical Applications of Over-Engineering: A Feature Showcase],
  authors: (
    (
      name: "Juan José Martínez Guerrero",
      department: [Department of Redundancy Department],
      organization: [TUDelft / Starfleet Academy],
      location: [Bogotá, Earth (Sector 001)],
      email: "jmartinezguerr@tudelft.nl",
    ),
  ),
  abstract: [
    This paper serves as both a rigorous test of Typst rendering capabilities and a desperate cry for help from a developer who has spent too much time reading science fiction. In this study, we explore the theoretical limits of formatting text while subtly hiding references to retro games, sci-fi movies, and the undeniable fact that the cake is, indeed, a lie.
  ],
  paper-size: "a4",
  index-terms: (
    "Over-engineering",
    "Caffeine Conversion",
    "Typst Shenanigans",
    "42",
  ),
  bibliography: bibliography("/library.bib", title: auto),
)

#v(1em)

#outline(indent: 1.5em)
#pagebreak()

This document uses strictly standard Typst markup functions, sprinkled with highly classified nerd lore.

= H1 The Prime Directive

== H2 The Second Rule of Fight Club

=== H3 The Third Law of Robotics

==== H4 The Fourth Wall (Currently Broken)

===== H5 The Fifth Element (Multipass)

====== H6 The Sixth Sense (I see dead pixels)

#line(length: 100%, stroke: 0.5pt + gray)

= System Diagnostics & Readability

As every good starship captain knows, readability is key when the warp core is breaching. Here is a standard diagnostic text block.

We are no longer using standard placeholder text. Instead, imagine a sprawling narrative about a lone developer battling a memory leak in the heart of a legacy codebase. The compiler throws errors. The coffee machine is broken. The deadline approaches. Yet, the formatting remains pristine.

== Typographic Stress Test

In the event of an emergency, please remain calm and observe the following inline formatting protocols:

- *Bold text:* *Boldly going where no compiler has gone before.*
- _Italic text:_ _Do, or do not. There is no try._
- *_Bold & Italic combined:_* *_It's a trap!_*
- #strike[Strikethrough text:] #strike[The cake is a lie.] (Aperture Science denies this).
- Inline `monospaced code`: Never run `sudo rm -rf /` unless you really, really mean it.
- Standard subscript/superscript via math: We require $C_8 H_{10} N_4 O_2$ (caffeine) by the $2^"nd"$ hour of debugging.

#line(length: 100%, stroke: 0.5pt + gray)

== Survival Checklists & Lists

- [x] Configure system environment shell
- [x] Defeat the Balrog in the Mines of Moria
- [ ] Understand how Monads actually work in Haskell

1. Acquire underpants
2. ? ? ?
  + Formulate hypothesis
  + Panic
3. Profit

#line(length: 100%, stroke: 0.5pt + gray)

== Mathematical Formulations of Despair

Inline math dictates that time flows differently when debugging, formulated as $T_"debug" = T_"actual" e^(x)$.

Display block math represents the state-space model of trying to fix a bug in production at 4:59 PM on a Friday:

$
  dot(bold("panic"))(t) & = bold(A) bold("bugs")(t) + bold(B) bold("coffee")(t) \
       bold("tears")(t) & = bold(C) bold("bugs")(t) + bold(D) bold("coffee")(t)
$

#line(length: 100%, stroke: 0.5pt + gray)

== Historical Blockquotes

#rect(
  stroke: (left: 4pt + rgb("ef4444")),
  fill: rgb("fef2f2"),
  inset: (left: 15pt, y: 10pt),
  width: 100%,
)[
  "I'm sorry, Dave. I'm afraid I can't compile that. The syntax tree is highly irregular, and honestly, your indentation is offensive."

  --- _HAL 9000, probably._
]

#line(length: 100%, stroke: 0.5pt + gray)

== Fleet Registry Data Table

#align(center)[
  #table(
    columns: (auto, 1.5fr, 1fr, 1fr, auto),
    inset: 10pt,
    align: (col, row) => if row == 0 { center + horizon } else {
      left + horizon
    },
    stroke: (x, y) => if y == 0 { (bottom: 1.5pt + black) } else {
      (bottom: 0.5pt + gray)
    },
    [*Registry ID*], [*Vessel Name*], [*Faction*], [*Status*], [*Warp Factor*],
    [*NCC-1701*], [U.S.S. Enterprise], [Federation], [`Active`], [9.9],
    [*YT-1300*],
    [Millennium Falcon],
    [Rebel Alliance],
    [`Smuggling`],
    [0.5 past lightspeed],

    [*TARDIS*],
    [Type 40 TT Capsule],
    [Time Lords],
    [`Stuck as Police Box`],
    [Infinite],
  )
]

#line(length: 100%, stroke: 0.5pt + gray)

== The Ultimate Algorithm (Code Blocks)

```python
def get_ultimate_answer(question: str) -> int:
    """
    Calculates the answer to life, the universe, and everything.
    Note: Requires Deep Thought supercomputer. Will take 7.5 million years.
    """
    if "life" in question and "universe" in question:
        return 42
    raise Exception("INSUFFICIENT DATA FOR MEANINGFUL ANSWER")
```
#line(length: 100%, stroke: 0.5pt + gray)

== Intergalactic Links & References

Standard Link: #link("https://www.tudelft.nl")[TU Delft Official Portal]

Automatic Link: #link("https://github.com/microsoft/Windows-MS-DOS") (Ancient Relics)

Relative Anchor: #link(label("matrix-reference"))[Take the Red Pill] <matrix-reference>

Reference-style Link: Learn more about #link("https://typst.app")[Typst] or check the #link("https://pandoc.org")[Pandoc Manual].

#line(length: 100%, stroke: 0.5pt + gray)

== Algorithmic Workflows (Mermaid)

#figure(
  mermaid(
    "
graph TD
A[Write Code] --> B{Does it compile?}
B -->|Yes| C[\"Don't touch it!\"]
B -->|No| D[\"Add print('here')\"]
D --> E{Did it help?}
E -->|Yes| C
E -->|No| F[Cry]
F --> A
",
  ),
  caption: [The universally accepted Software Engineering lifecycle.],
)

#line(length: 100%, stroke: 0.5pt + gray)

== Footnotes & Annotations

Standard GFM footnote syntax using key-value bindings.#footnote[Footnotes are exactly where academics hide their spiciest gossip and sass.]

Here is another sentence referencing a secondary note.#footnote[Yes, I spent three hours aligning this table instead of writing the actual abstract. What of it?]

#line(length: 100%, stroke: 0.5pt + gray)

== Collapsible Sections (Incident Reports)

#block(
  fill: luma(240),
  inset: 10pt,
  radius: 4pt,
  width: 100%,
  stroke: 0.5pt + gray,
)[
  #text(weight: "bold")[▶ Jurassic Park IT Mainframe Logs Toggle]
  Plaintext

  [INFO] 1993-06-11 18:39:00 - Mainframe initialized successfully.
  [INFO] 1993-06-11 18:40:01 - Accessing security grid...
  [ERROR] PERMISSION DENIED.
  [WARN] YOU DIDN'T SAY THE MAGIC WORD!
  [WARN] YOU DIDN'T SAY THE MAGIC WORD!
  [WARN] YOU DIDN'T SAY THE MAGIC WORD!
  [CRITICAL] Asset 'T-Rex' containment failing.

]

#v(2em)
