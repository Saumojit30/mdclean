# mdclean

`mdclean` is a lightweight command-line tool that automatically cleans Markdown (`.md`) files by removing AI-generated citation markers such as:

```text
[web:319]
[web:306]
[web:311]
```

It is designed to work on any repository containing Markdown documentation. The tool recursively scans directories, updates all matching `.md` files, and leaves the rest of the repository untouched.

---

# Features

* Recursively scans Markdown (`.md`, `.mdx`, and custom extensions) files.
* Removes AI citation markers like `[web:123]`, `[cite:45]`, `[ref:67]`.
* Preserves Markdown formatting — **fenced code blocks are skipped**.
* Preserves original line endings (CRLF / LF).
* Cleans up double spaces left behind after citation removal.
* Supports preview mode (`--dry-run`) with detailed citation listing.
* Optional backup creation (`--backup`) using safe copy (original untouched).
* Include/exclude directory filters (`--include` / `--exclude` globs).
* Git-only mode (`--git-only`) for processing tracked files only.
* Undo support (`--undo`) to restore from `.bak` backups.
* Custom citation patterns via `--pattern` regex flag.
* Displays a summary of processed files and removed references.
* Works on Windows, macOS, and Linux.
* Compatible with both global Python installations and virtual environments.
* No third-party runtime dependencies.

---

# Project Structure

```text
mdclean/
├── pyproject.toml
├── README.md
├── LICENSE
└── src/
    └── mdclean/
        ├── __init__.py
        ├── __main__.py
        └── cli.py
```

---

# Installation

## Option 1 – Install for Development

Clone the project and install it in editable mode.

```bash
git clone https://github.com/Saumojit30/mdclean.git

cd mdclean

pip install -e .
```

Editable mode means any changes you make to the source code are immediately reflected without reinstalling the package.

---

## Option 2 – Standard Installation

```bash
pip install .
```

---

## Option 3 – Install Globally (Recommended)

Using `pipx`:

```bash
pipx install .
```

or after publishing:

```bash
pipx install mdclean
```

This installs `mdclean` as a standalone command available from any terminal.

---

# Verify Installation

Run:

```bash
mdclean --help
```

If the installation succeeded, the help screen will be displayed.

---

# Usage

Navigate to any repository that contains Markdown files.

Example:

```bash
cd ~/Projects/Tracebase
```

Run:

```bash
mdclean
```

The tool scans the current directory recursively and cleans every `.md` file it finds.

---

## Clean Another Directory

```bash
mdclean /path/to/project
```

Example:

```bash
mdclean ~/Projects/MyRepository
```

---

## Preview Changes

To see what would change without modifying files:

```bash
mdclean --dry-run
```

Citations are listed per file:

```
[DRY RUN] .\README.md  (-85 bytes)
    - [web:319]
    - [web:306]
```

---

## Create Backups

Before editing files:

```bash
mdclean --backup
```

A `.bak` copy is created beside each modified file (original is never renamed — copy is made first).

---

## Process `.mdx` Files

```bash
mdclean --ext .md,.mdx
```

---

## Include / Exclude Filters

```bash
mdclean --include "docs/**"
mdclean --exclude "node_modules/**"
mdclean --include "docs/**" --exclude "**/drafts/**"
```

---

## Git-Only Mode

Only process files tracked by git:

```bash
mdclean --git-only
```

Skips untracked files and ignores file listing outside the git tree.

---

## Undo Backups

Restore all files from their `.bak` copies:

```bash
mdclean --undo
```

Each `.bak` is copied over the current file, then the `.bak` is deleted.

---

## Custom Citation Pattern

```bash
mdclean --pattern "\[source:\d+\]"
mdclean --pattern "\[(cite|ref|source):\d+\]"
```

---

## Disable Space Cleanup

```bash
mdclean --no-space-clean
```

Leaves any double spaces that result from citation removal as-is.

---

# All Flags

| Flag | Default | Description |
|---|---|---|
| `path` | `.` | Directory to scan |
| `--dry-run` | off | Preview changes |
| `--backup` | off | Create `.bak` copies |
| `--ext` | `.md` | Comma-separated extensions |
| `--include` | — | Glob pattern to include |
| `--exclude` | — | Glob pattern to exclude |
| `--git-only` | off | Git-tracked files only |
| `--undo` | off | Restore from `.bak` files |
| `--pattern` | `\[\w+:\d+\]` | Custom citation regex |
| `--no-space-clean` | off | Keep double spaces |
| `--version` | off | Show version |
| `--help` | — | Show help |

---

# Example

Before:

```md
This project follows AI guidelines. [web:319][web:306]

Documentation is important. [web:22]
```

After:

```md
This project follows AI guidelines.

Documentation is important.
```

---

# How It Works

1. Starts from the specified directory (or the current directory if none is provided).
2. Recursively searches for matching files (`.md` by default).
3. Applies include/exclude glob filters.
4. (Optional) Filters to git-tracked files only.
5. Reads each file into memory.
6. Detects AI citation markers using regular expressions.
7. Preserves fenced code blocks — citations inside them are skipped.
8. Removes matching citations from remaining text.
9. Cleans up extra whitespace (optional).
10. Preserves original line endings (CRLF / LF).
11. (Optional) Creates a `.bak` copy before writing.
12. Writes the updated content back to disk.
13. Prints a summary of the changes.

---

# Supported Commands

Clean the current directory:

```bash
mdclean
```

Clean a specific repository:

```bash
mdclean ~/Projects/MyRepo
```

Preview changes:

```bash
mdclean --dry-run
```

Create backups:

```bash
mdclean --backup
```

Process `.mdx` files:

```bash
mdclean --ext .md,.mdx
```

Git-only mode:

```bash
mdclean --git-only
```

Custom citation pattern:

```bash
mdclean --pattern "\[custom:\d+\]"
```

Undo from backups:

```bash
mdclean --undo
```

Display help:

```bash
mdclean --help
```

---

# Requirements

* Python 3.9 or later
* No third-party runtime dependencies

---

# Typical Workflow

```bash
cd ~/Projects/SomeRepository

mdclean --dry-run

mdclean --backup

git diff

git commit -am "Clean AI citation references"
```

---

# Edge Cases Handled

| Edge case | How it's handled |
|---|---|
| Citations in fenced code blocks | Preserved — not removed |
| CRLF (Windows) line endings | Detected and preserved |
| Read-only or locked files | Skipped with a warning |
| Non-UTF-8 / binary `.md` files | Read with `errors='replace'` |
| Orphaned double spaces | Automatically cleaned (can be disabled) |
| Files with no citations | Skipped (no modification) |
| Paths with spaces | Handled (quoted properly) |

---

# License

MIT


