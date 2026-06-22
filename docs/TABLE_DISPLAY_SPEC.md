# Table Display Layer — Specification

## Overview

A local web-based display that renders the blackjack table state in real time
during a session. Starts automatically when `python -m src.play` runs. The
terminal remains the input channel for human decisions; the browser is
display-only.

## Architecture

- Small HTTP server using stdlib `http.server`, started in a background thread
- Serves a single HTML page on a free port (default 8765, configurable)
- Page polls a `/events` endpoint every second
- Server reads the session JSONL file and streams events to the page
- `webbrowser.open()` called automatically on session start
- Server shuts down cleanly when the session ends
- `--no-display` flag disables the server entirely (headless/CI use)

## Launch flow

1. `python -m src.play --players ...` invoked
2. HTTP server starts on port 8765 (or next available port)
3. Browser tab opens automatically via `webbrowser.open()`
4. Game session starts in terminal
5. Browser polls `/events` endpoint, renders table state
6. Session ends → server thread stopped

## Module

`src/display.py` — `TableDisplay` class

```python
class TableDisplay:
    def __init__(self, session_file: Path, port: int = 8765) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
```

`start()` launches the HTTP server in a daemon thread and opens the browser.
`stop()` signals the server to shut down.

Called from `src/play.py` `main()` unless `--no-display` flag is set.

## HTTP endpoints

| Endpoint | Method | Response |
|---|---|---|
| `/` | GET | Single HTML page (inline CSS + JS) |
| `/events` | GET | JSON array of all events from session JSONL so far |

## Display — layout

### Table info bar (top, full width)
Horizontal strip showing: table ID, hand number (X of Y), seats occupied/total,
min/max bet, decks, BJ payout, soft 17 rule, cards remaining, cards drawn.

Cards remaining and drawn derived from `ShoeShuffled` (total) and counting
`CardDealt` + `CardDrawn` events.

### Dealer area (centered below info bar)
Large cards (56×78px). Hole card shown as face-down pattern until
`HoleCardRevealed` event. Hand value shown below cards.

### Player seats (row below dealer)
One seat per player. Empty seats togglable via checkbox (default: shown).

**Each seat shows:**
- Seat number badge (S1, S2, ... S7) — top left corner
- Player name
- Chip stack — stacked chip graphic, height proportional to wallet
- Bet stack — separate smaller stack in front, shown when bet is placed
- Cards — rank + suit symbol (♥♦♣♠), red for hearts/diamonds
- Hand value below cards
- Latest drawn card — gold outline + small gold dot (non-active players only)

**Seat states:**

| State | Border | Background | Card area |
|---|---|---|---|
| Waiting | transparent | dark | cards shown |
| Active (bot) | gold | gold tint | cards shown, no buttons |
| Active (human) | gold | gold tint | cards shown + Hit/Stand buttons |
| Stood | transparent | dark | cards shown, "— stood" on value |
| BUST | red | red tint, dimmed | cards cleared, BUST badge |
| BLACKJACK | gold | gold tint | cards cleared, BLACKJACK badge |

Hit/Stand buttons appear only on human-strategy seats when active.
Bot seats show gold highlight only — no buttons.
If multiple human seats at the table, buttons appear on whichever is currently active.

## Chip denominations

| Colour | Value |
|---|---|
| White | 1 UoM |
| Red | 5 UoM |
| Green | 25 UoM |
| Black | 100 UoM |

Chip stack composition calculated from wallet amount using greedy denomination
breakdown. Stack height capped at a maximum for display purposes; label shows
exact amount.

## Event mapping

| JSONL event | Display action |
|---|---|
| `TableOpened` | Populate table info bar |
| `SessionOpened` | Set player names |
| `PlayerSeated` | Render player seats |
| `ShoeShuffled` | Set total shoe size; update remaining/drawn |
| `HandStarted` | Increment hand counter; clear all seat states |
| `BetPlaced` | Show bet stack on player seat |
| `CardDealt` | Add card to seat; mark as latest |
| `CardDrawn` | Add card to seat; mark as latest; clear previous latest |
| `StandDeclared` | Set seat to stood state |
| `HandBust` | Clear cards; show BUST badge; dim seat |
| `HoleCardRevealed` | Flip dealer hole card |
| `HandResolved` | (used for outcome display in post-hand phase) |
| `PayoutMade` | Update wallet amount |
| `WalletUpdated` | Update chip stack |
| `PlayerLeft` | Mark seat as inactive |
| `SessionClosed` | Show session summary |
| `TableClosed` | Display closed banner |

## Bot decision delay

0.5s delay between non-human decisions (ICE-14). Implemented in
`play_table_session()` as `emit_delay_ms=500` when any non-human player is
seated. Default remains `None` (no delay) so tests are unaffected.

## CLI flag

`--no-display` on `src/play.py` — skips server start and browser open.
Useful for headless runs, CI, and bot-only sessions.

## Dependencies

Stdlib only: `http.server`, `threading`, `webbrowser`, `json`, `pathlib`.
No new external dependencies.

## Notes

- Server runs in a daemon thread — exits automatically if main thread exits
- Port conflict: if 8765 is taken, try next available port up to 8775
- Single HTML file served inline — no separate static files
- Page polls `/events` every second; large sessions may accumulate many events
  but volume is bounded by session length
- Not designed for concurrent sessions or multiple browser tabs
