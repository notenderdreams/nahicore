---
name: brain-dump
description: Researches a codebase topic or synthesizes chat insights into an exhaustive deep-dive markdown note (with LaTeX math, ASCII/Mermaid visuals, and code references), then deposits it into the project's Obsidian Vault or a local .dead-brain/ directory while maintaining an Index.md table.
---

# Brain Dump (`/brain-dump`)

> Transform transient coding insights, mathematical derivations, and architecture explanations into permanent, high-fidelity project knowledge.

**Brain Dump** bridges active development and your Second Brain. Whenever you need to understand or document a complex subsystem, algorithm, physics equation, or architectural pattern, Brain Dump reads the code, derives the math, diagrams the concepts, writes a polished note directly into your project's Obsidian vault (or local `.dead-brain/` directory), and indexes it in `Index.md`.

---

## Invocation Modes

Brain Dump can be triggered in three ways:

### 1. One-Shot Research Mode
Directly research a concept from the codebase and publish the note:
```
/brain-dump explain what is refract in vec3
/brain-dump how does BVH traversal work in Rtweekend
```
*Action*: Reads the source files, derives the theory, generates the complete note, appends to `Index.md`, and prints a concise chat summary.

### 2. Post-Chat Extraction Mode
Synthesize an ongoing chat discussion or debugging session into a note:
```
/brain-dump
```
*Action*: Scans the conversation transcript, distills the explanations and conclusions, formats the note, deposits it in the project vault, and updates `Index.md`.

### 3. In-Project Local Mode (`.dead-brain/`)
Drop notes directly inside the repository without touching Obsidian:
```
/brain-dump in-project
/brain-dump --local explain the ray-triangle intersection math
```
*Action*: Dumps to `./.dead-brain/`, automatically adds `.dead-brain/` to `.gitignore`, uses standard markdown links, and maintains `./.dead-brain/Index.md`.

---

## Vault & Path Resolution

Use the bundled resolver from the active project directory:

```bash
bash <skill-dir>/scripts/resolve_target.sh [PROJECT_NAME]
bash <skill-dir>/scripts/resolve_target.sh --local [PROJECT_NAME]
```

`PROJECT_NAME` defaults to the current directory name. Read the printed
`TARGET_DIR` and `INDEX_FILE` as data; do not execute or source the output.

- **Local mode** creates `.dead-brain/` in the current directory and adds it to
  `.gitignore`, creating the ignore file when necessary.
- **Vault mode** reads `~/.config/nahicore/brain-dump/vault.conf` and stores project
  mappings in `projects.map` beside it. `XDG_CONFIG_HOME` changes the config root;
  `NAHICORE_CONFIG_DIR` overrides the `nahicore` directory itself.
- For first-time vault setup, copy [vault.conf.example](vault.conf.example) to
  the config directory and set `VAULT_PATH` to the user's vault. Optionally copy
  [projects.map.example](projects.map.example). Ask for the vault location only
  when it is needed and unavailable from existing configuration.
- Configuration values are literal text; shell expressions are never executed.
  `NAHICORE_VAULT_PATH` may override the configured vault path.
- Mappings use exact project-name matches and paths relative to the vault.
  New projects default to `DEFAULT_PROJECTS_DIR/PROJECT_NAME`. Destinations that
  escape the vault are rejected. An optional second positional argument selects
  a relative destination and saves that mapping.
- Private legacy `vault.conf` and `projects.map` files inside the skill remain
  readable for existing users. New mappings go to the user config directory.
  Private files are excluded from copy installations and release archives.

Resolve and verify the destination before writing. Existing notes and index rows
must be updated deliberately; do not overwrite unrelated content.

---

## Note Formatting Standards

### 1. File Naming
* Use **Obsidian default Title Case With Spaces**:
  * ✅ `Refraction and Snell's Law.md`
  * ✅ `Möller–Trumbore Triangle Intersection.md`
  * ✅ `BVH Spatial Partitioning.md`
  * ❌ `REFRACTION_AND_SNELLS_LAW.md` (avoid all-caps snake case unless naming a literal code constant/macro)

