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
