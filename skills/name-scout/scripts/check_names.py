#!/usr/bin/env python3
"""Check candidate names across common registries and public search APIs.

Uses only the Python standard library. Results are discovery evidence, not legal
clearance or a guarantee that a name can be registered.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import dataclasses
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable, Iterable


USER_AGENT = "name-scout/1.0 (name collision research)"
DEFAULT_CHECKS = ("npm", "pypi", "crates", "github", "domains", "steam", "wikipedia")
STATUSES = {"CLEAR", "TAKEN", "RELATED", "UNKNOWN"}


@dataclasses.dataclass(frozen=True)
class Result:
    candidate: str
    check: str
    queried: str
    status: str
    detail: str
    url: str

    def __post_init__(self) -> None:
        if self.status not in STATUSES:
            raise ValueError(f"invalid status: {self.status}")


@dataclasses.dataclass(frozen=True)
class Response:
    status: int
    data: Any
    url: str


def package_slug(value: str) -> str:
    value = value.strip().lower().replace("&", " and ")
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    return re.sub(r"[-_.]+", "-", value).strip("-")


def display_key(value: str) -> str:
    return "".join(character for character in value.casefold() if character.isalnum())


def invalid_spelling(candidate: str, check: str) -> list[Result]:
    return [
        Result(
            candidate,
            check,
            "",
            "UNKNOWN",
            "candidate has no ASCII package spelling",
            "",
        )
    ]


def request_json(url: str, timeout: float, headers: dict[str, str] | None = None) -> Response:
    request_headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    if headers:
        request_headers.update(headers)
    request = urllib.request.Request(url, headers=request_headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            data = json.loads(raw.decode("utf-8")) if raw else None
            return Response(response.status, data, response.geturl())
    except urllib.error.HTTPError as error:
        raw = error.read()
        try:
            data = json.loads(raw.decode("utf-8")) if raw else None
        except (UnicodeDecodeError, json.JSONDecodeError):
            data = None
        return Response(error.code, data, error.geturl())


def registry_result(
    candidate: str,
    check: str,
    queried: str,
    url: str,
    timeout: float,
    headers: dict[str, str] | None = None,
) -> Result:
    try:
        response = request_json(url, timeout, headers)
    except (OSError, TimeoutError, json.JSONDecodeError) as error:
        return Result(candidate, check, queried, "UNKNOWN", type(error).__name__, url)
    if response.status == 200:
        return Result(candidate, check, queried, "TAKEN", "exact registry entry exists", response.url)
    if response.status == 404:
        return Result(candidate, check, queried, "CLEAR", "no exact registry entry found", url)
    return Result(candidate, check, queried, "UNKNOWN", f"HTTP {response.status}", url)


def check_npm(candidate: str, timeout: float) -> list[Result]:
    name = package_slug(candidate)
    if not name:
        return invalid_spelling(candidate, "npm")
    url = "https://registry.npmjs.org/" + urllib.parse.quote(name, safe="")
    return [registry_result(candidate, "npm", name, url, timeout)]


def check_pypi(candidate: str, timeout: float) -> list[Result]:
    name = package_slug(candidate)
    if not name:
        return invalid_spelling(candidate, "pypi")
    url = f"https://pypi.org/pypi/{urllib.parse.quote(name, safe='')}/json"
    return [registry_result(candidate, "pypi", name, url, timeout)]


def check_crates(candidate: str, timeout: float) -> list[Result]:
    primary = package_slug(candidate)
    if not primary:
        return invalid_spelling(candidate, "crates.io")
    variants = [primary]
    alternate = primary.replace("-", "_")
    if alternate != primary:
        variants.append(alternate)
    results = []
    for name in variants:
        url = f"https://crates.io/api/v1/crates/{urllib.parse.quote(name, safe='')}"
        results.append(registry_result(candidate, "crates.io", name, url, timeout))
    return results


def check_github(candidate: str, timeout: float) -> list[Result]:
    name = package_slug(candidate)
    if not name:
        return invalid_spelling(candidate, "github")
    query = urllib.parse.urlencode({"q": f'"{name}" in:name', "per_page": 20})
    url = "https://api.github.com/search/repositories?" + query
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        response = request_json(url, timeout, headers)
    except (OSError, TimeoutError, json.JSONDecodeError) as error:
        return [Result(candidate, "github", name, "UNKNOWN", type(error).__name__, url)]
    if response.status != 200 or not isinstance(response.data, dict):
        return [Result(candidate, "github", name, "UNKNOWN", f"HTTP {response.status}", url)]
    items = response.data.get("items", [])
    exact = [item for item in items if str(item.get("name", "")).casefold() == name.casefold()]
    if exact:
        stars = max(int(item.get("stargazers_count", 0)) for item in exact)
        return [Result(candidate, "github", name, "TAKEN", f"{len(exact)} exact repo name(s); max {stars} stars", url)]
    if items:
        return [Result(candidate, "github", name, "RELATED", f"{len(items)} nearby repo result(s)", url)]
    return [Result(candidate, "github", name, "CLEAR", "no matching repository names found", url)]


def check_domains(candidate: str, timeout: float) -> list[Result]:
    label = package_slug(candidate)
    results = []
    if not label or len(label.encode("idna")) > 63:
        return [Result(candidate, "domain", label, "UNKNOWN", "invalid DNS label", "")]
    for suffix in ("com", "net", "io"):
        domain = f"{label}.{suffix}"
        url = "https://rdap.org/domain/" + domain
        try:
            response = request_json(url, timeout)
        except (OSError, TimeoutError, json.JSONDecodeError) as error:
            results.append(Result(candidate, "domain", domain, "UNKNOWN", type(error).__name__, url))
            continue
        if response.status == 200:
            status, detail = "TAKEN", "RDAP registration exists"
        elif response.status == 404:
            status, detail = "CLEAR", "no RDAP registration found; confirm with registrar"
        else:
            status, detail = "UNKNOWN", f"HTTP {response.status}"
        results.append(Result(candidate, "domain", domain, status, detail, response.url))
    return results


def check_steam(candidate: str, timeout: float) -> list[Result]:
    query = urllib.parse.urlencode({"term": candidate, "l": "english", "cc": "US"})
    url = "https://store.steampowered.com/api/storesearch/?" + query
    try:
        response = request_json(url, timeout)
    except (OSError, TimeoutError, json.JSONDecodeError) as error:
        return [Result(candidate, "steam", candidate, "UNKNOWN", type(error).__name__, url)]
    if response.status != 200 or not isinstance(response.data, dict):
        return [Result(candidate, "steam", candidate, "UNKNOWN", f"HTTP {response.status}", url)]
    items = response.data.get("items") or []
    exact = [item for item in items if display_key(str(item.get("name", ""))) == display_key(candidate)]
    if exact:
        return [Result(candidate, "steam", candidate, "TAKEN", f"{len(exact)} exact title(s)", url)]
    if items:
        return [Result(candidate, "steam", candidate, "RELATED", f"{len(items)} nearby title(s)", url)]
    return [Result(candidate, "steam", candidate, "CLEAR", "no title result found", url)]


def check_wikipedia(candidate: str, timeout: float) -> list[Result]:
    params = {
        "action": "query",
        "list": "search",
        "srsearch": f'intitle:"{candidate}"',
        "srlimit": 10,
        "format": "json",
        "origin": "*",
    }
    url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
    try:
        response = request_json(url, timeout)
    except (OSError, TimeoutError, json.JSONDecodeError) as error:
        return [Result(candidate, "wikipedia", candidate, "UNKNOWN", type(error).__name__, url)]
    if response.status != 200 or not isinstance(response.data, dict):
        return [Result(candidate, "wikipedia", candidate, "UNKNOWN", f"HTTP {response.status}", url)]
    items = response.data.get("query", {}).get("search", [])
    exact = [item for item in items if display_key(str(item.get("title", ""))) == display_key(candidate)]
    if exact:
        return [Result(candidate, "wikipedia", candidate, "TAKEN", f"{len(exact)} exact article title(s)", url)]
    if items:
        titles = ", ".join(str(item.get("title", "")) for item in items[:3])
        return [Result(candidate, "wikipedia", candidate, "RELATED", f"nearby: {titles}", url)]
    return [Result(candidate, "wikipedia", candidate, "CLEAR", "no article-title result found", url)]


CHECKERS: dict[str, Callable[[str, float], list[Result]]] = {
    "npm": check_npm,
    "pypi": check_pypi,
    "crates": check_crates,
    "github": check_github,
    "domains": check_domains,
    "steam": check_steam,
    "wikipedia": check_wikipedia,
}


def run_checks(names: Iterable[str], checks: Iterable[str], timeout: float, workers: int) -> list[Result]:
    names = list(names)
    tasks = [(name, check, CHECKERS[check]) for name in names for check in checks]
    results: list[Result] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(checker, name, timeout): (name, check)
            for name, check, checker in tasks
        }
        for future in concurrent.futures.as_completed(futures):
            name, check = futures[future]
            try:
                results.extend(future.result())
            except Exception as error:  # Keep one broken integration from hiding other evidence.
                results.append(Result(name, check, name, "UNKNOWN", f"unexpected {type(error).__name__}", ""))
    order = {name: index for index, name in enumerate(names)}
    checks_order = {check: idx for idx, check in enumerate(checks)}

    def sort_key(item: Result) -> tuple[int, int, str]:
        check_name = "domains" if item.check == "domain" else ("crates" if item.check == "crates.io" else item.check)
        return (order[item.candidate], checks_order.get(check_name, 99), item.queried)

    return sorted(results, key=sort_key)


def target_column(check: str, queried: str) -> str:
    if check == "domain":
        for suffix in (".com", ".net", ".io"):
            if queried.endswith(suffix):
                return suffix
        return "domain"
    if check == "crates.io":
        return "crates"
    return check


def get_ordered_columns(checks: Iterable[str]) -> list[str]:
    cols: list[str] = []
    for check in checks:
        if check == "domains":
            cols.extend([".com", ".net", ".io"])
        elif check == "crates":
            cols.append("crates")
        else:
            cols.append(check)
    return cols


STATUS_PRECEDENCE = {"TAKEN": 4, "RELATED": 3, "UNKNOWN": 2, "CLEAR": 1}


def aggregate_status(results: list[Result]) -> str:
    if not results:
        return "-"
    highest = max(results, key=lambda r: STATUS_PRECEDENCE.get(r.status, 0))
    return highest.status


def print_single_name(results: list[Result], candidate: str, checked_at: str) -> None:
    crates = [r for r in results if r.check == "crates.io"]
    collapse_crates = len(crates) > 1 and len({(r.status, r.detail) for r in crates}) == 1

    rows: list[tuple[str, str, str]] = []
    seen_crates = False
    for r in results:
        if r.check == "crates.io":
            if collapse_crates:
                if not seen_crates:
                    rows.append(("crates.io", r.status, r.detail))
                    seen_crates = True
                continue
            else:
                rows.append((f"crates.io ({r.queried})", r.status, r.detail))
                continue
        target = target_column(r.check, r.queried)
        rows.append((target, r.status, r.detail))

    headers = ("TARGET", "STATUS", "DETAIL")
    widths = {
        "TARGET": max(len("TARGET"), max((len(r[0]) for r in rows), default=0)),
        "STATUS": max(len("STATUS"), max((len(r[1]) for r in rows), default=0)),
        "DETAIL": max(len("DETAIL"), max((len(r[2]) for r in rows), default=0)),
    }
    widths["DETAIL"] = min(60, widths["DETAIL"])

    print(f'Availability for: "{candidate}"')
    print(f"Checked at {checked_at}\n")
    print(f"{headers[0].ljust(widths['TARGET'])}  {headers[1].ljust(widths['STATUS'])}  {headers[2].ljust(widths['DETAIL'])}")
    print(f"{'-' * widths['TARGET']}  {'-' * widths['STATUS']}  {'-' * widths['DETAIL']}")
    for target, status, detail in rows:
        print(f"{target.ljust(widths['TARGET'])}  {status.ljust(widths['STATUS'])}  {detail[:widths['DETAIL']].ljust(widths['DETAIL'])}")
    print("\nCLEAR means no exact result was found at check time; it is not trademark or registration clearance.")


def print_matrix(results: list[Result], names: list[str], checks: Iterable[str], checked_at: str) -> None:
    columns = get_ordered_columns(checks)

    grid: dict[str, dict[str, list[Result]]] = {name: {col: [] for col in columns} for name in names}
    for r in results:
        col = target_column(r.check, r.queried)
        if r.candidate in grid and col in grid[r.candidate]:
            grid[r.candidate][col].append(r)

    matrix_cells: dict[str, dict[str, str]] = {}
    for name in names:
        matrix_cells[name] = {}
        for col in columns:
            matrix_cells[name][col] = aggregate_status(grid[name][col])

    name_col_width = max(len("NAME"), max(len(name) for name in names))
    col_widths = {col: max(len(col), max(len(matrix_cells[name][col]) for name in names)) for col in columns}

    print(f"Checked at {checked_at}\n")

    header_title = "NAME".ljust(name_col_width) + "  " + "  ".join(col.ljust(col_widths[col]) for col in columns)
    separator_line = ("-" * name_col_width) + "  " + "  ".join("-" * col_widths[col] for col in columns)

    print(header_title)
    print(separator_line)

    for name in names:
        row_str = name.ljust(name_col_width) + "  " + "  ".join(matrix_cells[name][col].ljust(col_widths[col]) for col in columns)
        print(row_str)

    notes: list[str] = []
    for name in names:
        item_notes = []
        for col in columns:
            col_results = grid[name][col]
            for r in col_results:
                if r.status in ("TAKEN", "RELATED"):
                    item_notes.append(f"{col} ({r.detail})")
        if item_notes:
            notes.append(f"  - {name}: {', '.join(item_notes)}")

    if notes:
        print("\nCollisions & notes:")
        for note in notes:
            print(note)

    print("\nCLEAR means no exact result was found at check time; it is not trademark or registration clearance.")


def print_table(results: list[Result], checked_at: str) -> None:
    columns = ("candidate", "check", "queried", "status", "detail")
    widths = {
        column: min(52, max(len(column), *(len(str(getattr(item, column))) for item in results)))
        for column in columns
    }
    print(f"Checked at {checked_at}")
    print("  ".join(column.upper().ljust(widths[column]) for column in columns))
    print("  ".join("-" * widths[column] for column in columns))
    for item in results:
        values = [str(getattr(item, column)) for column in columns]
        print("  ".join(value[: widths[column]].ljust(widths[column]) for column, value in zip(columns, values)))
    print("\nCLEAR means no exact result was found at check time; it is not trademark or registration clearance.")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("names", nargs="*", help="candidate names; reads non-empty stdin lines when omitted")
    parser.add_argument(
        "--checks",
        nargs="+",
        choices=tuple(CHECKERS),
        default=list(DEFAULT_CHECKS),
        help="checks to run (default: all)",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--matrix", action="store_true", help="force matrix view even for a single candidate")
    parser.add_argument("--detail", action="store_true", help="show detailed multi-row list instead of matrix")
    parser.add_argument("--timeout", type=float, default=8.0, help="per-request timeout in seconds")
    parser.add_argument("--workers", type=int, default=8, help="maximum concurrent checks")
    args = parser.parse_args(argv)
    if not args.names and not sys.stdin.isatty():
        args.names = [line.strip() for line in sys.stdin if line.strip()]
    args.names = list(dict.fromkeys(name.strip() for name in args.names if name.strip()))
    if not args.names:
        parser.error("provide at least one candidate name")
    if len(args.names) > 25:
        parser.error("limit one run to 25 candidates to respect public services")
    if args.timeout <= 0 or not 1 <= args.workers <= 32:
        parser.error("timeout must be positive and workers must be between 1 and 32")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    checked_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    results = run_checks(args.names, args.checks, args.timeout, args.workers)
    if args.json:
        payload = {
            "checked_at": checked_at,
            "disclaimer": "Discovery evidence only; CLEAR is not legal or registration clearance.",
            "results": [dataclasses.asdict(item) for item in results],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif args.detail:
        print_table(results, checked_at)
    elif len(args.names) == 1 and not args.matrix:
        print_single_name(results, args.names[0], checked_at)
    else:
        print_matrix(results, args.names, args.checks, checked_at)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
