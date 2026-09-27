"""Build one complete GitLab Pages snapshot containing stable and branch sites."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable
from urllib.parse import urlsplit


@dataclass(frozen=True)
class BranchTip:
    name: str
    sha: str


@dataclass(frozen=True)
class BuildRequest:
    branch: str
    sha: str
    destination: Path
    base_url: str
    stable: bool = False


BuildGroup = Callable[[str, list[BuildRequest]], None]


def branch_path(ref_name: str) -> str:
    """Return a readable, deterministic path with a digest of the full ref name."""
    ascii_name = unicodedata.normalize("NFKD", ref_name).encode("ascii", "ignore").decode()
    readable = re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-")
    readable = readable[:40].rstrip("-") or "branch"
    digest = hashlib.sha256(ref_name.encode("utf-8")).hexdigest()[:12]
    return f"{readable}-{digest}"


def normalized_pages_url(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("--pages-url must be an absolute HTTP(S) URL")
    if parsed.query or parsed.fragment:
        raise ValueError("--pages-url cannot contain a query or fragment")
    return value.rstrip("/")


def run(args: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> str:
    print("+", subprocess.list2cmdline(args), flush=True)
    completed = subprocess.run(
        args,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if completed.stdout:
        print(completed.stdout, end="", flush=True)
    completed.check_returncode()
    return completed.stdout


def refresh_remote_refs(repository: Path, remote: str, ref_prefix: str) -> None:
    refspec = f"+refs/heads/*:{ref_prefix}*"
    run(["git", "fetch", "--force", "--prune", remote, refspec], cwd=repository)


def read_branch_tips(repository: Path, ref_prefix: str) -> list[BranchTip]:
    output = run(
        ["git", "for-each-ref", "--format=%(refname)%00%(objectname)", ref_prefix],
        cwd=repository,
    )
    tips: list[BranchTip] = []
    for line in output.splitlines():
        ref, separator, sha = line.partition("\0")
        if not separator or not ref.startswith(ref_prefix):
            raise RuntimeError(f"unexpected branch record: {line!r}")
        name = ref[len(ref_prefix) :]
        if not name or name == "HEAD":
            continue
        tips.append(BranchTip(name=name, sha=sha))
    return sorted(tips, key=lambda tip: tip.name.encode("utf-8"))


def _write_branch_index(root: Path, pages_url: str, tips: list[BranchTip]) -> None:
    branch_rows = []
    manifest_branches = []
    for tip in tips:
        path = branch_path(tip.name)
        url = f"{pages_url}/branches/{path}/"
        branch_rows.append(
            "<li><a href=\"{url}\"><code>{name}</code></a> "
            "<small><code>{sha}</code></small></li>".format(
                url=html.escape(url, quote=True),
                name=html.escape(tip.name),
                sha=html.escape(tip.sha),
            )
        )
        manifest_branches.append(
            {"ref": tip.name, "sha": tip.sha, "path": path, "url": url}
        )

    index = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="robots" content="noindex, nofollow">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>NaguMIX branch sites</title>
</head>
<body>
  <main>
    <h1>NaguMIX branch sites</h1>
    <p>This index represents one coherent snapshot of the repository branches.</p>
    <ul>
      {rows}
    </ul>
  </main>
</body>
</html>
""".format(rows="\n      ".join(branch_rows))
    branches_root = root / "branches"
    branches_root.mkdir()
    (branches_root / "index.html").write_text(index, encoding="utf-8", newline="\n")

    main_tip = next(tip for tip in tips if tip.name == "main")
    manifest = {
        "pages_url": pages_url,
        "stable": {"ref": "main", "sha": main_tip.sha, "url": f"{pages_url}/"},
        "branches": manifest_branches,
    }
    (branches_root / "snapshot.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_snapshot(
    output: Path,
    pages_url: str,
    tips: Iterable[BranchTip],
    build_group: BuildGroup,
) -> None:
    """Atomically replace output with a complete root plus branch snapshot."""
    pages_url = normalized_pages_url(pages_url)
    tips = list(tips)
    if not tips:
        raise RuntimeError("no branch tips found")
    by_name = {tip.name: tip for tip in tips}
    if len(by_name) != len(tips):
        raise RuntimeError("duplicate branch names found")
    if "main" not in by_name:
        raise RuntimeError("stable branch main is missing")

    paths = [branch_path(tip.name) for tip in tips]
    if len(paths) != len(set(paths)):
        raise RuntimeError("branch URL collision after slug and digest mapping")

    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = output.with_name(f".{output.name}-next")
    backup = output.with_name(f".{output.name}-previous")
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir()
    try:
        main_tip = by_name["main"]
        build_group(
            main_tip.sha,
            [BuildRequest("main", main_tip.sha, staging, f"{pages_url}/", stable=True)],
        )
        if not (staging / "index.html").is_file():
            raise RuntimeError("stable build did not produce index.html")
        if (staging / "branches").exists():
            raise RuntimeError("stable build uses reserved output path: branches/")

        _write_branch_index(staging, pages_url, tips)
        requests_by_sha: dict[str, list[BuildRequest]] = defaultdict(list)
        for tip in tips:
            path = branch_path(tip.name)
            requests_by_sha[tip.sha].append(
                BuildRequest(
                    tip.name,
                    tip.sha,
                    staging / "branches" / path,
                    f"{pages_url}/branches/{path}/",
                )
            )
        for sha, requests in requests_by_sha.items():
            build_group(sha, requests)
            for request in requests:
                if not (request.destination / "index.html").is_file():
                    raise RuntimeError(f"branch build did not produce index.html: {request.branch}")

        if backup.exists():
            shutil.rmtree(backup)
        if output.exists():
            output.rename(backup)
        try:
            staging.rename(output)
        except Exception:
            if backup.exists() and not output.exists():
                backup.rename(output)
            raise
        if backup.exists():
            shutil.rmtree(backup)
    finally:
        if staging.exists():
            shutil.rmtree(staging)


