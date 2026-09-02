#!/usr/bin/env python3
"""Daily GitHub contribution helper.

    python green.py once              # commit today, no push
    python green.py once --push       # commit today and push
    python green.py backfill --days 180 --min 1 --max 3 --push

Git author email MUST be an address listed at github.com/settings/emails
or the squares will not attach to your profile.

Schedule the daily run in GitHub Actions (PC can be off). Use this script
locally only for backfill or as a Task Scheduler fallback.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import random
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG = ROOT / "data" / "log.txt"


def run(cmd: list[str], env: dict[str, str] | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(
        cmd,
        cwd=ROOT,
        env=merged,
        check=check,
        text=True,
        capture_output=True,
    )


def git_out(cmd: list[str]) -> str:
    return run(cmd).stdout.strip()


def ensure_identity() -> tuple[str, str]:
    name = os.environ.get("GIT_AUTHOR_NAME") or git_out(["git", "config", "user.name"])
    email = os.environ.get("GIT_AUTHOR_EMAIL") or git_out(["git", "config", "user.email"])
    if not name or not email:
        sys.exit(
            "Set git user.name / user.email in this repo, or export "
            "GIT_AUTHOR_NAME and GIT_AUTHOR_EMAIL.\n"
            "Email must be one listed at https://github.com/settings/emails"
        )
    run(["git", "config", "user.name", name])
    run(["git", "config", "user.email", email])
    return name, email


def append_line(text: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(text.rstrip() + "\n")


def commit(message: str, when: dt.datetime | None = None) -> None:
    env: dict[str, str] = {}
    if when is not None:
        stamp = when.strftime("%Y-%m-%dT%H:%M:%S")
        env["GIT_AUTHOR_DATE"] = stamp
        env["GIT_COMMITTER_DATE"] = stamp
    run(["git", "add", str(LOG.relative_to(ROOT))])
    run(["git", "commit", "-m", message], env=env or None)


def already_committed_on(day: dt.date) -> bool:
    if not LOG.exists():
        return False
    needle = day.isoformat()
    return any(needle in line for line in LOG.read_text(encoding="utf-8").splitlines())


def push() -> None:
    run(["git", "push"])


def cmd_once(push_remote: bool) -> int:
    ensure_identity()
    today = dt.date.today()
    if already_committed_on(today):
        print(f"already have an entry for {today.isoformat()}, skip")
        return 0
    now = dt.datetime.now()
    line = f"{now.isoformat(timespec='seconds')} daily ping"
    append_line(line)
    commit(f"chore: daily ping {today.isoformat()}")
    print(f"committed {line}")
    if push_remote:
        push()
        print("pushed")
    return 0


def cmd_backfill(days: int, min_c: int, max_c: int, seed: int | None, push_remote: bool) -> int:
    if days < 1 or min_c < 1 or max_c < min_c:
        sys.exit("invalid --days / --min / --max")
    ensure_identity()
    rng = random.Random(seed)
    today = dt.date.today()
    made = 0
    for offset in range(days, 0, -1):
        day = today - dt.timedelta(days=offset)
        if already_committed_on(day):
            print(f"skip {day.isoformat()} (already in log)")
            continue
        n = rng.randint(min_c, max_c)
        for i in range(n):
            when = dt.datetime(
                day.year,
                day.month,
                day.day,
                rng.randint(9, 21),
                rng.randint(0, 59),
                rng.randint(0, 59),
            )
            line = f"{when.isoformat(timespec='seconds')} backfill {i + 1}/{n}"
            append_line(line)
            commit(f"chore: backfill {day.isoformat()} ({i + 1}/{n})", when=when)
            print(f"committed {line}")
            made += 1
    print(f"\ncreated {made} commits")
    if push_remote:
        push()
        print("pushed")
    else:
        print("review with: git log --pretty=fuller")
        print("then: python green.py once --push   (or git push)")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="GitHub daily / backfill commits")
    sub = p.add_subparsers(dest="cmd", required=True)

    once = sub.add_parser("once", help="commit today")
    once.add_argument("--push", action="store_true")

    bf = sub.add_parser("backfill", help="commit dated history")
    bf.add_argument("--days", type=int, default=180)
    bf.add_argument("--min", type=int, default=1, dest="min_c")
    bf.add_argument("--max", type=int, default=3, dest="max_c")
    bf.add_argument("--seed", type=int, default=None)
    bf.add_argument("--push", action="store_true")

    args = p.parse_args()
    if args.cmd == "once":
        return cmd_once(args.push)
    return cmd_backfill(args.days, args.min_c, args.max_c, args.seed, args.push)


if __name__ == "__main__":
    raise SystemExit(main())
