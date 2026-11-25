---
name: chop-chop
description: Refactor AI-generated or monolithic code into a modular structure without changing behavior. Splits oversized "god files" into cohesive modules, extracts copy-pasted UI components, hooks, and helpers into one shared definition, and rewires every call site. Plan-only by default; edits only after the user approves the plan. Use when the user says a file is too big, everything is in one file, code is duplicated across places, asks to modularize, split, extract components, clean up AI slop, or "make this a proper project structure".
---

# Chop Chop (`/chop-chop`)

> Move code, don't rewrite it. Same behavior, better boundaries, one definition per thing.

Targets the two classic AI-codegen smells:

1. **God file**: one 800+ line file holding UI, state, API calls, types, utils, constants, and styles.
2. **Copy-paste components**: the same card / button / modal / fetch-and-parse block written 3 times with tiny drift.

Language-agnostic: React/Vue/Svelte, Node, Python, Go, Rust, Swift, etc. Follow the target language's module idioms.

**Two phases, always:**

- **Phase A — Plan (default).** Read-only. Analyze, then print the plan in the exact format below and **stop**. Edit no files, install nothing, create no tests.
- **Phase B — Chop.** Only after the user approves the plan ("go", "yes", "do it", or approves with edits). Approval covers that plan only; if the plan changes materially, show the new plan and ask again.

If the user's original request already says to skip review ("just do it", "no plan"), print the plan anyway, then proceed straight to Phase B.

---

## Phase A: Plan

### A1. Recon

- **Scope**: the file(s) the user named; else find candidates: `find . -type f \( -name '*.ts*' -o -name '*.js*' -o -name '*.py' -o -name '*.go' -o -name '*.rs' -o -name '*.vue' -o -name '*.svelte' \) -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/dist/*' -not -path '*/build/*' | xargs wc -l | sort -rn | head -20`. Plan at most **one god file (plus its duplicates elsewhere) per run**; list other candidates as "next up".
- **Conventions**: existing folder layout (`components/`, `lib/`, `hooks/`, `utils/`, `services/`, package layout), naming case, import style (aliases like `@/`, relative), barrel files or not, test location. **Match them.** Only invent structure where none exists.
- **Safety net**: find the typecheck, lint, test, build, run commands (`package.json` scripts, `Makefile`, `pyproject.toml`, CI workflows). Run them and record the **baseline** (pre-existing failures are noted, not fixed). Then judge coverage of the target file: do existing tests actually exercise it? See A4.
- **Move tooling**: detect what can move code and rewrite imports automatically (see "Move tooling" below). Record which one Phase B will use.
- **Git state**: dirty tree → say so in the plan; recommend committing/stashing first so the refactor is one clean, revertable diff.

### A2. Map the monolith

Build an inventory (in your head or a scratch file outside the repo):

| Region (lines) | What it is | Depends on | Used by | Destination |
| --- | --- | --- | --- | --- |

Classify every top-level symbol into a responsibility:

- **types / interfaces / schemas**
- **constants / config** (magic strings, URLs, enums, theme tokens)
- **pure utils** (formatting, parsing, math, validation)
- **data access** (fetch / DB / API clients, serialization)
- **state & logic** (hooks, stores, reducers, services, classes)
- **UI components** (each visually distinct piece, including inline sub-components and big JSX blocks inside a render)
- **entry / composition** (the page, `main`, route, CLI command that wires it all)

### A3. Hunt duplicates

1. **Tool first**: run `jscpd` (copy/paste detector, 150+ languages) if available or runnable without installing into the project:
   `npx --yes jscpd --min-lines 5 --min-tokens 40 --reporters json --output <scratch-dir> --ignore "**/node_modules/**,**/dist/**,**/build/**,**/.git/**" <src-dir>`
   Read the JSON report from the scratch dir; never write the report into the repo. If `npx`/network is unavailable, say so in the plan and fall back.
2. **Then by hand** (jscpd misses renamed/reshaped copies): grep distinctive class strings, literal URLs, function names, repeated JSX shapes, repeated fetch → parse → set-state / try-catch-toast sequences, re-declared types/constants/helpers (`formatDate` defined in 4 files).
3. **Diff near-duplicates.** Each difference is either **intentional** (becomes a prop/parameter) or **a bug** (one copy missed a fix). Never silently pick one: list each drift point as a question in the plan with a recommended answer.

