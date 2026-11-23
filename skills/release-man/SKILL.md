---
name: release-man
description: Interview the user, then build or repair a repo's release pipeline (cargo-dist, GoReleaser, release-plz, release-please, changesets, semantic-release, PyPI trusted publishing, tauri-action, Docker, Homebrew taps). Use when adding releases, CI publishing, versioning, changelogs, or binary distribution to a repo with no release setup or an existing one.
---

# Release Man (`/release-man`)

> Grill first, generate second. Detect what the repo already tells you, ask only what it can't, then build a verified pipeline.

Works for repos with **no** release setup (greenfield) and repos with an **existing** one (audit, fix, migrate). Never overwrite existing release config before the user has chosen keep / fix / replace.

---

## Workflow

### 1. Recon (no questions yet)

Inspect before asking. Collect:

- **Language & build**: `Cargo.toml`, `go.mod`, `package.json`, `pyproject.toml`, `tauri.conf.json`, `Dockerfile`, `Makefile`, workspace/monorepo layout.
- **Artifacts**: binaries (bin targets, `main` packages), libraries, containers, desktop apps, static sites.
- **Existing release machinery**: `.github/workflows/*`, `.gitlab-ci.yml`, `dist-workspace.toml`, `.goreleaser.y*ml`, `release-plz.toml`, `.release-please-*`, `.changeset/`, `.releaserc*`, `CHANGELOG.md`, `scripts/release*`.
- **Version state**: version source of truth, `git tag --list | tail`, commit style (conventional commits?), default branch, remote host (`git remote -v`).
- **Auth hints**: existing secrets referenced in workflows, registry names in manifests.

Summarize in ≤8 lines: "Here is what I found." Then grill only on gaps.

### 2. Grill

Rules:

- **One question at a time.** Each carries your **recommended answer** and a one-line why. User can reply "yes" / "default".
- **Skip anything the repo answers.** Confirm inferred facts in the recon summary instead.
- **Follow the branches**: an answer can open or close later questions.
- **Resolve contradictions** (e.g. "no signing" + "notarized macOS DMG") before moving on.
- Stop when the decision tree is closed. Don't ask for ceremony's sake.

Question tree (ask in this order, skipping the irrelevant):

1. **Existing setup** *(only if found)*: keep & fix / migrate to another tool / replace from scratch? What hurts today?
2. **What ships**: binaries, library package, container, desktop installer, docs site?
3. **Platforms (OS × arch × libc)**: linux x86_64/aarch64 × gnu/musl (minimum glibc?), macOS arm64/x86_64 or universal, Windows x86_64/arm64. Native runners or cross-compile? Offer a recommended matrix inferred from the project type, then **echo the final matrix back as a table and get a yes before building**.
4. **Destinations**: GitHub Releases, crates.io, npm, PyPI, GHCR/Docker Hub, Homebrew tap, Scoop, winget, AUR, apt/rpm, installer script (`curl | sh`, PowerShell)?
5. **Trigger model**:
   - *Tag push* (`v1.2.3` → release): simplest.
   - *Release PR* (bot opens version-bump PR; merging releases): release-plz / release-please / changesets.
   - *Manual dispatch* with version input.
6. **Versioning**: semver source (commits vs changesets vs manual), conventional commits enforced?, pre-release channels (`-rc`, `-beta`, nightly)?, tag format (`v1.2.3` vs `pkg-v1.2.3` for monorepos)?
7. **Changelog & notes**: generated from commits/PRs/changesets, or hand-written `CHANGELOG.md`?
8. **Monorepo**: release all together or per package? Dependency-ordered publish?
9. **Trust & integrity**: checksums (always), build provenance attestations (`actions/attest-build-provenance`), cosign/sigstore, SBOM, macOS signing + notarization, Windows code signing?
10. **Credentials**: OIDC trusted publishing where supported (PyPI, crates.io, npm provenance), else which secrets? Who owns the tap repo / tokens?
11. **Gates**: tests/lint required before release? Protected branch or environment approval for publish? Draft release first?
12. **CI host & runners**: GitHub Actions (default) / GitLab / other; self-hosted or paid runners?
13. **Rollback**: how are bad releases yanked/superseded?

After the tree closes, print a one-screen **release plan** (ASCII, no Mermaid): trigger → gate → build matrix → package/sign → GitHub Release → publish destinations, reflecting the user's actual answers. Get a yes, then continue.

