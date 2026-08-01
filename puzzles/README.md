# Puzzle banks

Each puzzle type is one JSON file here, named `<type>.json` to match an entry in
`TYPE_ORDER` in `staysharp.py`.

```json
{
  "label": "Human-readable name shown in the puzzle header",
  "puzzles": [
    {
      "code": "the snippet shown to the player",
      "answer": "exact string the player must type to be marked correct",
      "explain": "shown after answering, whether right or wrong"
    }
  ]
}
```

To add a puzzle to an existing type, append an entry to that file's `puzzles` list —
no Python changes needed.

To add a new type: create `puzzles/<name>.json` in this shape, then add `"<name>"` to
`TYPE_ORDER` in `staysharp.py`.