### A4. Safety net plan

- Tests already cover the target's behavior → use them.
- Coverage is thin or absent → plan **characterization tests**: a few tests that pin down what the code does *today* (rendered output/snapshots for components, return values for utils, request/response shape for data access, stdout for CLIs), using the repo's existing test runner. They assert current behavior, even if it looks wrong.
- A runner built into the toolchain (`node --test`, `go test`, `cargo test`, `unittest`) needs no approval; use it.
- No test runner at all → propose the most standard one for the stack as a **dev-only** addition and mark it as needing approval; or, if the user declines, fall back to typecheck + build + a manual run, and say the net is weak.

### A5. Print the plan and stop

Use exactly this format. Keep it scannable: short lines, no prose paragraphs. Emojis only where shown (title, Found, Safety net, Split, Dedupe, Decisions); never add more.

```
🔪 CHOP-CHOP PLAN · src/pages/Dashboard.tsx (1,412 lines)
Nothing changed yet.

🔍 Found
- 7 jobs in one file: types, API calls, data hook, 6 components, formatters
- 4 duplicate groups, 11 copies total
- Baseline: typecheck ✓  lint ✓  tests ✓ 38/38  build ✓

🕸️ Safety net
- No existing tests cover Dashboard → adding 6 characterization tests first
  (src/pages/__tests__/Dashboard.test.tsx)
- Move tool: ts-morph (imports rewired automatically)

✂️ Split
src/pages/Dashboard.tsx                    1,412 → ~110   composition only
src/components/dashboard/StatCard.tsx      new    ~45
src/components/dashboard/ActivityFeed.tsx  new    ~80
src/hooks/useDashboardData.ts              new    ~60    fetch + loading/error
src/lib/api/dashboard.ts                   new    ~40
src/types/dashboard.ts                     new    ~35

🧩 Dedupe
- StatCard        4 → 1   props: label, value, trend
- Modal           3 → 1   Dashboard, Settings, Profile → src/components/ui/Modal.tsx
- formatCurrency  3 → 1   Dashboard, Billing, utils/money → src/lib/format.ts

🤔 Decisions (my pick first)
1. StatCard copy #3 rounds to 1 decimal, others 2 → keep 2 (looks like a bug) | add `precision` prop
2. Settings Modal closes on Esc, others don't → keep as `closeOnEsc` prop

Stays the same: public imports, dependencies, visuals, behavior.
Uncommitted changes → commit or stash first.
Next up: src/pages/Settings.tsx (940), src/api.ts (610)

Reply "go", answer decisions ("1 prop, 2 ok"), or tell me what to change.
```

A check with no command in the project shows as `none` (e.g. `lint none`), never ✓.

Omit sections and lines that are empty (e.g. no uncommitted-changes line). Then **end your turn**.

---

## Phase B: Chop

### B1. Lay the net

Add the characterization tests from the plan (if any). Run them against the **untouched** code: they must pass before any move. A test that fails now is wrong, not the code; fix the test.

### B2. Extract (small, mechanical steps)

Order: **leaves first**, so every move compiles on its own:

1. types → 2. constants → 3. pure utils → 4. data access → 5. state/hooks/services → 6. leaf components → 7. composite components → 8. slim the original down to composition.

For each step:

- **Move with tooling when available** (see below); otherwise cut and paste **verbatim**. Don't rename, restyle, "improve", or reformat during a move. Behavior changes and moves never share a step.
- Fix imports/exports; delete the original; remove now-unused imports.
- **Dedupe**: create the single shared version, parameterize only the observed differences (per the decisions answered), replace *every* copy including other files, then grep: zero remaining copies.
- Run typecheck/lint and the characterization tests after each meaningful step. Red → fix before the next move.

### B3. Verify

