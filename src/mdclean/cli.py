import argparse
import difflib
import os
import re
import shutil
import subprocess
from pathlib import Path

__version__ = "0.2.0"

DEFAULT_PATTERN = r'\[\w+:\d+\]|\[\^\d+\]'


def find_files(root: str, extensions: list[str], include: str | None, exclude: str | None) -> list[str]:
    result = []
    root_path = Path(root).resolve()
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if not any(f.endswith(ext) for ext in extensions):
                continue
            full = os.path.join(dirpath, f)
            rel = os.path.relpath(full, root)
            if include and not Path(rel).match(include):
                continue
            if exclude and Path(rel).match(exclude):
                continue
            result.append(full)
    return result


def get_git_files(root: str) -> set[str]:
    try:
        result = subprocess.run(
            ['git', 'ls-files'],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return set()
        return set(result.stdout.splitlines())
    except FileNotFoundError:
        return set()


def detect_line_ending(text: str) -> str:
    cr = text.count('\r\n')
    lf = text.count('\n') - cr
    return '\r\n' if cr >= lf else '\n'


def clean_content(text: str, citation_re: re.Pattern, clean_spaces: bool) -> tuple[str, list[str]]:
    le = detect_line_ending(text)
    lines = text.split(le)
    citation_list = []
    in_fence = False
    new_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            in_fence = not in_fence
            new_lines.append(line)
            continue
        if in_fence:
            new_lines.append(line)
            continue
        found = citation_re.findall(line)
        if found:
            citation_list.extend(found)
        cleaned = citation_re.sub('', line)
        cleaned = cleaned.rstrip()
        if clean_spaces:
            cleaned = re.sub(r'  +', ' ', cleaned)
        new_lines.append(cleaned)

    result = le.join(new_lines)
    return result, citation_list


def process_file(path: str, citation_re: re.Pattern, dry_run: bool, backup: bool, clean_spaces: bool) -> dict | None:
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            original = f.read()
    except Exception as e:
        print(f'[ERROR] Could not read {path}: {e}')
        return None

    updated, citations = clean_content(original, citation_re, clean_spaces)
    if original == updated:
        return None

    info = {
        'file': path,
        'original': original,
        'updated': updated,
        'removed': len(original) - len(updated),
        'citations': citations,
    }

    if not dry_run:
        try:
            if backup:
                shutil.copy2(path, path + '.bak')
            with open(path, 'w', encoding='utf-8', newline='') as f:
                f.write(updated)
        except Exception as e:
            print(f'[ERROR] Could not write {path}: {e}')
            return None

    return info


def undo_backups(root: str) -> int:
    restored = 0
    root_path = Path(root).resolve()
    for bak in root_path.rglob('*.bak'):
        original = bak.with_suffix('')
        try:
            shutil.copy2(str(bak), str(original))
            bak.unlink()
            restored += 1
            print(f'[RESTORED] {original}')
        except Exception as e:
            print(f'[ERROR] Could not restore {original}: {e}')
    return restored


def make_diff(filepath: str, original: str, updated: str) -> str:
    lines = difflib.unified_diff(
        original.splitlines(keepends=True),
        updated.splitlines(keepends=True),
        fromfile=filepath,
        tofile=filepath,
    )
    return ''.join(lines).rstrip()


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Remove AI citation markers from Markdown files'
    )
    parser.add_argument(
        'path', nargs='?', default='.',
        help='Directory to scan (default: current directory)'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--show', choices=['diff', 'summary'], default='summary',
        help='Display mode for dry-run: "diff" shows unified diff, "summary" lists citations (default)'
    )
    parser.add_argument(
        '--backup', action='store_true',
        help='Create .bak files before modifying'
    )
    parser.add_argument(
        '--ext', default='.md',
        help='Comma-separated file extensions to process (default: .md)'
    )
    parser.add_argument(
        '--include',
        help='Only process files matching this glob pattern (e.g. "docs/**")'
    )
    parser.add_argument(
        '--exclude',
        help='Skip files matching this glob pattern (e.g. "node_modules/**")'
    )
    parser.add_argument(
        '--git-only', action='store_true',
        help='Only process files tracked by git'
    )
    parser.add_argument(
        '--undo', action='store_true',
        help='Restore files from .bak backups and exit'
    )
    parser.add_argument(
        '--pattern', default=DEFAULT_PATTERN,
        help=f'Custom regex pattern for citations (default: {DEFAULT_PATTERN})'
    )
    parser.add_argument(
        '--no-space-clean', action='store_true',
        help='Do not clean up double spaces left behind by citation removal'
    )
    parser.add_argument(
        '--version', action='store_true',
        help='Show version and exit'
    )
    args = parser.parse_args()

    if args.version:
        print(f'mdclean {__version__}')
        return

    root = args.path

    if args.undo:
        count = undo_backups(root)
        print(f'Restored {count} file(s).')
        return

    extensions = [e.strip() if e.startswith('.') else f'.{e.strip()}' for e in args.ext.split(',')]
    files = find_files(root, extensions, args.include, args.exclude)

    if args.git_only:
        git_files = get_git_files(root)
        if not git_files:
            print('[WARNING] Not a git repository or git not found. Processing all files.')
        else:
            root_path = Path(root).resolve()
            tracked = {str(root_path / f).replace('\\', '/') for f in git_files}
            files = [f for f in files if f.replace('\\', '/') in tracked]
            print(f'[INFO] Git-only mode: {len(files)} tracked file(s) found.')

    if not files:
        print('No matching files found.')
        return

    is_dry_run = args.dry_run
    citation_re = re.compile(args.pattern)
    total_removed = 0
    total_citations = 0
    modified = 0

    for path in files:
        info = process_file(path, citation_re, is_dry_run, args.backup, not args.no_space_clean)
        if info:
            modified += 1
            total_removed += info['removed']
            total_citations += len(info['citations'])
            mode = '[DRY RUN]' if is_dry_run else '[MODIFIED]'
            print(f'{mode} {info["file"]}  (-{info["removed"]} bytes)')
            if is_dry_run and args.show == 'diff':
                print(make_diff(info['file'], info['original'], info['updated']))
            elif is_dry_run and args.show == 'summary':
                for c in info['citations']:
                    print(f'    - {c}')
            elif not is_dry_run:
                print(f'    removed {len(info["citations"])} citation(s)')

    what = 'Would clean' if is_dry_run else 'Cleaned'
    print(f'\n{what} {modified} file(s), {total_citations} citation(s), {total_removed} byte(s).')


if __name__ == '__main__':
    main()
