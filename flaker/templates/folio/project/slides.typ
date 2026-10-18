// ========================================================
// FOLIO PRESENTATION TEMPLATE (16:9 Widescreen / 1080p)
// Minimal, ultra-crisp slide deck design system for Typst
// ========================================================

#let themes = (
  dark: (
    bg: rgb("#09090b"),
    text: rgb("#f4f4f5"),
    heading: rgb("#ffffff"),
    muted: rgb("#a1a1aa"),
    accent: rgb("#38bdf8"),
    card-bg: rgb("#18181b"),
    border: rgb("#27272a"),
    code-bg: rgb("#121215"),
    inserted: rgb("#4ade80"),
    highlight: rgb("#fde047"),
  ),
  light: (
    bg: rgb("#ffffff"),
    text: rgb("#18181b"),
    heading: rgb("#09090b"),
    muted: rgb("#71717a"),
    accent: rgb("#0284c7"),
    card-bg: rgb("#f4f4f5"),
    border: rgb("#e4e4e7"),
    code-bg: rgb("#f8fafc"),
    inserted: rgb("#15803d"),
    highlight: rgb("#fef08a"),
  ),
)

#let fonts = (
  sans: ("Inter", "Liberation Sans", "FreeSans"),
  display: ("Inter Display", "Inter"),
  mono: ("Iosevka NF", "Source Code Pro", "Consolas"),
)

// In Markdown presentations, horizontal rules (---) create slide breaks
#let horizontalrule = pagebreak(weak: true)

#let slides(
  md-path: none,
  title: "Folio Presentation",
  subtitle: none,
  author: "Juan José Martínez Guerrero",
  dependency: "TUDelft Systems & Control",
  date: none,
  theme: "dark",
  doc,
) = {
  // ==========================================
  // READ FRONTMATTER
  // ==========================================
  let fm = (:)
  if md-path != none {
    let text = read(md-path)
    let m = text.match(regex("^---\\s*\\n([\\s\\S]*?)\\n---\\s*\\n"))
    if m != none {
      let yaml-text = m.captures.at(0)
      for line in yaml-text.split("\n") {
        let trimmed = line.trim()
        if trimmed != "" and trimmed.contains(":") {
          let parts = trimmed.split(":")
          let key = parts.first().trim()
          let val = parts.slice(1).join(":").trim().trim("\"").trim("\x27")
          fm.insert(key, val)
        }
      }
    }
  }

  let final-title = fm.at("title", default: title)
  let final-subtitle = fm.at("subtitle", default: subtitle)
  let final-author = fm.at("author", default: author)
  let final-dep = fm.at("dependency", default: dependency)
  let final-date = fm.at("date", default: date)
  let chosen-theme-name = fm.at("theme", default: theme)
  let t = themes.at(chosen-theme-name, default: themes.dark)

  // ==========================================
  // PAGE SETUP (16:9 Aspect Ratio)
  // ==========================================
  set page(
    paper: "presentation-16-9",
    fill: t.bg,
    margin: (
      top: 2.2cm,
      bottom: 1.6cm,
      x: 2.4cm,
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
            #if final-title != none [ • #final-title]
          ],
          align(right)[#cur / #tot],
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
    leading: 0.75em,
    spacing: 1.3em,
  )

  // ==========================================
  // SLIDE HEADINGS
  // ==========================================
  show heading.where(level: 1): it => {
    pagebreak(weak: true)
    v(0.2em)
    block(
      width: 100%,
      below: 1.2em,
      [
        #text(
          size: 26pt,
          weight: "bold",
          fill: t.heading,
          tracking: -0.02em,
        )[#it.body]
        #v(0.3em)
        #line(length: 100%, stroke: 1.5pt + t.accent)
      ],
    )
  }

  show heading.where(level: 2): it => block(
    above: 1.1em,
    below: 0.7em,
    text(
      size: 19pt,
      weight: "bold",
      fill: t.accent,
      tracking: -0.01em,
      it.body,
    ),
  )

  show heading.where(level: 3): it => block(
    above: 0.9em,
    below: 0.5em,
    text(
      size: 16pt,
      weight: "semibold",
      fill: t.muted,
      it.body,
    ),
  )

  // Lists
  set list(
    spacing: 1.1em,
    marker: [•],
  )
  set enum(
    spacing: 1.1em,
  )

  // Links
  show link: it => text(
    fill: t.accent,
    underline(offset: 2pt, it),
  )

  // Code Blocks
  show raw.where(block: true): it => block(
    fill: t.code-bg,
    inset: 14pt,
    radius: 6pt,
    width: 100%,
    stroke: 0.5pt + t.border,
    outset: 0pt,
    [
      #set text(
        font: fonts.mono,
        size: 13pt,
      )
      #it
    ],
  )

  // Inline Code
  show raw.where(block: false): it => box(
    fill: t.card-bg,
    inset: (x: 5pt, y: 2pt),
    radius: 4pt,
    stroke: 0.3pt + t.border,
    text(
      font: fonts.mono,
      size: 14pt,
      fill: t.accent,
      it,
    ),
  )

  // Blockquotes & Callouts
  show quote.where(block: true): it => block(
    fill: t.card-bg,
    inset: (x: 16pt, y: 12pt),
    radius: 6pt,
    stroke: (left: 3pt + t.accent),
    width: 100%,
    it.body,
  )

  // Math equations
  show math.equation.where(block: true): it => block(
    width: 100%,
    inset: (y: 8pt),
    align(center, text(size: 20pt, it)),
  )

  // ==========================================
  // TITLE SLIDE HERO (Slide 1)
  // ==========================================
  align(center + horizon)[
    #text(
      size: 11pt,
      weight: "bold",
      tracking: 0.25em,
      fill: t.accent,
    )[FOLIO PRESENTATION]

    #v(1.2em)

    #text(
      size: 34pt,
      weight: "bold",
      fill: t.heading,
      tracking: -0.03em,
    )[#final-title]

    #if final-subtitle != none [
      #v(0.8em)
      #text(
        size: 18pt,
        fill: t.muted,
      )[#final-subtitle]
    ]

    #v(2.5em)

    #if final-author != none [
      #text(
        size: 16pt,
        weight: "medium",
        fill: t.text,
      )[#final-author]
    ]

    #if final-dep != none [
      #v(0.3em)
      #text(
        size: 13pt,
        fill: t.muted,
      )[#final-dep]
    ]

    #if final-date != none [
      #v(0.3em)
      #text(
        size: 11pt,
        fill: t.muted,
      )[#final-date]
    ]
  ]

  doc
}
