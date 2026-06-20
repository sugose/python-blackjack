"""JSONL viewer CLI for blackjack session files (ICE-2)."""

import argparse
import glob
import json
import re
import sys
from typing import Any

from src.logger import GameEvent, _hrf

VERSION = "1.0.0"

# Maps lowercase filter field names to actual JSON payload field names
_FIELD_MAP: dict[str, str] = {
    "eventtype": "eventType",
    "sessionid": "sessionId",
    "handid": "handId",
    "actor": "actor",
    "timestamp": "timestamp",
    "eventid": "eventId",
}
_UUID_FIELDS: frozenset[str] = frozenset({"sessionid", "handid", "eventid"})

_COND_RE = re.compile(r"^([a-zA-Z]+)(~=|!=|=)(.+)$")
_TOKEN_RE = re.compile(r"\s*(?:(\(|\))|(\bAND\b|\bOR\b)|([^\s()]+))", re.IGNORECASE)


def _tokenize(expr: str) -> list[str]:
    tokens = []
    for m in _TOKEN_RE.finditer(expr):
        if m.group(1):
            tokens.append(m.group(1))
        elif m.group(2):
            tokens.append(m.group(2).upper())
        elif m.group(3):
            tokens.append(m.group(3))
    return tokens


class _Parser:
    def __init__(self, tokens: list[str]) -> None:
        self._tokens = tokens
        self._pos = 0

    def parse(self) -> tuple:
        """Parse the full token list and return an AST node."""
        if not self._tokens:
            raise ValueError("Empty filter expression")
        node = self._expr()
        if self._pos < len(self._tokens):
            raise ValueError(f"Unexpected token: {self._tokens[self._pos]!r}")
        return node

    def _expr(self) -> tuple:
        left = self._term()
        while self._pos < len(self._tokens) and self._tokens[self._pos] == "OR":
            self._pos += 1
            right = self._term()
            left = ("OR", left, right)
        return left

    def _term(self) -> tuple:
        left = self._factor()
        while self._pos < len(self._tokens) and self._tokens[self._pos] == "AND":
            self._pos += 1
            right = self._factor()
            left = ("AND", left, right)
        return left

    def _factor(self) -> tuple:
        if self._pos < len(self._tokens) and self._tokens[self._pos] == "(":
            self._pos += 1
            node = self._expr()
            if self._pos >= len(self._tokens) or self._tokens[self._pos] != ")":
                raise ValueError("Expected closing parenthesis ')'")
            self._pos += 1
            return node
        return self._comparison()

    def _comparison(self) -> tuple:
        if self._pos >= len(self._tokens):
            raise ValueError("Expected comparison expression")
        token = self._tokens[self._pos]
        self._pos += 1
        m = _COND_RE.match(token)
        if not m:
            raise ValueError(
                f"Invalid comparison: {token!r}. "
                "Expected FIELD=VALUE, FIELD!=VALUE, or FIELD~=VALUE"
            )
        field_raw, op, value = m.group(1), m.group(2), m.group(3)
        field = field_raw.lower()
        if field not in _FIELD_MAP:
            known = ", ".join(sorted(_FIELD_MAP))
            raise ValueError(f"Unknown filter field: {field_raw!r}. Known fields: {known}")
        return ("CMP", field, op, value)


def parse_filter(expr: str) -> tuple:
    """Parse a filter expression string into an AST node.

    Raises ValueError on parse error or unknown field.
    """
    return _Parser(_tokenize(expr)).parse()


def match_event(event: dict[str, Any], node: tuple) -> bool:
    """Evaluate a filter AST node against a JSONL event dict."""
    kind = node[0]
    if kind == "AND":
        return match_event(event, node[1]) and match_event(event, node[2])
    if kind == "OR":
        return match_event(event, node[1]) or match_event(event, node[2])

    # CMP node: ("CMP", field_lower, op, value)
    _, field, op, value = node
    actual_key = _FIELD_MAP[field]
    raw = event.get(actual_key)
    if raw is None:
        return op == "!="

    raw_lower = str(raw).lower()
    value_lower = value.lower()

    if field == "actor":
        if op == "=":
            if value_lower == "player":
                return raw_lower != "dealer"
            if value_lower == "dealer":
                return raw_lower == "dealer"
            return raw_lower == value_lower
        if op == "!=":
            if value_lower == "player":
                return raw_lower == "dealer"
            if value_lower == "dealer":
                return raw_lower != "dealer"
            return raw_lower != value_lower
        # ~= falls through to generic handler below

    if op == "=":
        if field in _UUID_FIELDS:
            return raw_lower.endswith(value_lower)
        return raw_lower == value_lower
    if op == "!=":
        if field in _UUID_FIELDS:
            return not raw_lower.endswith(value_lower)
        return raw_lower != value_lower
    if op == "~=":
        return value_lower in raw_lower

    return False  # unreachable — _COND_RE only allows these three operators


