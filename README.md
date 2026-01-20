# AutoConfigOSCLI

Professional CLI tool to automate development environment configuration on macOS and Linux.

## Overview
AutoConfigOSCLI automates the installation, update, and maintenance of your dev tools using defined profiles. It manages system packages (apt, brew, dnf, pacman) and configurations.

## Features
- **Stateless**: Logic in git, state in SQLite.
- **Multi-OS**: macOS and Linux (Debian, Fedora, Arch).
- **Profiles**: YAML-based configuration.
- **Safety**: Atomic updates, backups, and dry-runs.

## Installation

### Linux / macOS
```bash
./scripts/init.sh
```
Ensure `~/.local/bin` is in your PATH.

## Usage

### List Profiles
```bash
autoconfigoscli list
```

### Install a Profile
```bash
autoconfigoscli install Backend-Dev
```

### Check Status
```bash
autoconfigoscli status
```

### Export/Import State
```bash
autoconfigoscli export --output my_backup.json
autoconfigoscli import my_backup.json
```

### Diagnostics
```bash
autoconfigoscli doctor
```

## Directory Structure
- `~/.autoconfigoscli/repo`: Source code.
- `~/.autoconfigoscli/data`: SQLite database.
- `~/.autoconfigoscli/logs`: Logs.

## Contributing
Please read `decisions_ai.md` for architectural decisions.
