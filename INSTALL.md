# Host Installation Reference

## 1. Rules

- **Declarative only** — this file states *what* must be in place, never *how* to achieve it. All execution details (package manager commands, version checks, paths, distribution detection) are determined at runtime by the provisioning agent.
- **Target platform** — Linux x86_64 (systemd-based, apt/yum/pacman).
- **Agent-oriented** — each step is self-contained, verifiable, and recoverable.
- **Idempotent** — check before act. Before installing anything, verify whether it already exists. If it does, skip it. If it doesn't, install it. Never reinstall what's already there. Every step must be safe to re-run without causing side effects.

---

## 2. Prerequisites

- `sudo` access with passwordless `sudo` or a known sudo password.
- Internet connectivity, standard `PATH` (`/usr/local/bin`, `/opt` writable by root).

---

## 3. OS Packages

Install the following core utilities via the system package manager. Determine the correct package manager and package names for the target distribution at execution time.

| Package    | Purpose                                  |
|------------|------------------------------------------|
| `tmux`     | Terminal multiplexer                     |
| `htop`     | Interactive process viewer               |
| `gh`       | GitHub CLI (auth, PRs, issues)           |
| `git`      | Version control                          |
| `zip`      | Compression (.zip archives)              |
| `unzip`    | Decompression (.zip archives)            |
| `sqlite3`  | SQLite database engine                   |
| `jq`       | JSON processor (query, filter, transform) |

### Verification

Each package should respond with a version string when queried. If any fail, install that package individually.

---

## 4. System Locale & Timezone

Set the system to `en_US.UTF-8` locale and `UTC` timezone. These are recommended defaults for server/container environments — predictable encoding avoids subtle bugs in scripts, databases, and Python.

- The `en_US.UTF-8` locale must be generated (if not already) and set as the system-wide default for `LANG` and `LC_ALL`.
- The system timezone must be set to `UTC`.

### Verification

- `locale` should show `LANG=en_US.UTF-8` and `LC_ALL=en_US.UTF-8`.
- `date` should display the timezone as `UTC` (or `+0000`).

---

## 5. Neovim (latest stable)

- Use https://github.com/neovim/neovim/releases/latest/download/nvim-linux-x86_64.tar.gz
- Install to `/opt/nvim-linux-x86_64`.
- Make it available to all users via `/etc/profile.d/nvim.sh`.
- Verify it's properly installed by sourcing `/etc/profile.d/nvim.sh` and running `nvim --version`.

---

## 6. Go (latest stable)

- Install the official Go binary tarball system-wide into `/opt/go`.
- Make it available to all users via `/etc/profile.d/go.sh`.
- Verify it's properly installed by sourcing `/etc/profile.d/go.sh` and running `go version`.

---

## 7. Summary Checklist

After all steps are complete, verify every installed component reports a version string:

- OS packages: `tmux`, `htop`, `gh`, `git`, `zip`, `unzip`, `sqlite3`, `jq`
- Neovim
- Go

If any step fails, report the failed command and its stderr output, then stop — do not silently continue.
