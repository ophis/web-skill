# CLAUDE.md — web-skill repo rules

## Sync rule

`script/install.sh` and `INSTALL.md` must be kept in sync with the actual skill structure at all times:

- Adding a new reference under `skill/references/`? Update the install.sh system-deps section if the reference needs new CLI tools, and update INSTALL.md's model-download list if it downloads new models on first use.
- Removing a dependency? Remove it from install.sh and INSTALL.md.
- Changing the `skill/` layout? Verify install.sh still copies correctly and INSTALL.md's verify step still works.

Never leave install.sh or INSTALL.md stale after a structural change.