class HugoBuilder:
    def __init__(self, repository: Path) -> None:
        self.repository = repository.resolve()
        self.checker = self.repository / "scripts" / "check_rendered_links.py"

    def __call__(self, sha: str, requests: list[BuildRequest]) -> None:
        with tempfile.TemporaryDirectory(prefix="nagumix-pages-source-") as directory:
            temporary = Path(directory)
            archive_path = temporary / "source.tar"
            source = temporary / "source"
            source.mkdir()
            run(
                ["git", "archive", "--format=tar", "--output", str(archive_path), sha],
                cwd=self.repository,
            )
            with tarfile.open(archive_path) as archive:
                archive.extractall(source, filter="data")

            module_files = [source / "go.mod", source / "go.sum"]
            before = {path.name: path.read_bytes() for path in module_files}
            env = os.environ.copy()
            run(["go", "mod", "download"], cwd=source, env=env)
            run(["go", "mod", "verify"], cwd=source, env=env)
            run(["hugo", "mod", "tidy", "--environment", "production"], cwd=source, env=env)
            for path in module_files:
                if path.read_bytes() != before[path.name]:
                    raise RuntimeError(f"Hugo module tidy changed {path.name} at {sha}")
            run(
                ["go", "list", "-m", "-f", "{{.Path}} {{.Version}}", "github.com/pgsty/oink"],
                cwd=source,
                env=env,
            )

            for request in requests:
                request.destination.mkdir(parents=True, exist_ok=True)
                print(
                    f"BUILD ref={request.branch!r} sha={request.sha} url={request.base_url}",
                    flush=True,
                )
                run(
                    [
                        "hugo",
                        "--cleanDestinationDir",
                        "--gc",
                        "--minify",
                        "--environment",
                        "production",
                        "--printPathWarnings",
                        "--panicOnWarning",
                        "--baseURL",
                        request.base_url,
                        "--destination",
                        str(request.destination),
                    ],
                    cwd=source,
                    env=env,
                )
                run(
                    [
                        "python3" if os.name != "nt" else "python",
                        str(self.checker),
                        str(request.destination),
                        "--base-url",
                        request.base_url,
                    ],
                    cwd=source,
                    env=env,
                )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pages-url", required=True)
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--ref-prefix", default="refs/remotes/pages/")
    parser.add_argument("--skip-fetch", action="store_true")
    args = parser.parse_args()

    repository = args.repository.resolve()
    if not args.skip_fetch:
        refresh_remote_refs(repository, args.remote, args.ref_prefix)
    tips = read_branch_tips(repository, args.ref_prefix)
    print(f"SNAPSHOT branches={len(tips)}", flush=True)
    for tip in tips:
        print(f"REF {tip.name!r} {tip.sha} {branch_path(tip.name)}", flush=True)
    build_snapshot(args.output, args.pages_url, tips, HugoBuilder(repository))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
