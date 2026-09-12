---
name: liquid-metal
description: Activates single-file persistent soft tooling. Instead of running inline code or scattering multiple temporary files, maintains exactly ONE dedicated persistent script file outside the repository for the entire session, re-shaping and executing it whenever dynamic tools are needed.
---

# Liquid Metal (`/liquid-metal`)

> A single, persistent shape-shifting script file maintained outside the repository for the entire session.

Like liquid metal that reforms into whatever tool is needed at the moment, **Liquid Metal** designates **exactly ONE dedicated script file** outside the project repository. Whenever the agent needs to inspect data, parse files, calculate values, or execute dynamic logic, it updates that single file in place and runs it.

---

## The Golden Rules

1. **Exactly One File**: Never create multiple scratch files or scatter one-off scripts. There is only **one** persistent script file for the entire session/project (e.g., `scratch/liquid_metal.py`).
2. **Out-of-Repository Storage**: That single file must live **outside** the active project repository (in the session scratch directory). It must never exist inside the repository tree or show up in `git status`.
3. **Shape-Shift in Place (Overwrite)**: Whenever a new tool or computation is needed, completely overwrite this single file with the new code.
4. **No Inline Commands**: Never use inline execution flags (e.g., `python -c "..."`, `node -e "..."`, or inline multiline heredocs). Always write to the single persistent file, then run it.

---

## File Location & Designation

At the start of the session or upon first invocation, designate the single persistent file in the external scratch directory:

* **Primary Path**: `<appDataDir>/brain/<conversation-id>/scratch/liquid_metal.<ext>`
* **Fallback Path**: `~/.cache/liquid-metal/liquid_metal.<ext>`

*(Default extension is `.py`, or `.ts` / `.js` / `.sh` if the primary project environment requires a different runtime).*

---

## Workflow (Loop for Every Task)

Every time dynamic execution or a soft tool is required during the session:

```
                  ┌─────────────────────────────────┐
                  │  Need dynamic utility or code   │
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

### 1. Re-shape (Overwrite)
Write the new self-contained logic into the single designated file, completely replacing any prior contents.

### 2. Execute with Native Runner
Run that exact file path directly:
```bash
python3 /path/to/scratch/liquid_metal.py
```
*(or `bun run`, `node`, `bash` depending on the file's designated runtime).*

### 3. Capture Results
Collect the output and continue the task. The file stays in place, waiting to be overwritten the next time dynamic logic is needed.

---

## Guardrails

* **Zero Repository Pollution**: No script files created inside `./`, `./src`, `./scripts`, or any workspace folder.
* **Zero File Proliferation**: Do NOT create `script1.py`, `script2.py`, `temp_test.py`, etc. Only reuse and overwrite `liquid_metal.<ext>`.
* **No Inline Pipelining**: Strictly avoid piping multiline strings into shell interpreters.
