# nahicore

A collection of reusable agent skills for studying, documenting code, naming
projects, and scratch tooling. Each skill is a self-contained folder with
instructions, optional helpers, and Codex UI metadata. Licensed under MIT.

## Skills

| Skill | Purpose | Requirements |
| --- | --- | --- |
| [Notex](skills/notex/SKILL.md) | Turn slides and PDFs into complete study notes in TeXifier-compatible LaTeX, with worked exercises and source coverage. | An agent able to read the source documents; TeXifier to typeset the output. |
| [Brain Dump](skills/brain-dump/SKILL.md) | Save detailed codebase explanations to Obsidian or a local `.dead-brain/` folder and maintain an index. | Python 3.10+ and Bash; an Obsidian vault is optional. |
| [Name Scout](skills/name-scout/SKILL.md) | Generate context-driven project names and check registry, domain, and public-name collisions. | Python 3.10+; network access for live lookups. |
| [Liquid Metal](skills/liquid-metal/SKILL.md) | Reuse one persistent script outside the repository for dynamic scratch tooling during a session. | A runtime appropriate to the task. |

## Install

### Claude Code (plugin)

This repository is a Claude Code plugin and its own marketplace. In Claude Code:

```text
/plugin marketplace add notenderdreams/nahicore
/plugin install nahicore@nahicore
```

On Claude Code 2.1.275 or later, one command does both:

```text
/plugin install nahicore --marketplace notenderdreams/nahicore
```

Or from a shell: `claude plugin marketplace add notenderdreams/nahicore`, then
`claude plugin install nahicore@nahicore`. Run `/reload-plugins` or start a new
session; the skills appear as `/nahicore:notex`, `/nahicore:brain-dump`,
`/nahicore:name-scout`, and `/nahicore:liquid-metal`, and Claude also loads them
automatically when a request matches. Update with `/plugin marketplace update nahicore`.
To try a local checkout without installing: `claude --plugin-dir /path/to/nahicore`.

### Installer script (Claude Code, Codex, and other agents)

To copy plain skills instead of using the plugin system, use the installer.
Requires **Python 3.10+**. Bash is optional for the installer wrapper. Clone this
repository or extract a release archive, then run:

```bash
git clone https://github.com/notenderdreams/nahicore.git
cd nahicore

# Preview installation into ~/.agents/skills.
python3 scripts/install.py --dry-run

# Install all four skills.
python3 scripts/install.py

# Install only Notex into ~/.codex/skills.
python3 scripts/install.py --target codex --skill notex
```

The shell wrapper accepts the same options: `bash install.sh --help`.
No dependencies are downloaded, application settings changed, or plugins registered.

### Destinations

| Option | Skills directory |
| --- | --- |
| `--target agents` (default), or `--global` | `~/.agents/skills` |
| `--target codex` | `~/.codex/skills` |
| `--target claude` | `~/.claude/skills` (Claude Code, all projects) |
| `--target claude-project` | `.claude/skills` in the current directory (Claude Code, this project) |
| `--target project`, or `--project` | `.agents/skills` in the current directory |
| `--dest /some/path` | The exact custom directory; overrides `--target` |

These are destination presets. Skill discovery and invocation depend on the
application you use; no universal application compatibility is claimed.
Run `python3 /path/to/nahicore/scripts/install.py --project` **from the project
that should receive the skills**. The installer never searches for a project root.

### Select, update, or link skills

```bash
python3 scripts/install.py --list
python3 scripts/install.py --skill notex --skill brain-dump
python3 scripts/install.py --target codex --skill notex --symlink
```

Copy installation is the default. Rerun the same command to update an unchanged
managed installation. Symlinks point to this checkout and follow its edits;
keep the checkout in place. Existing links to the same source can be adopted
with `--symlink`. Use `--force` to switch an existing source link to a copy.

The installer records ownership in `.nahicore-install.json` in the destination.
Unowned or locally modified skill folders cause a refusal before any selected
skill is changed. To replace one while preserving its contents:

```bash
python3 scripts/install.py --target codex --skill notex --force
```

