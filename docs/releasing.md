# Releasing nahicore

The distribution is a collection of skill folders, not a hosted service.
`.claude-plugin/` makes the repository a Claude Code plugin and marketplace;
the installer itself does not register plugins or change application settings.

1. Update `VERSION`, the `version` fields in `.claude-plugin/plugin.json` and
   `.claude-plugin/marketplace.json`, and `CHANGELOG.md`. `scripts/validate.py`
   rejects mismatched versions. Claude Code users only receive an update when
   the plugin version changes. The first packaged version is `0.1.0`.
2. Run the checks in [CONTRIBUTING.md](../CONTRIBUTING.md).
3. Inspect `dist/nahicore-<version>.tar.gz` and its adjacent `.sha256` file.
   The builder excludes private `vault.conf` and `projects.map` files, caches,
   Git history, and build output. Configuration examples remain included.
4. Extract the archive into a temporary directory and try installation with
   `python3 scripts/install.py --dest /path/to/temporary/skills --skill notex`.
5. Review and commit the intended files, then push the branch. CI validates on
   macOS and Linux and uploads an archive artifact; it does not publish a release.
6. When ready to publish, tag the reviewed commit `v<version>`, push that tag,
   and create a GitHub release attaching the archive and checksum.

Example publishing commands, run only when you intend to publish:

```bash
git tag v0.1.0
git push origin v0.1.0
gh release create v0.1.0 dist/nahicore-0.1.0.tar.gz dist/nahicore-0.1.0.tar.gz.sha256 --title 'nahicore 0.1.0' --notes-file CHANGELOG.md
```

Builds use normalized archive paths, permissions, ownership, and timestamps.
Identical public source files produce identical archive bytes. The archive does
not depend on whether source files have already been committed. Review the
archive contents and source diff before publishing.