### 2. Frontmatter Template
Every note must begin with clean YAML frontmatter:
```yaml
---
date: YYYY-MM-DD
project: <ProjectName>
tags:
  - <domain, e.g. raytracing>
  - <math/physics/architecture>
  - <language, e.g. rust>
type: deep-dive
status: evergreen
---
```

### 3. Dual Visuals (ASCII + Mermaid)
Choose visuals that explain the topic; include both forms only when each adds useful information:
* **ASCII Diagram**: For spatial geometry, ray bounces, coordinate vectors, and memory layouts.
* **Mermaid Diagram**: For pipelines, state machines, call sequences, and class structures.

### 4. Mathematical Rigor (Obsidian MathJax)
* Use inline `$ \eta \sin\theta = \eta' \sin\theta' $` for short equations.
* Use display math blocks for derivations and formulas:
  ```markdown
  $$
  \mathbf{R}' = \mathbf{R}'_{\parallel} \mathbf{n} + \mathbf{R}'_{\perp}
  $$
  ```

### 5. Document Structure Checklist
Adapt the note to the topic; use these sections when applicable:
1. **The Goal & Physical Intuition**: High-level motivation, physical or system behavior, why this technique exists.
2. **Mathematical & Formal Foundations**: Underlying laws, formulas, and definitions.
3. **Spatial / Architectural Diagrams**: ASCII and/or Mermaid as appropriate.
4. **Step-by-Step Derivation**: Breaking down equations into executable components.
5. **Code Walkthrough with Exact References**: Direct mapping of the math/architecture to the codebase (with `filename:line-range`).
6. **Edge Cases, Pitfalls & Stability**: Floating-point precision, total internal reflection, division-by-zero guards, epsilons.
7. **Quick Memory Cheat Sheet**: Markdown table summarizing formulas, variable names, and code equivalents.

---

## Live `Index.md` Catalog Maintenance

Every project folder (`<TARGET_DIR>`) must maintain an up-to-date `Index.md` table cataloging every note.

### Index Format

If `Index.md` does not exist in `TARGET_DIR`, initialize it:

```markdown
# 🫧 <ProjectName> Knowledge Base

| Note | Topic & Core Concept | Added |
| :--- | :--- | :--- |
```

### Appending Entries:
* **Vault Mode (Wikilinks)**:
  ```markdown
  | [[Refraction and Snell's Law]] | Snell's law vector formulation, perpendicular/parallel ray decomposition, and Rust dielectric scattering implementation. | 2026-09-28 |
  ```
* **Local Mode (Markdown Links)**:
  ```markdown
  | [Refraction and Snell's Law](./Refraction%20and%20Snell's%20Law.md) | Snell's law vector formulation, perpendicular/parallel ray decomposition, and Rust dielectric scattering implementation. | 2026-09-28 |
  ```

If the entry already exists in `Index.md`, verify that the description is accurate; do not duplicate rows.

---

## Example Workflow

### User Prompt:
```
/brain-dump explain what is refract in vec3
```

### Agent Actions:
1. **Locate & Read Code**:
   Inspects `src/vec3.rs` and `src/material.rs` in `Rtweekend`.
2. **Resolve Target**:
   Runs `resolve_target.sh Rtweekend` -> resolves `<vault>/Projects/Rtweekend`.
3. **Draft Deep-Dive Note**:
   Creates `Refraction and Snell's Law.md` with frontmatter, Snell's law derivation, ASCII ray-normal diagram, Mermaid scatter pipeline, code walkthrough, and cheat sheet.
4. **Update `Index.md`**:
   Appends `| [[Refraction and Snell's Law]] | Snell's law vector formulation... | 2026-09-28 |` to `Index.md`.
5. **Chat Response**:
   Outputs a concise summary of the concept and confirms the created note location.
