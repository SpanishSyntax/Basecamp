// ========================================================
// FOLIO IEEE ACADEMIC PAPER TEMPLATE
// Turnkey 2-Column Camera-Ready Format for Typst
// ========================================================

#let fonts = (
  serif: ("Times New Roman", "Libertinus Serif", "Liberation Serif", "FreeSerif", "Nimbus Roman"),
  sans: ("Inter", "Liberation Sans", "Helvetica", "Arial"),
  mono: ("Iosevka NF", "Source Code Pro", "Courier New", "Consolas"),
)

#let horizontalrule = line(length: 100%, stroke: 0.5pt + rgb("#a1a1aa"))

#let paper(
  md-path: none,
  title: "Untitled IEEE Paper",
  author: "First Author, Member, IEEE, and Second Author",
  dependency: "Department of Systems & Control, Delft University of Technology",
  email: none,
  abstract: none,
  keywords: none,
  date: none,
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
  let final-author = fm.at("author", default: author)
  let final-dep = fm.at("dependency", default: dependency)
  let final-email = fm.at("email", default: email)
  let final-abstract = fm.at("abstract", default: abstract)
  let final-keywords = fm.at("keywords", default: keywords)
  let paper-size = fm.at("paper", default: "us-letter")

  // ==========================================
  // PAGE SETUP (IEEE Standard Dimensions)
  // ==========================================
  set page(
    paper: paper-size,
    margin: (
      top: 0.75in,
      bottom: 1.0in,
      left: 0.625in,
      right: 0.625in,
    ),
    footer: context {
      set text(font: fonts.serif, size: 9pt)
      align(center)[#counter(page).display("1")]
    },
  )

  // ==========================================
  // TYPOGRAPHY (IEEE Standard 10pt Serif)
  // ==========================================
  set text(
    font: fonts.serif,
    size: 10pt,
    lang: "en",
  )

  set par(
    justify: true,
    leading: 0.55em,
    spacing: 0.8em,
    first-line-indent: 1.25em,
  )

  // ==========================================
  // IEEE SECTION NUMBERING
  // ==========================================
  set heading(numbering: (..nums) => {
    let level = nums.pos().len()
    if level == 1 {
      numbering("I.", ..nums)
    } else if level == 2 {
      numbering("A.", ..nums.pos().slice(1))
    } else if level == 3 {
      numbering("1)", ..nums.pos().slice(2))
    } else {
      numbering("a)", ..nums.pos().slice(3))
    }
  })

  show heading.where(level: 1): it => block(
    above: 1.6em,
    below: 0.8em,
    width: 100%,
    align(center)[
      #text(
        size: 10pt,
        weight: "bold",
        smallcaps(it),
      )
    ],
  )

  show heading.where(level: 2): it => block(
    above: 1.2em,
    below: 0.6em,
    text(
      size: 10pt,
      weight: "bold",
      style: "italic",
      it,
    ),
  )

  show heading.where(level: 3): it => block(
    above: 1.0em,
    below: 0.5em,
    text(
      size: 10pt,
      style: "italic",
      it,
    ),
  )

  // ==========================================
  // CODE & LIST FORMATTING
  // ==========================================
  show raw.where(block: true): it => block(
    fill: rgb("#f4f4f5"),
    inset: 8pt,
    radius: 3pt,
    width: 100%,
    stroke: 0.3pt + rgb("#d4d4d8"),
    [
      #set text(font: fonts.mono, size: 8pt)
      #it
    ],
  )

  show raw.where(block: false): it => box(
    fill: rgb("#f4f4f5"),
    inset: (x: 3pt, y: 1pt),
    radius: 2pt,
    text(font: fonts.mono, size: 8.5pt, it),
  )

  set list(spacing: 0.6em, marker: [•])
  set enum(spacing: 0.6em)

  // ==========================================
  // TITLE & AUTHORS BLOCK (Full Width Span)
  // ==========================================
  align(center)[
    #v(0.5em)
    #text(
      size: 22pt,
      weight: "bold",
      tracking: -0.01em,
    )[#final-title]

    #v(1.2em)

    #if final-author != none [
      #text(
        size: 11pt,
        weight: "medium",
      )[#final-author]
    ]

    #if final-dep != none [
      #v(0.3em)
      #text(
        size: 9.5pt,
        style: "italic",
      )[#final-dep]
    ]

    #if final-email != none [
      #v(0.2em)
      #text(
        size: 9pt,
        font: fonts.mono,
      )[#final-email]
    ]
  ]

  v(1.5em)

  // ==========================================
  // ABSTRACT & INDEX TERMS (Full Width)
  // ==========================================
  if final-abstract != none {
    block(
      width: 100%,
      inset: (x: 1.8em),
      [
        #set par(justify: true, first-line-indent: 0pt, leading: 0.55em)
        #text(size: 9pt)[
          #text(weight: "bold", style: "italic")[Abstract—]#final-abstract
        ]

        #if final-keywords != none [
          #v(0.5em)
          #text(size: 9pt)[
            #text(weight: "bold", style: "italic")[Index Terms—]#final-keywords
          ]
        ]
      ],
    )
    v(1.2em)
  }

  // ==========================================
  // TWO-COLUMN DOCUMENT BODY
  // ==========================================
  columns(2, gutter: 0.25in)[#doc]
}
