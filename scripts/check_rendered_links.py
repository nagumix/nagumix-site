"""Check local links, assets, and HTML anchors in a rendered Hugo output tree."""

from __future__ import annotations

import argparse
import posixpath
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit


TARGET_ATTRIBUTES = ("href", "src", "poster")
NON_HTTP_SCHEMES = {"data", "javascript", "mailto", "tel"}


@dataclass(frozen=True)
class Target:
    raw: str
    attribute: str


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.targets: list[Target] = []
        self.anchors: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        for attribute in TARGET_ATTRIBUTES:
            value = values.get(attribute)
            if value:
                self.targets.append(Target(value, attribute))
        anchor_id = values.get("id")
        if anchor_id:
            self.anchors.add(anchor_id)
        if tag == "a":
            anchor_name = values.get("name")
            if anchor_name:
                self.anchors.add(anchor_name)
        if tag == "meta" and values.get("http-equiv", "").lower() == "refresh":
            match = re.search(r"url\s*=\s*(.+)$", values.get("content", ""), re.IGNORECASE)
            if match:
                self.targets.append(Target(match.group(1).strip(" '\""), "refresh"))


def parsed_page(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser


def normalized_prefix(base_url: str) -> tuple[str, str, str]:
    base = urlsplit(base_url)
    if base.scheme not in {"http", "https"} or not base.netloc:
        raise ValueError("--base-url must be an absolute HTTP(S) URL")
    path = unquote(base.path or "/")
    if "\\" in path:
        raise ValueError("--base-url cannot contain backslashes")
    prefix = posixpath.normpath("/" + path.lstrip("/"))
    return base.scheme.lower(), base.netloc.lower(), "/" if prefix == "/" else prefix.rstrip("/") + "/"


def source_url(root: Path, source: Path, base_url: str) -> str:
    relative = source.relative_to(root).as_posix()
    if relative.endswith("/index.html"):
        relative = relative[: -len("index.html")]
    return urljoin(base_url.rstrip("/") + "/", relative)


def target_file(root: Path, target_path: str) -> Path | None:
    relative = target_path.lstrip("/")
    candidates = [root / relative]
    if target_path.endswith("/"):
        candidates.append(root / relative / "index.html")
    else:
        candidates.extend((root / relative / "index.html", root / f"{relative}.html"))
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved.is_relative_to(root) and resolved.is_file():
            return resolved
    return None


def check_output(root: Path, base_url: str) -> tuple[dict[str, int], list[str]]:
    root = root.resolve()
    scheme, host, prefix = normalized_prefix(base_url)
    pages = sorted(root.rglob("*.html"))
    anchors = {page.resolve(): parsed_page(page).anchors for page in pages}
    counts = {"html_files": len(pages), "targets": 0, "checked": 0, "ignored": 0}
    failures: list[str] = []

    for source in pages:
        page_url = source_url(root, source, base_url)
        for target in parsed_page(source).targets:
            counts["targets"] += 1
            parsed = urlsplit(target.raw)
            if parsed.scheme.lower() in NON_HTTP_SCHEMES:
                counts["ignored"] += 1
                continue
            if parsed.scheme and parsed.scheme.lower() not in {"http", "https"}:
                counts["ignored"] += 1
                continue
            if parsed.netloc and parsed.netloc.lower() != host:
                counts["ignored"] += 1
                continue
            resolved_url = urljoin(page_url, target.raw)
            resolved = urlsplit(resolved_url)
            if resolved.scheme.lower() != scheme or resolved.netloc.lower() != host:
                counts["ignored"] += 1
                continue
            decoded_path = unquote(resolved.path)
            if "\\" in decoded_path:
                failures.append(f"{page_url} -> {target.raw}: backslash paths are unsupported")
                continue
            normalized_path = posixpath.normpath("/" + decoded_path.lstrip("/"))
            if resolved.path.endswith("/") and not normalized_path.endswith("/"):
                normalized_path += "/"
            if prefix != "/" and not normalized_path.startswith(prefix):
                failures.append(f"{page_url} -> {target.raw}: escapes deployment prefix {prefix}")
                continue
            output_path = normalized_path if prefix == "/" else normalized_path[len(prefix) - 1 :]
            file_path = target_file(root, output_path)
            counts["checked"] += 1
            if file_path is None:
                failures.append(f"{page_url} -> {target.raw}: target file not found")
                continue
            fragment = unquote(resolved.fragment)
            if fragment:
                if file_path.suffix.lower() != ".html":
                    failures.append(f"{page_url} -> {target.raw}: fragment target is not HTML")
                elif fragment not in anchors.get(file_path, set()):
                    failures.append(f"{page_url} -> {target.raw}: fragment #{fragment} not found")
    return counts, failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="rendered site output directory")
    parser.add_argument("--base-url", required=True, help="deployment URL used for the build")
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error(f"output root does not exist: {args.root}")
    counts, failures = check_output(args.root, args.base_url)
    print(f"html_files={counts['html_files']}")
    print(f"total_targets={counts['targets']}")
    print(f"checked_targets={counts['checked']}")
    print(f"ignored_targets={counts['ignored']}")
    print(f"failures={len(failures)}")
    for failure in failures:
        print(f"FAIL {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