`--force` moves conflicting content into `.nahicore-backups/<id>/<skill>` and
prints its path. Backups are retained for manual recovery. Restore one by moving
the current skill aside and moving the backed-up folder to its original location.
An installation failure can leave earlier skills in the selected batch updated;
each completed skill is recorded separately. Do not run concurrent installers
against the same destination.

### Uninstall

Use the same destination as installation:

```bash
python3 scripts/install.py --target codex --skill notex --uninstall
python3 scripts/install.py --target agents --uninstall --dry-run
```

Without `--skill`, uninstall selects only entries in that destination's ownership
receipt. Other skills are preserved. Modified installations require `--force`,
which backs them up before removal. Symlink uninstall removes the link and keeps
the source. Receipts, backups, and external Brain Dump configuration remain.
Older installations without receipts are treated as unowned; use `--force`
to migrate them with backups. No other applications are reinstalled automatically.

Do not install the same skills both as the plugin and with `--target claude`;
Claude Code would list each skill twice. Plain installs are invoked without the
`nahicore:` prefix, for example `/notex`.

## Use

For an agent that supports `$skill` invocation:

```text
$notex Turn these lecture slides into complete study notes.
$brain-dump --local Explain how the parser handles error recovery.
$name-scout Find names for this project and check likely collisions.
$liquid-metal Use one external scratch script during this session.
```

Other agents may expose skills through slash commands or their own interface.
Refresh the agent's skill discovery or start a new session after installation.

### Notex

Notex preserves slide order, definitions, numbers, examples, quotations, diagrams,
and references. It labels derived solutions and source discrepancies, includes
quizzes and worked exercises, and checks every source page for coverage.
It prepares standalone `.tex` source for TeXifier's built-in TexpadTeX compiler
and performs source checks without compiling unless explicitly asked to compile.

### Brain Dump configuration

Local mode needs no vault setup:

```bash
bash skills/brain-dump/scripts/resolve_target.sh --local
```

Run the resolver from the project being documented. It creates `.dead-brain/`
and adds that folder to the project's `.gitignore`.

For Obsidian, create a private configuration:

```bash
mkdir -p ~/.config/nahicore/brain-dump
cp skills/brain-dump/vault.conf.example ~/.config/nahicore/brain-dump/vault.conf
# Edit VAULT_PATH in the copied file before using vault mode.
```

Optionally copy `projects.map.example` to `projects.map` in the same directory.
Mappings are `project-name|relative/path/inside/vault`; names match literally.
Values are plain text, never executed. Spaces need no shell escaping.
New mappings are saved outside the installed skill.

`XDG_CONFIG_HOME` changes the configuration root. `NAHICORE_CONFIG_DIR` selects
the `nahicore` configuration directory itself; the resolver appends `brain-dump`.
`NAHICORE_VAULT_PATH` overrides the vault value in an existing configuration.
Legacy private files inside the skill remain readable but are excluded from
copy installations and release packages. Move any local customizations to the
user configuration directory before upgrading an old installation.

### Name Scout helper

```bash
python3 skills/name-scout/scripts/check_names.py 'My Project' --checks npm pypi domains
python3 skills/name-scout/scripts/check_names.py 'First Name' 'Second Name' --json
```

The helper queries public services; `GITHUB_TOKEN` is optional for GitHub API
rate limits. Results are evidence at check time, not a registration guarantee.

## Development and releases

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
python3 scripts/build_release.py
```

The archive and SHA-256 checksum are written to `dist/`. Packaging is independent
of Git tracking state and excludes private configuration and caches. CI runs
validation and tests on Linux and macOS and uploads a downloadable archive.
It does not publish a GitHub release.

See [CONTRIBUTING.md](CONTRIBUTING.md), [the release guide](docs/releasing.md),
and [CHANGELOG.md](CHANGELOG.md). The Claude Code plugin manifest and
marketplace live in `.claude-plugin/`; `claude plugin validate .` checks them.

## License

[MIT](LICENSE) © 2026 Nahian (notenderdreams).
