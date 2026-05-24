# AGENTS.md — Host Provisioning Reference

[`INSTALL.md`](../INSTALL.md) is a **declarative, agent-oriented provisioning plan** for bootstrapping a Linux x86_64 host (systemd-based). It lists what must be in place — OS packages, locale/timezone, Neovim, Go — but deliberately does *not* specify how. An AI agent executing it determines the correct package manager, commands, paths, and distribution detection at runtime.

Key principles:
- **Declarative** — states what, never how.
- **Idempotent** — check before act, safe to re-run.
- **Verifiable** — every step has a verification command.
