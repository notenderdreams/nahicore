---
name: notex
description: Create complete, well-organized LaTeX study notes from slides or PDFs, including worked exercises and diagrams, with optional TeXifier compatibility on request. Use when the user wants educational notes from lecture slides, a PDF, or course material, or needs a LaTeX notes document created or repaired.
---

# Notex

Produce a standalone LaTeX study-notes document. By default, deliver the complete `.tex` source without compiling it. An explicit request to compile overrides that default.

## Document setup

- Use standard LaTeX commands and a small set of widely supported packages. A useful baseline is `article`, `geometry`, `amsmath`, `amssymb`, and `xcolor`. Add `booktabs`, `tabularx`, `longtable`, `enumitem`, `graphicx`, `tikz`, and `hyperref` only as needed.
- Keep the document self-contained: no shell escape, custom fonts, or external bibliography processors. Do not load `microtype`.
- Prefer a simpler construction over an exotic package when it satisfies the task.

## Optional: TeXifier compatibility

Apply this section only when the user asks for TeXifier compatibility (or reports a TexpadTeX error). Otherwise ignore it.

- Target TeXifier's built-in TexpadTeX typesetter with default settings.
- Do not load `microtype`; TeXifier documents that it needs engine extensions TexpadTeX lacks. Do not assume a common pdfLaTeX package works without checking.
- Avoid pdfLaTeX/XeLaTeX/LuaLaTeX requirements, shell escape, custom fonts, and external bibliography processors. Do not insert engine-selection directives or tell the user to switch compilers.
- Package availability is not proof of support for every option. When unsure, check the official docs below and prefer a simpler supported construction.
- When repairing a TexpadTeX error, inspect the source and any error log, check the docs, and fix the actual source.
- Describe the file as prepared for TexpadTeX, not as verified, unless it was compiled.
- Docs: [package coverage](https://www.texifier.com/docs/tutorials/tex/typesetters/texpadtex/package-coverage), [package options](https://www.texifier.com/docs/tutorials/tex/typesetters/texpadtex/package-options).

## Notes from slides or PDFs

Treat the notes as a **complete study replacement for the supplied slides**, unless the user explicitly requests a summary or a narrower scope. Restructure the content for studying; do not summarize it or impose a page limit.

### Coverage and order

- Read every supplied slide or page, including diagrams, captions, footnotes, tables, and image-only content that text extraction misses. If content is unreadable or unavailable, identify the affected slides and the gap instead of guessing or claiming complete coverage.
- Preserve every substantive point, definition, qualification, number, formula, assumption, unit, example, quotation, and reference. Keep exact wording for quotations; preserve technical meaning and detail when rewriting other text.
- Follow slide order. Merge consecutive slides that continue the same topic under one heading, using clean sections, subsections, lists, and tables. Keep later revisits in their original position with cross-references when useful.
- Consolidate exact duplicates and repeated roadmaps only when no information is lost. Preserve any new detail, changed value, or differing wording that changes the meaning. A roadmap mentioning an absent topic is not permission to invent that topic.
- Explain the relationships actually shown in diagrams and charts, retaining labels, directions, values, legends, and conditions.
- Diagrams: first try to recreate each diagram in LaTeX (TikZ, `tabular`, or `array`), keeping every label, arrow, value, and legend. If it cannot be reproduced faithfully, crop the diagram from the slide and include it with `\includegraphics`, with a caption naming its source slide. Supply the image files alongside the `.tex` source.
- Turn each meme or cartoon slide into one line stating its instructional point. Preserve any substantive facts or labels it also contains; mark an uncertain interpretation as such.
- Include the source's complete references list and retain inline attributions, URLs, and citation details as supplied. Mark incomplete citations rather than inventing bibliographic details.

### Source fidelity and derived work

- Keep the notes grounded in the supplied material. Do not add outside facts, examples, references, or unrequested enrichment. Use connected prose to unpack what the source states without silently extending its claims.
- Label any necessary inference, added calculation, or answer absent from the slides clearly as **Derived explanation** or **Derived solution** at the point of use. State the reasoning and any additional assumptions; a derived result is not a source-provided claim.
- Preserve both versions of contradictory claims, values, or inconsistent numbering, with their slide locations and a brief **Source discrepancy** note. Keep original item numbers where needed to make the mismatch visible.
- For a demonstrable error, retain the source statement and give a separately labeled **Correction (derived)** with its reasoning. If the evidence is insufficient, describe the uncertainty rather than choosing a version silently. Preserve original units alongside any derived conversion or correction.

### Quizzes and exercises

- Include every quiz and exercise in its original position, retaining the full prompt, answer choices, data, constraints, and supplied answer or explanation.
- Provide a worked solution with the intermediate reasoning, formulas, substitutions, units, and final answer as applicable. Clearly distinguish source-provided solution steps from derived additions. For conceptual questions, explain why the answer follows; discuss alternatives when needed to resolve the question.
- If a question is ambiguous or lacks necessary information, state what is missing. Give a conditional solution only with explicit assumptions, and never present a guessed answer as settled. Flag conflicts with a supplied answer using the discrepancy rules above.

### Study layout and coverage check

Keep styling minimal: readable margins, conventional headings, and restrained color for key terms and discrepancy notes. Use tables for comparisons and lists for parallel points without dropping qualifications. Give every figure a caption and a source slide reference.

Record source slide or page ranges beside headings or in a compact coverage guide. Before delivery, compare the notes against every source page: each must map to a notes location, an identified duplicate, a one-line meme interpretation, or an explicit unreadable-content gap. Check exercises and references separately so they are not omitted. Use as many pages as the full content requires.

## Verification and delivery

Review the complete source for balanced braces and environments, escaped special characters, defined commands, consistent math units, table structure, missing packages, and that every included image file exists at the referenced path. Under the default, do not compile; perform source checks only.

When repairing a compile error, inspect the document and any available error log, then fix the actual source. Ask for the error text only if needed after examining available evidence.

Deliver a clickable link to the `.tex` file (and any image files). State whether it was compiled. Source checks do not establish successful compilation; do not claim it without evidence.