def _event_to_hrf(payload: dict[str, Any]) -> str:
    """Reconstruct a GameEvent from a JSONL payload and render it as HRF."""
    evt = GameEvent(
        eventType=payload["eventType"],
        sessionId=payload["sessionId"],
        data=payload.get("data", {}),
        handId=payload.get("handId"),
        actor=payload.get("actor"),
        eventId=payload["eventId"],
        timestamp=payload["timestamp"],
    )
    return _hrf(evt)


class _HelpOnErrorParser(argparse.ArgumentParser):
    """ArgumentParser that prints help to stderr and exits 1 on any argument error."""

    def error(self, message: str) -> None:
        print(f"Error: {message}", file=sys.stderr)
        self.print_help(sys.stderr)
        sys.exit(1)


_EPILOG = """\
Filterable fields:
  eventType   Event type string (e.g. BetPlaced, CardDealt)
  sessionId   Session UUID — implicit suffix match (e.g. sessionId=b7c19a2d)
  handId      Hand UUID — implicit suffix match; absent on session-level events
  actor       'player' = any non-dealer; 'dealer' = Dealer only;
              any other value = literal case-insensitive match
  timestamp   ISO-8601 UTC timestamp string
  eventId     Event UUID — implicit suffix match

Operators: = (equality / UUID suffix match), != (not-equal), ~= (contains)
Logical:   AND, OR (case-insensitive), parentheses for grouping

Examples:
  --filter "eventType=BetPlaced"
  --filter "eventType=BetPlaced AND actor=player"
  --filter "(eventType=CardDealt OR eventType=CardDrawn) AND actor=dealer"
  --filter "sessionId=b7c19a2d"
  --filter "eventType!=SessionOpened AND actor!=dealer"
"""


def _build_parser() -> _HelpOnErrorParser:
    parser = _HelpOnErrorParser(
        prog="python -m src.viewer",
        description="Inspect blackjack session JSONL files.",
        epilog=_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument(
        "--filter",
        metavar="EXPRESSION",
        help="SQL-like filter expression (see below for fields and operators)",
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="JSONL session files or glob patterns (expanded cross-platform by the viewer)",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    """Entry point for the JSONL viewer CLI."""
    if argv is None:
        argv = sys.argv[1:]

    parser = _build_parser()

    if not argv:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args(argv)

    filter_node: tuple | None = None
    if args.filter:
        try:
            filter_node = parse_filter(args.filter)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            parser.print_help(sys.stderr)
            sys.exit(1)

    if not args.files:
        parser.print_help()
        sys.exit(0)

    # Expand globs; viewer handles expansion cross-platform
    resolved: list[str] = []
    for pattern in args.files:
        matches = sorted(glob.glob(pattern, recursive=True))
        if not matches:
            print(f"Error: No files matched: {pattern!r}", file=sys.stderr)
            parser.print_help(sys.stderr)
            sys.exit(2)
        resolved.extend(matches)

    # Deduplicate while preserving order
    seen: set[str] = set()
    resolved = [p for p in resolved if not (p in seen or seen.add(p))]

    # Read all events from all resolved files
    events: list[dict[str, Any]] = []
    for filepath in resolved:
        try:
            with open(filepath, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        try:
                            events.append(json.loads(line))
                        except json.JSONDecodeError as exc:
                            print(
                                f"Warning: skipping malformed line in {filepath!r}: {exc}",
                                file=sys.stderr,
                            )
        except OSError as exc:
            print(f"Error: Cannot read {filepath!r}: {exc}", file=sys.stderr)
            parser.print_help(sys.stderr)
            sys.exit(2)

    # Note: all events buffered in memory for chronological sort — large files may be slow.
    events.sort(key=lambda e: e.get("timestamp", ""))

    for event in events:
        if filter_node is None or match_event(event, filter_node):
            try:
                print(_event_to_hrf(event))
            except (KeyError, TypeError) as exc:
                print(f"Warning: skipping malformed event (missing field: {exc})", file=sys.stderr)


if __name__ == "__main__":
    main()
