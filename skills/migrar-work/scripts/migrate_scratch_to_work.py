#!/usr/bin/env python3
"""Migra .scratch/ (no repo) -> <home>/.agents/work/<marca>/ sem reescrever conteúdo.

Exemplos:
  python migrate_scratch_to_work.py --repo-root . --marca guiaucan-skills --dry-run
  python migrate_scratch_to_work.py --repo-root /path/ao/repo --marca meu-app
  python migrate_scratch_to_work.py --repo-root . --marca meu-app --copy
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path


def work_root(marca: str) -> Path:
    return Path.home() / ".agents" / "work" / marca


def iter_files(src: Path):
    for path in sorted(src.rglob("*")):
        if path.is_file():
            yield path


def migrate(
    scratch: Path,
    dest_root: Path,
    *,
    copy: bool,
    force: bool,
    dry_run: bool,
) -> int:
    if not scratch.is_dir():
        print(f"Origem inexistente: {scratch}", file=sys.stderr)
        return 1

    dest_root = dest_root.resolve()
    scratch = scratch.resolve()
    print(f"Origem:  {scratch}")
    print(f"Destino: {dest_root}")

    moved = skipped = conflicts = 0

    for src in iter_files(scratch):
        rel = src.relative_to(scratch)
        dst = dest_root / rel

        if dst.exists():
            same = False
            try:
                same = filecmp.cmp(src, dst, shallow=False)
            except OSError:
                same = False
            if same:
                print(f"  skip (idêntico): {rel}")
                skipped += 1
                if not copy and not dry_run:
                    src.unlink()
                continue
            if not force:
                print(f"  CONFLITO (destino existe): {rel}", file=sys.stderr)
                conflicts += 1
                continue
            print(f"  overwrite: {rel}")

        print(f"  {'copy' if copy else 'move'}: {rel}")
        if dry_run:
            moved += 1
            continue

        dst.parent.mkdir(parents=True, exist_ok=True)
        if copy:
            shutil.copy2(src, dst)
        else:
            shutil.move(str(src), str(dst))
        moved += 1

    if not copy and not dry_run:
        # remove empty dirs under .scratch
        for path in sorted(scratch.rglob("*"), reverse=True):
            if path.is_dir():
                try:
                    path.rmdir()
                except OSError:
                    pass
        try:
            scratch.rmdir()
        except OSError:
            pass

    print(f"Feito: {moved} migrados, {skipped} idênticos, {conflicts} conflitos.")
    if conflicts:
        print("Reexecute com --force após ok do usuário, ou resolva os conflitos à mão.", file=sys.stderr)
        return 2
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True, help="Raiz do repositório (onde está .scratch/)")
    parser.add_argument("--marca", required=True, help="Marca do projeto (pasta sob ~/.agents/work/)")
    parser.add_argument("--copy", action="store_true", help="Copiar em vez de mover")
    parser.add_argument("--force", action="store_true", help="Sobrescrever destino em conflito")
    parser.add_argument("--dry-run", action="store_true", help="Só listar ações")
    args = parser.parse_args()

    scratch = args.repo_root / ".scratch"
    dest = work_root(args.marca.strip())
    return migrate(scratch, dest, copy=args.copy, force=args.force, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