### 3. Pick the tool (state the choice + why)

| Situation | Default |
| --- | --- |
| Rust binaries | **cargo-dist** (`dist init`) for build/installers/Homebrew; **release-plz** for version + changelog + crates.io |
| Rust library only | release-plz |
| Go | **GoReleaser** (+ `goreleaser-action`) |
| Node library/CLI | **changesets** (monorepo/manual notes) or **semantic-release** (full automation, conventional commits); npm provenance |
| Python | `uv build` + **PyPI trusted publishing** (`pypa/gh-action-pypi-publish`); maturin for Rust ext; cibuildwheel for native wheels |
| Tauri / Electron | `tauri-apps/tauri-action` / electron-builder |
| Container | `docker/build-push-action` + buildx multi-arch + GHCR |
| Polyglot / monorepo / unsure | **release-please** (manifest mode) + per-language publish jobs |

Prefer the maintained, purpose-built tool over hand-rolled YAML. Hand-roll only when no tool fits; say so.

#### Custom repos (no standard tool fits)

Unusual stack, bespoke build script, mixed toolchains, generated artifacts, or a nonstandard layout: **derive the pipeline from the repo itself** instead of forcing a tool.

1. Find the real build path: `Makefile`/`justfile` targets, `scripts/build*`, `package.json` scripts, existing CI build jobs, README build instructions. Run the build locally to confirm it works and to see what it outputs.
2. Identify the artifacts (file names, paths, per-platform variants) from that output, not from assumptions.
3. Generate a minimal workflow that: runs the repo's own build command per target in a matrix, packages artifacts with stable names (`<name>-<version>-<os>-<arch>.<ext>`), writes `SHA256SUMS`, and attaches them to a GitHub Release (`gh release create` or `softprops/action-gh-release`).
4. Reuse the repo's own scripts and tool versions (read `.tool-versions`, `rust-toolchain.toml`, `.nvmrc`, `go.mod`); don't introduce a new build system.
5. Ask the grill questions only for what the build can't reveal (channels, trigger, signing, secrets).

### 4. Build

- **Run the tool's own generator** when it has one (`dist init`, `goreleaser init`), then edit its output. Don't hand-write generated files (cargo-dist's workflow is regenerated by `dist generate`).
- Workflow hygiene (GitHub Actions):
  - Least-privilege top-level `permissions: {}` / `contents: read`; elevate per job (`contents: write`, `id-token: write`, `attestations: write`).
  - Pin third-party actions to a full commit SHA with a version comment (or at least major tags if the user declines).
  - `concurrency` group so two releases don't race.
  - `fetch-depth: 0` where tags/changelog need history.
  - Publish jobs depend on build + test jobs; publish last, artifacts uploaded once.
  - Use OIDC over long-lived tokens wherever the registry supports it.
- Add alongside: `CHANGELOG.md` seed if missing, release docs (`docs/releasing.md`: how to cut, yank, recover), PR title/commit lint only if conventional commits were chosen.
- **Existing setup**: show a diff-style plan (add / change / remove) and get a yes before touching files. Preserve tag history and version continuity; never retag or rewrite published versions.

### 5. Verify (before claiming done)

Run what's available; report each as passed / failed / skipped:

- Tool dry runs: `dist plan`, `goreleaser release --snapshot --clean`, `goreleaser check`, `release-plz update --dry-run`, `npm pack --dry-run`, `uv build`, `cargo publish --dry-run`.
- Workflow lint: `actionlint`, `zizmor` (if installed).
- Build the host-platform artifact locally when cheap.
- Tag trigger sanity: confirm the tag glob matches the project's tag format.

Never push tags, publish, or trigger a real release without explicit per-action approval. Suggest a throwaway pre-release tag (`v0.0.0-rc.1`) in a fork or after approval for an end-to-end test.

### 6. Hand off

End with a short checklist of **human-only steps**: secrets to add (exact names, where), trusted-publisher registrations (PyPI/crates.io/npm settings page), tap repo creation, environment approvals, branch protection. Then: how to cut the first release (exact commands) and how to yank.

---

## Rules

- Recommend, don't interrogate: every question ships with a default.
- Facts from the repo beat questions; questions beat assumptions on irreversible choices (registries, signing, tag format).
- Tag format and package names on a registry are effectively permanent: confirm them explicitly.
- Secrets are never written to files or logs; reference by name only.
- Keep the output boring and maintainable: smallest config that satisfies the answers.