- Rerun the full baseline: typecheck, lint, all tests, build. Anything newly failing is yours.
- Grep for leftovers: old definitions, duplicate blocks, dead imports, orphaned files.
- Check for **circular imports** (`npx --yes madge --circular --extensions ts,tsx <src>` for JS/TS; import the module for Python; the compiler for Go/Rust).
- If the app runs cheaply (dev server, CLI), launch it and exercise the refactored screen/command.
- Report each check as passed / failed / skipped.

### B4. Report

Use this format. Same emoji rule as the plan: only where shown. Omit empty sections. Mark checks ✓ passed, ✗ failed, `skipped`, or `none`.

```
🔪 CHOP-CHOP DONE · src/pages/Dashboard.tsx (1,412 → 108 lines)

✂️ Split
src/components/dashboard/StatCard.tsx      47
src/hooks/useDashboardData.ts              63
...

🧩 Dedupe
- StatCard  4 → 1

🤔 Decisions applied
1. Rounding: kept 2 decimals (copy #3 output changed)

📋 Checks
typecheck ✓  lint ✓  tests ✓ 44/44  build ✓  circular imports ✓  app run skipped

🧪 Tests added
- src/pages/__tests__/Dashboard.test.tsx (6)

Noticed, not fixed: ...
Next up: src/pages/Settings.tsx (940)
```

---

## Move tooling

Prefer tools that move a symbol and rewrite every import over hand edits. Use what the project or editor already has; never add them as project dependencies (run via `npx --yes` / a throwaway venv / the editor LSP).

| Stack | Tool |
| --- | --- |
| TS/JS | LSP "move to file" / rename (TypeScript language server) if available to you; else a short throwaway `ts-morph` script outside the repo |
| Python | `rope` (move module/global, rename) in a throwaway venv; LSP rename (pyright/pylsp) |
| Go | `gopls` rename / move; `gofmt` after |
| Rust | rust-analyzer "move item", rename; `cargo check` after |
| Other | LSP rename where possible; manual verbatim move + grep for every reference |

After any tool run, read the diff: tools sometimes reformat or reorder. Revert incidental churn.

---

## Splitting rules

- **One reason to change per file.** A file mixing fetch logic and rendering is two files.
- **Size is a signal, not the goal.** ~200-300 lines is a smell threshold; cohesion beats line counts. Don't shatter a coherent 400-line module into ten 40-line files.
- **Colocate first, share second.** A component used by one feature lives next to that feature (`components/dashboard/`). Promote to a shared dir (`components/ui/`, `lib/`) only when ≥2 features use it.
- **Extract a shared abstraction only for real duplication** (≥2 actual copies today). No "might reuse later" components, no generic wrappers around one call site.
- **Parameterize differences, don't flag-branch them.** If copies differ in 1-3 values → props/args. If they differ in structure → they're different components; leave them separate or share only the common inner piece.
- **Watch what a move changes silently.** Turning `function` into `const` loses hoisting; aliasing merged duplicates (`export const b = a`) changes `.name` and identity; moving a file changes relative paths and `import.meta.url` / `__file__` lookups. Check for each.
- **Keep the public surface.** Anything exported from the original file stays importable from the same path (re-export) unless the user agrees to update consumers. Same for package entry points, routes, CLI flags.
- **No barrels by default.** Add `index.ts`-style re-export files only if the repo already uses them.
- **Names describe purpose**, not mechanics: `PriceTag`, not `Component2` / `helpers2.ts` / `misc.py`. No `utils.ts` dumping ground: group by domain (`format.ts`, `validation.ts`).
- **Framework constraints win**: Next.js `"use client"` boundaries, server-only modules, Python package `__init__.py`, Go one-package-per-dir, Rust `mod` declarations, Svelte/Vue SFC rules.
- **State stays where it was owned.** Extracting a component doesn't mean lifting or globalizing its state. Don't introduce a store/context the code didn't need.

## Never

- Edit anything in Phase A.
- Change behavior, output, styling, or public APIs as a side effect.
- Fix unrelated bugs mid-refactor. Note them in the report instead (drift bugs are the exception, only per the user's decision).
- Add runtime dependencies, new frameworks, or a DI/container layer. Dev-only test tooling needs explicit approval.
- Leave the build red, or leave both old and new copies in place.
- Rewrite logic "while you're there." If something deserves a rewrite, list it as a follow-up.
