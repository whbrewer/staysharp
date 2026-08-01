# StaySharp

A 1-2 minute daily Python puzzle for your terminal — like Wordle, but for keeping your
programming skills sharp instead of your vocabulary.

One puzzle a day, one attempt, deterministic by date (same puzzle if you run it multiple
times today). Tracks a streak locally.

## Usage

```bash
python3 staysharp.py
```

Or add an alias:

```bash
alias staysharp='python3 /path/to/staysharp.py'
```

State (streak + history) is stored in `~/.staysharp/state.json`.

## Puzzle types

- **Guess the output** — read a short snippet, predict exactly what it prints.
- **Spot the bug** — find the line number responsible for a bug in the snippet.

Puzzle type rotates by day. New types can be added by adding a key to `TYPE_ORDER` and a
bank of puzzles to `PUZZLES` in `staysharp.py`.
