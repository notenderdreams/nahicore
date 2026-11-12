# Contributing

Use Python 3.10 or newer and Bash. Runtime tools use the Python standard library;
there are no packages to install for validation or tests.

Add each skill under `skills/<name>/SKILL.md`, with a matching lowercase,
hyphenated `name` and a specific, single-line `description` in YAML frontmatter.
Include `agents/openai.yaml` with a display name, a 25–64 character short
description, and a default prompt mentioning `$<name>`. Keep the supported
metadata format simple: single-line frontmatter fields and quoted UI strings.

Keep personal paths, credentials, vault settings, and generated output out of
commits. Ship `.example` configuration files. Bundle helpers only when the skill
needs them, and keep reference links relative to the skill folder.

Before submitting:

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
python3 scripts/build_release.py
git diff --check
```

Test installer and path-resolution changes in temporary directories. Add tests
for observable behavior and preservation of existing user files. Network lookup
tests should use fixtures rather than relying on live registry availability.

Describe the resulting behavior and the checks you ran. See
[the release guide](docs/releasing.md) for packaging and publishing.
