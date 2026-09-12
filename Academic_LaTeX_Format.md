# Standing academic LaTeX format

**Owner:** Miquel Noguer i Alonso.

**Standing instruction, September 12, 2026:** “Use my academic latex format. ALWAYS”. Apply this format to the author's academic papers and their Overleaf projects. Do not substitute a different house style without an explicit later instruction from the author.

## Established settings

- `\documentclass[11pt]{article}` with the class's standard paper-size default.
- `\usepackage[margin=1.08in]{geometry}`.
- Classic serif academic typography; ordinary AMS mathematics and theorem environments.
- `\usepackage{setspace}` and `\setstretch{1.08}`.
- `\setlength{\parindent}{1.25em}` and `\setlength{\parskip}{0pt}`.
- `\captionsetup{font=small,labelfont=bf}`.
- `natbib` and `\bibliographystyle{plainnat}`. Preserve the author-year citation convention used in these papers.
- `\usepackage[hidelinks]{hyperref}`; links remain functional without colored or boxed presentation.
- Title and subtitle through the standard `\title` / `\maketitle` mechanism, with `\\[0.35em]` before the smaller subtitle.
- Author block: `Miquel Noguer i Alonso\\ \small Artificial Intelligence Finance Institute (AIFI)`.
- `\date{\today}`; do not hardcode the date or silently suppress it.
- Keep any requested manuscript DOI as a separate, clickable front-matter identifier.
- Abstract and keywords followed by a clickable table of contents, then the article text. Use `\setcounter{tocdepth}{2}` to include sections and subsections, with appendix and reference entries. Start the contents and the main text on fresh pages.
- No running headers, footers, or page numbers: `\pagestyle{empty}` and `\thispagestyle{empty}` after `\maketitle`.
- Number mathematical statements and sections as needed by the manuscript. Keep cross-references intact.
- Include all figures and complete mathematical/Lean content in the source package.
- Do not cite the author's draft papers or add excessive self-citations.

## Basis

The layout and author block follow the author's established July 26, 2026 article source, *Conditional Short-Put-Spread Returns under Rich Implied--Realized Volatility Spreads*. The absence of headers, footers, and page numbers follows the explicit July 24, 2026 academic-classic-format preference. Current instructions require `plainnat`, `\today`, and no draft self-citations. This file records formatting instructions; it is not a scholarly citation to the earlier manuscript.

The subsequent September 12, 2026 instruction, “use table of contents”, supersedes the earlier omission of a contents page. Include the contents in this standing academic format.
