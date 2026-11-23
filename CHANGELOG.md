# Changelog

## 0.1.0

- Bundle Brain Dump, Liquid Metal, Name Scout, Notex, and Release Man as standalone skills.
- Add selective copy and symlink installation, destination presets, dry runs,
  ownership receipts, conflict backups, and managed uninstall.
- Keep Brain Dump configuration outside the distributed skill and provide examples.
- Package the collection as a Claude Code plugin and single-plugin marketplace
  in `.claude-plugin/`, replacing the legacy root `plugin.json`.
- Add the `claude-project` installer target for `.claude/skills` in a project.
- Add UI metadata, validation, integration tests, CI, and deterministic release
  archives with SHA-256 checksums.
