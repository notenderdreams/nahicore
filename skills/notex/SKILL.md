---
name: notex
description: Create or repair standalone LaTeX documents for TeXifier's built-in TexpadTeX compiler. Use when the user requests TeXifier-compatible documents, complete study notes from slides or PDFs for TeXifier, or reports a TexpadTeX compatibility error.
---

# Notex

Target **TeXifier's built-in TexpadTeX typesetter with default settings**. The user's default preference is to receive a complete `.tex` source without compiling it. An explicit request to compile overrides that preference.

## Compiler compatibility

- Produce a standalone document using standard LaTeX commands and a small set of supported packages. Keep the built-in fonts and encoding unless the task needs something else.
- Do not load `microtype`: TeXifier documents that it depends on engine extensions unavailable in TexpadTeX. Do not assume that a package works merely because it is common in pdfLaTeX documents.
- Avoid requirements for an external TeX installation, pdfLaTeX, XeLaTeX, LuaLaTeX, shell escape, custom fonts, or external bibliography processors. Do not insert engine-selection directives or tell the user to switch away from the built-in compiler.
- A useful baseline is `article`, `geometry`, `amsmath`, `amssymb`, and `xcolor`. Add packages such as `booktabs`, `tabularx`, `longtable`, `enumitem`, and `hyperref` only as needed. Package availability is not proof of support for every package option.
- For a package or engine feature whose support is uncertain, consult the official compatibility documentation linked below. Prefer a simpler supported construction when it satisfies the task.

## Notes from slides or PDFs

Treat the notes as a **complete study replacement for the supplied slides**, unless the user explicitly requests a summary or a narrower scope. Restructure the content for studying; do not summarize it or impose a page limit.

### Coverage and order

- Read every supplied slide or page, including diagrams, captions, footnotes, tables, and image-only content that text extraction misses. If content is unreadable or unavailable, identify the affected slides and the gap instead of guessing or claiming complete coverage.
- Preserve every substantive point, definition, qualification, number, formula, assumption, unit, example, quotation, and reference. Keep exact wording for quotations; preserve technical meaning and detail when rewriting other text.
- Follow slide order. Merge consecutive slides that continue the same topic under one heading, using clean sections, subsections, lists, and tables. Keep later revisits in their original position with cross-references when useful.
- Consolidate exact duplicates and repeated roadmaps only when no information is lost. Preserve any new detail, changed value, or differing wording that changes the meaning. A roadmap mentioning an absent topic is not permission to invent that topic.
- Explain the relationships actually shown in diagrams and charts, retaining labels, directions, values, legends, and conditions. Reproduce or include the figure when prose alone would lose information.
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

Keep styling minimal: readable margins, conventional headings, and restrained color for key terms and discrepancy notes. Use tables for comparisons and lists for parallel points without dropping qualifications. Keep figures self-contained when practical; supply any required assets alongside the source.

Record source slide or page ranges beside headings or in a compact coverage guide. Before delivery, compare the notes against every source page: each must map to a notes location, an identified duplicate, a one-line meme interpretation, or an explicit unreadable-content gap. Check exercises and references separately so they are not omitted. Use as many pages as the full content requires.

## Verification and delivery

Review the complete source for balanced braces and environments, escaped special characters, defined commands, consistent math units, table structure, and missing dependencies. Under the default no-compilation preference, perform source checks only: do not invoke a TeX engine, rendering preview, or any command that triggers compilation.

When repairing a compatibility error, inspect the document and any available error log, check official documentation, and modify the actual source. Ask for the error text only if needed after examining available evidence.

Deliver a clickable link to the `.tex` file. State whether it was compiled. Source checks do not establish successful compilation; describe the file as prepared for TexpadTeX rather than claiming verified compilation without evidence.

## Official references

- [TexpadTeX package coverage](https://www.texifier.com/docs/tutorials/tex/typesetters/texpadtex/package-coverage): check package restrictions and known unsupported features.
- [TexpadTeX package options](https://www.texifier.com/docs/tutorials/tex/typesetters/texpadtex/package-options): consult when an option may select an incompatible driver.
