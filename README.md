# AutoConfigOSCLI (v0.1.0)

**Professional Environment Automation for Developers.**
*Offline-first. Reversible. Hybrid AI.*

---

## 🚀 Introduction

**AutoConfigOSCLI** is a command-line tool designed to set up, maintain, and replicate professional development environments across Linux and macOS. 

Unlike simple dotfile managers, it provides a **holistic** approach:
- **Context-Aware**: Adapts to your hardware (RAM, CPU), machine type (Laptop/Server), and role (Frontend/Backend).
- **Tiered Profiles**: Choose between `Lite` (CLI-only), `Mid` (Balanced), or `Full` (Batteries-included) stacks.
- **Safe & Reversible**: Every change is tracked. Built-in `audit`, `backup`, and `downgrade` capabilities.
- **Agentless Remote Management**: Configure remote servers via SSH without installing persistent agents.

## 🛡️ Core Principles

1.  **Offline-First**: Core logic, profile resolution, and validation work without internet. AI is an optional layer.
2.  **Reversible**: State is tracked in a local SQLite database. You can roll back changes (`downgrade`).
3.  **Idempotent**: Running the same command twice is safe.
4.  **Transparent AI**: AI explains, recommends, and verifies, but **never executes** without your confirmation.
5.  **Agentless**: No background daemons. SSH connections use your native system configuration.

## 📦 Installation

```bash
git clone https://github.com/yourusername/AutoConfigOSCLI.git
cd AutoConfigOSCLI
./init.sh
```

**What `init.sh` does:**
- Checks for Python 3.
- Creates a virtual environment.
- Installs dependencies.
- Links the `autoconfigoscli` command to your shell (e.g., `~/.local/bin` or alias).

**What it does NOT do:**
- It does NOT install packages on your system.
- It does NOT modify your root files.

## 🎮 Basic Usage (Safe Demo)

You can explore the tool without making any changes using `--dry-run`.

### 1. List Profiles
See all available official profiles:
```bash
autoconfigoscli profiles list
```

### 2. Inspect a Profile
See exactly what a profile includes:
```bash
autoconfigoscli profiles show backend-python-dev-postgresql-mid
```

### 3. Dry-Run Install
Simulate an installation to see the exact commands that would be executed:
```bash
autoconfigoscli install backend-python-dev-postgresql-mid --dry-run --verbose
```
*Output will show plan: [System] Install python3, [Flatpak] Install vscode, etc.*

## 🏗️ Profiles & Tiers

We strictly categorize profiles to prevent bloat.

| Tier | Focus | Typical Tools | Editors |
|:---|:---|:---|:---|
| **Lite** | Efficiency, Low Resources, SSH | TUI Apps, CLI Clients | `micro`, `neovim` |
| **Mid** | Standard Workflow | Docker, Language Runtimes | `vscode` |
| **Full** | Productivity Powerhouse | GUI Databases, IDE Suites | `jetbrains-toolbox`, `pycharm`, `dbeaver` |

**Variants:**
- **PostgreSQL**: Includes `psql` (Lite) or `postgresql-server` (Mid/Full).
- **MongoDB**: Includes `mongosh` (Lite) or `compass` (Full).

**Examples:**
- `general-dev-lite`: Git, Micro, Ripgrep, Htop.
- `fullstack-node-dev-postgresql-mid`: Node, PNPM, VS Code, Docker, Postgres.

## 🛠️ User & Manual Mode

### Manual Selection
Interactive package picker using FZF:
```bash
autoconfigoscli manual
```

### User Profiles
Create your own mix:
```bash
autoconfigoscli profiles user create my-custom-stack
```

## 🔄 Updates & Backups

**Update Tool:**
```bash
autoconfigoscli update
```

**Restore State:**
Pass a backup JSON to revert your system state:
```bash
autoconfigoscli downgrade --backup ~/.autoconfigos/backups/state_20231020.json
```

## 🩺 Diagnostics

- **`autoconfigoscli doctor`**: Checks dependencies, internet, and disk space.
- **`autoconfigoscli audit`**: Scans your hardware and OS details.
- **`autoconfigoscli whoami`**: View/Edit your user identity (Role, Preferences).

## 🧠 Hybrid AI

**Privacy First:**
- **Local Engine**: Recommendations run locally 100% of the time based on RAM/CPU/Role.
- **Optional Cloud**: You can configure Gemini/OpenAI for "Explain" features.
- **PII Scrubbing**: Paths (`/home/user`) and sensitive env vars are scrubbed before sending queries.

```bash
# Set Provider (Optional)
autoconfigoscli ai config provider set gemini

# Ask questions
autoconfigoscli ai ask "Why should I use podman instead of docker?"
```

## 📡 Remote SSH Management

Manage remote machines as easily as your local one.

```bash
# Check remote status
autoconfigoscli remote status user@192.168.1.50

# Install profile remotely (Dry Run)
autoconfigoscli remote install user@server.local backend-python-dev-mongodb-lite --dry-run
```

**Features:**
- **Bootstrap**: Auto-installs git/python if missing.
- **Ephemeral**: Clones tool to `/tmp`, executes, and deletes itself.
- **Copy Profile**: Transfer your local user profile to remote: `--copy-user-profile my-stack`.

## 🔒 Security & Trust

- **No Credentials**: We never ask for or store sudo passwords (sudo handles it).
- **No Telemetry**: Your data stays on your machine.
- **Explicit Confirmation**: Destructive actions always strictly require user confirmation.

---
*Generated by AutoConfigOSCLI v0.1.0*
