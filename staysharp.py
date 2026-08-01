#!/usr/bin/env python3
"""StaySharp — a 1-2 minute daily Python puzzle. One attempt per day."""
import argparse
import json
import random
from datetime import date
from pathlib import Path

STATE_PATH = Path.home() / ".staysharp" / "state.json"
START_DATE = date(2026, 8, 1)  # day 0 of the series; determines today's puzzle index
PUZZLES_DIR = Path(__file__).resolve().parent / "puzzles"

# Puzzle types rotate in this order. Add a new type by adding its name here
# and dropping a matching puzzles/<name>.json file (see puzzles/README.md).
TYPE_ORDER = ["guess_output", "spot_bug"]


def load_puzzles():
    banks = {}
    for ptype in TYPE_ORDER:
        path = PUZZLES_DIR / f"{ptype}.json"
        banks[ptype] = json.loads(path.read_text())
    return banks


PUZZLES = load_puzzles()


def load_state():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {"streak": 0, "last_played": None, "last_correct": None, "history": {}}


def save_state(state):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2))


def todays_puzzle():
    days = (date.today() - START_DATE).days
    ptype = TYPE_ORDER[days % len(TYPE_ORDER)]
    bank = PUZZLES[ptype]["puzzles"]
    return ptype, bank[days % len(bank)]


def random_puzzle():
    ptype = random.choice(TYPE_ORDER)
    return ptype, random.choice(PUZZLES[ptype]["puzzles"])


def update_streak(state, correct, today_str):
    if not correct:
        state["streak"] = 0
        return
    last = state["last_played"]
    if last is not None and (date.today() - date.fromisoformat(last)).days == 1:
        state["streak"] += 1
    else:
        state["streak"] = 1


def parse_args():
    parser = argparse.ArgumentParser(description="StaySharp — a daily Python puzzle.")
    parser.add_argument(
        "-r", "--replay",
        action="store_true",
        help="Play an extra random puzzle without touching today's streak or history.",
    )
    return parser.parse_args()


def play(ptype, puzzle, label_prefix):
    label = PUZZLES[ptype]["label"]
    print(f"=== StaySharp — {label_prefix} — {label} ===\n")
    print(puzzle["code"])
    print()

    guess = input("Your answer: ").strip()
    correct = guess == puzzle["answer"]

    print("\n✅ Correct!" if correct else f"\n❌ Not quite. Answer: {puzzle['answer']}")
    print(puzzle["explain"])
    return correct


def main():
    args = parse_args()

    if args.replay:
        ptype, puzzle = random_puzzle()
        play(ptype, puzzle, "replay (doesn't count toward streak)")
        return

    state = load_state()
    today_str = date.today().isoformat()

    if state["last_played"] == today_str:
        outcome = "correct" if state["last_correct"] else "incorrect"
        print(f"Already played today ({outcome}). Streak: {state['streak']}. Come back tomorrow.")
        print("Use --replay/-r for an extra practice puzzle that doesn't touch your streak.")
        return

    ptype, puzzle = todays_puzzle()
    correct = play(ptype, puzzle, today_str)

    update_streak(state, correct, today_str)
    state["last_played"] = today_str
    state["last_correct"] = correct
    state["history"][today_str] = {"type": ptype, "correct": correct}
    save_state(state)

    print(f"\nStreak: {state['streak']}")


if __name__ == "__main__":
    main()
