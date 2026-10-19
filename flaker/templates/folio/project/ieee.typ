// ========================================================
// FOLIO IEEE ACADEMIC PAPER TEMPLATE
// Powered by @preview/charged-ieee:0.1.4 with Markdown Interop
// ========================================================
#import "@preview/charged-ieee:0.1.4": ieee

#let horizontalrule = line(length: 100%, stroke: 0.5pt + rgb("#a1a1aa"))

#let paper(
  title: "Untitled IEEE Paper",
  author: "First Author, Member, IEEE, and Second Author",
  dependency: "Department of Systems & Control, Delft University of Technology",
  email: none,
  abstract: none,
  keywords: none,
  paper: "us-letter",
  date: none,
  doc,
  ..sink,
) = {
  let final-title = title
  let final-author = author
  let final-dep = dependency
  let final-email = email
  let final-abstract = abstract
  let final-keywords = keywords
  let paper-size = paper

  let index-terms = ()
  if final-keywords != none {
    index-terms = final-keywords.split(",").map(k => k.trim())
  }

  show: ieee.with(
    title: final-title,
    authors: (
      (
        name: final-author,
        department: final-dep,
        organization: final-dep,
        email: final-email,
      ),
    ),
    abstract: if final-abstract != none [ #final-abstract ] else { [] },
    index-terms: index-terms,
    paper-size: paper-size,
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
