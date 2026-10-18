// ========================================================
// FOLIO IEEE ACADEMIC PAPER TEMPLATE
// Powered by @preview/charged-ieee:0.1.4 with Markdown Interop
// ========================================================
#import "@preview/charged-ieee:0.1.4": ieee

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
