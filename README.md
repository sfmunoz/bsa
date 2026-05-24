# bsa — BootStrap Agent

Declarative, agent-oriented host provisioning for Linux x86_64 (systemd-based).

[`INSTALL.md`](INSTALL.md) is the provisioning plan. It states **what** must be in place — never **how**. An AI agent executing it determines the correct package manager, commands, paths, and distribution detection at runtime.

## Key Principles

- **Declarative** — states what, never how.
- **Idempotent** — check before act, safe to re-run.
- **Verifiable** — every step has a verification command.
- **Agent-oriented** — each step is self-contained, recoverable, and platform-agnostic.

## What Gets Provisioned

- **OS packages** — core CLI utilities (`tmux`, `htop`, `gh`, `git`, `zip`, `unzip`, `sqlite3`, `jq`)
- **System config** — `en_US.UTF-8` locale, `UTC` timezone
- **Developer tools** — Neovim (latest, binary install), Go (latest, binary install)

See [`INSTALL.md`](INSTALL.md) for the full specification.

## Usage

```bash
# Agent reads INSTALL.md and provisions accordingly
# No manual commands needed — the agent handles everything
```

Prerequisites: `sudo` access, internet connectivity, standard `PATH`.
