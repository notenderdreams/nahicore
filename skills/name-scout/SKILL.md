---
name: name-scout
description: Generate distinctive names from a project's actual context, then investigate exact and nearby collisions across package registries (npm, PyPI, Crates.io), GitHub, domains (RDAP .com/.net/.io), Steam, and Wikipedia. Use for naming or renaming software, libraries, games, products, CLIs, and open-source projects; verifies whether names are clear or taken.
---

# Name Scout (`/name-scout`)

> Context-driven naming generation and automated multi-registry namespace collision checks.

Find a distinctive name with a defensible product story and an evidence-backed collision report. Treat “not found” as a search result, never as proof of ownership or legal clearance.

---

## Workflow

### 1. Build the naming brief

Inspect the project before inventing names. Read the highest-signal local material: README and product docs, package manifests, directory structure, user-facing copy, and the main entry points. Extract:

- **What the project does**: core value prop, target audience, key differentiators;
- **Naming constraints**: desired tone, pronunciation, language, length, prefix/suffix;
- **Target ecosystems**: where the name must be published (npm, PyPI, crates, Homebrew, domains, etc.);
- **Native vocabulary**: concepts, metaphors, or terminology already central to the codebase.

If the repository does not reveal an essential product fact, ask one focused question. Otherwise state the inferred brief and proceed.

---

### 2. Generate and shape candidate territories

Create several distinct naming territories before drafting individual names:
- **Functional / Descriptive**: directly communicates utility (clean, transparent)
- **Metaphorical**: evokes a vivid image, action, or physical dynamic
- **Invented / Neologisms**: fresh coinages, portmanteaus, distinctive root merges
- **Domain-Native**: borrows language from math, physics, biology, mechanics, etc.

Generate broadly, then prune ruthlessly:
- Reject candidates with pronunciation ambiguity, awkward spelling, or negative connotations.
- Eliminate generic keyword soup or misleading promises.
- Avoid normalized package spellings that collide with existing prominent projects.
- Ensure every finalist has a concise, defensible product rationale.

Filter locally down to a strong shortlist of roughly **6–12 candidates** before performing live network queries.

---

### 3. Check availability & collision status

Run the bundled standard-library checker from the skill directory:

```bash
# Single candidate: prints availability list with target, status, and detail
python3 scripts/check_names.py "Candidate Name"

# Multiple candidates: prints comparative matrix (names in rows, registries/domains in columns)
python3 scripts/check_names.py "Candidate One" "Candidate Two" candidate-three
```
*(Or via absolute path `python3 <path-to-skill>/scripts/check_names.py "Candidate"`).*

#### Output Modes:
- **Single name**: Prints a clean vertical list of every target registry/domain, its availability status, and specific detail.
- **Multiple names**: Prints a compact comparison matrix where rows are candidate names and columns are registries/domains, followed by a concise collisions summary for any `TAKEN` or `RELATED` hits.
- **Options**:
  - `--json`: machine-readable output for programmatic parsing
  - `--detail`: show detailed multi-row output table instead of the matrix
  - `--matrix`: force matrix display even when checking a single candidate
  - `--checks npm pypi domains`: limit execution to specific target registries
  - `GITHUB_TOKEN`: optional environment variable to increase GitHub API rate limits

#### What the checker inspects:
| Target | What is Queried |
| :--- | :--- |
| **npm** | Exact package availability via npmjs registry |
| **PyPI** | Python package index registrations |
| **crates.io** | Rust crate registry (checks hyphen and underscore variants) |
| **GitHub** | Repository search for exact name matches and related star counts |
| **Domains (RDAP)** | Authoritative RDAP registration lookups for `.com`, `.net`, and `.io` |
| **Steam** | Store search for exact or nearby video game titles |
| **Wikipedia** | Exact article title collisions and disambiguation pages |

Options:
- `--json`: machine-readable output for programmatic parsing
- `--checks npm pypi github`: limit execution to specific target registries
- `GITHUB_TOKEN`: optional environment variable to increase GitHub API rate limits

#### Manual Reconnaissance:
Supplement the automated checks with focused web searches for top finalists:
- Search quoted name `"<name>"` + category (e.g. `"<name>" cli tool`).
- Check any domain-specific registries not in the default suite (e.g., Docker Hub, RubyGems, Maven, App Store).

---

### 4. Rank, score, and deliver report

Score finalists across four distinct dimensions:
1. **Product Fit & Evocativeness**: Does the name reinforce the product's identity and story?
2. **Distinctiveness & Searchability**: Will it dominate search results, or disappear into common words?
3. **Collision Risk**: Are there similar, confusingly close, or famous projects in adjacent spaces?
4. **Namespace Availability**: Is it clean across required package registries, GitHub, and domains?

Present a structured report containing:
- Inferred naming brief
- Top candidate names with rationales
- Compact evidence table with checker statuses:
  - `CLEAR`: No exact collision detected at check time
  - `TAKEN`: Exact match or registered domain found
  - `RELATED`: Nearby or similar names exist—review required
  - `UNKNOWN`: Registry lookup could not be completed reliably
- Unambiguous recommendation with tradeoffs
- Clear disclaimer: *Evidence-based reconnaissance only; recommend trademark review before committing financial or brand resources.*
