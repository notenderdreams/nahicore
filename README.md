# nahicore ⚡

> **A curated collection of bespoke skills, workflows, and soft-tooling for AI coding agents.**  
> Built for Antigravity, Claude Code, Zed, Cursor, Codex, and modern agentic pair-programming environments.

---

## What is `nahicore`?

**`nahicore`** is a unified agent skills repository and plugin suite created by [Sajid Al Nahian](https://github.com/notenderdreams). Instead of distributing isolated, fragmented single-skill repositories, `nahicore` packages high-discipline agent behaviors, ephemeral execution runtimes, and developer ergonomics into a single cohesive toolkit.

---

## Included Skills

| Skill | Command | Description |
| :--- | :--- | :--- |
| [**Liquid Metal**](#featured-skill-liquid-metal-) | `/liquid-metal` | **Persistent, single-file soft tooling.** Designates exactly ONE scratch file outside the repository, shape-shifting in place whenever dynamic computation is needed. Zero repo pollution, no inline quoting hell. |

*(More skills and agent workflows are continually added to `skills/`)*.

---

## Featured Skill: Liquid Metal 🪞

### The Problem

When coding agents need dynamic computation—parsing logs, transforming complex JSON, inspecting ASTs, or orchestrating pipelines—they usually default to one of two flawed patterns:

1. **Repository Pollution**: Generating multiple temporary scripts (`test_parse.py`, `temp_extract.ts`, `script1.sh`) inside your project directory, dirtying `git status` and risking accidental commits.
2. **Inline Execution Quoting Hell**: Running ad-hoc one-liners via `python -c "..."` or multiline heredocs inside bash tools, which regularly fail on complex escaping, quotes, indentation, and nested braces.

---

### The Solution

Like liquid metal that reforms into whatever tool is needed at the moment, **Liquid Metal** forces the agent into a disciplined workflow:

* **One File to Rule Them All**: Exactly **ONE** persistent script file is designated outside the repository (in the session scratch directory, e.g. `<scratch>/liquid_metal.py`).
* **Shape-Shift in Place**: Whenever dynamic logic or a helper tool is needed, the agent completely overwrites this single file with the new code.
* **Native Runner Execution**: The script is executed directly with its runtime (`python3`, `bun`, `node`, `bash`)—clean, reliable, and unpolluted.
* **Zero Git Dirt**: Your project tree stays 100% clean.

```
                  ┌─────────────────────────────────┐
                  │  Need dynamic utility or tool   │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
        ┌─────────────────────────────────────────────────────┐
        │ Overwrite the SINGLE persistent script file:        │
        │ `<scratch>/liquid_metal.<ext>`                      │
        └──────────────────────────┬──────────────────────────┘
                                   │
                                   ▼
        ┌─────────────────────────────────────────────────────┐
        │ Execute the file via native runner:                 │
        │ `python3 <scratch>/liquid_metal.py`                 │
        └──────────────────────────┬──────────────────────────┘
                                   │
                                   ▼
        ┌─────────────────────────────────────────────────────┐
        │ Read stdout / results and proceed                   │
        │ (File remains ready to be reshaped for next task)   │
        └─────────────────────────────────────────────────────┘
```

#### Supported Runtimes

| Language | Extension | Default Runner | Use Case |
| :--- | :--- | :--- | :--- |
| **Python** | `.py` | `python3 <path>` / `uv run <path>` | Data parsing, AST analysis, math, APIs |
| **TypeScript** | `.ts` | `bun run <path>` / `npx tsx <path>` | Type checking, frontend transformations |
| **JavaScript** | `.js` | `node <path>` / `bun <path>` | Quick Node utilities, package testing |
| **Bash** | `.sh` | `bash <path>` | System orchestration, multi-pipeline flows |

---

## Repository Layout

```text
nahicore/
├── .gitignore
├── install.sh                  # Multi-target installer (Antigravity plugin & agent skills)
├── LICENSE                     # MIT License
├── README.md                   # nahicore suite documentation
├── plugin.json                 # Antigravity plugin manifest (name: "nahicore")
└── skills/
    └── liquid-metal/
        └── SKILL.md            # Canonical skill definition for Liquid Metal
```

---

## Installation

### Option 1: Installer Script (Recommended)

Clone the repository and run the installer:

```bash
git clone https://github.com/notenderdreams/nahicore.git
cd nahicore

# Install globally to ~/.gemini/config/plugins/nahicore and ~/.agents/skills/
./install.sh

# Or create symlinks for live development (recommended):
./install.sh --symlink

# Or install member skills locally to the current project (.agents/skills/):
./install.sh --project
```

### Option 2: Manual Installation

**Antigravity (Global Plugin):**
```bash
ln -s "$(pwd)" ~/.gemini/config/plugins/nahicore
```

**Agent Ecosystem (`~/.agents/skills`):**
```bash
mkdir -p ~/.agents/skills/liquid-metal
ln -s "$(pwd)/skills/liquid-metal/SKILL.md" ~/.agents/skills/liquid-metal/SKILL.md
```

---

## Usage

In your agent chat or terminal prompt:

```text
/liquid-metal
```

Or mention it directly:
> *"Use liquid-metal for any helper scripts needed during this session."*

The agent will immediately restrict all helper code to the single external persistent file.

---

## Adding New Skills to `nahicore`

To add a new skill to the collection:

1. Create a new directory under `skills/<your-skill-name>/`.
2. Add a `SKILL.md` with standard YAML frontmatter:
   ```markdown
   ---
   name: your-skill-name
   description: Detailed explanation of when the skill activates and what it does.
   ---

   # Your Skill Title
   ...
   ```
3. Run `./install.sh --symlink` to immediately make the new skill available across your agent environments.

---

## License

[MIT](LICENSE) © 2026 [Nahian](https://github.com/notenderdreams)
