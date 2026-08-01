#!/usr/bin/env python3
"""StaySharp — a 1-2 minute daily Python puzzle. One attempt per day."""
import argparse
import json
import random
from datetime import date
from pathlib import Path

STATE_PATH = Path.home() / ".staysharp" / "state.json"
START_DATE = date(2026, 8, 1)  # day 0 of the series; determines today's puzzle index

# Puzzle types rotate in this order. Add a new key here + a bank below to add a type.
TYPE_ORDER = ["guess_output", "spot_bug"]

PUZZLES = {
    "guess_output": [
        {
            "code": "x = [1, 2, 3]\ny = x\ny.append(4)\nprint(x)",
            "answer": "[1, 2, 3, 4]",
            "explain": "Lists are mutable and `y = x` binds the same object, not a copy — appending to y also changes x.",
        },
        {
            "code": "def f(a, b=[]):\n    b.append(a)\n    return b\n\nprint(f(1))\nprint(f(2))",
            "answer": "[1]\n[2, 1]",
            "explain": "Mutable default arguments are created once and reused across calls, so the list keeps growing.",
        },
        {
            "code": "print(0.1 + 0.2 == 0.3)",
            "answer": "False",
            "explain": "Floating point can't represent 0.1 or 0.2 exactly, so their sum is 0.30000000000000004, not 0.3.",
        },
        {
            "code": "print([i for i in range(5) if i % 2][::-1])",
            "answer": "[3, 1]",
            "explain": "The comprehension keeps odd numbers 1 and 3, then [::-1] reverses the resulting list.",
        },
        {
            "code": "class A:\n    x = []\n\na, b = A(), A()\na.x.append(1)\nprint(b.x)",
            "answer": "[1]",
            "explain": "`x` is a class attribute shared by all instances, so mutating it through `a` is visible through `b` too.",
        },
        {
            "code": "print('-'.join(sorted('banana')))",
            "answer": "a-a-a-b-n-n",
            "explain": "sorted() on a string sorts its characters alphabetically before join inserts '-' between them.",
        },
        {
            "code": "def outer():\n    x = 1\n    def inner():\n        print(x)\n        x = 2\n    inner()\n\nouter()",
            "answer": "UnboundLocalError",
            "explain": "Assigning to x anywhere in inner() makes it a local variable for the whole function, so the print() before the assignment fails.",
        },
        {
            "code": "print(3 in {3: 'a'})\nprint(3 in [3, 4])",
            "answer": "True\nTrue",
            "explain": "`in` on a dict checks keys, and 3 is a key here; `in` on a list checks membership, and 3 is present.",
        },
        {
            "code": "a = (1, 2)\nb = (1, 2)\nprint(a is b)\nprint(a == b)",
            "answer": "False\nTrue",
            "explain": "`is` checks identity (two separate tuple objects here); `==` checks value equality, which matches.",
        },
        {
            "code": "print(bool('False'))",
            "answer": "True",
            "explain": "'False' is a non-empty string, and any non-empty string is truthy regardless of its text content.",
        },
        {
            "code": "print(len({1, 1, 2, 2, 3}))",
            "answer": "3",
            "explain": "Sets deduplicate elements automatically, so {1, 1, 2, 2, 3} only keeps 1, 2, 3.",
        },
        {
            "code": "print(*[1, 2, 3], sep='-')",
            "answer": "1-2-3",
            "explain": "The * unpacks the list into three positional args to print(), joined by the given sep instead of a space.",
        },
    ],
    "spot_bug": [
        {
            "code": (
                "1  def average(nums):\n"
                "2      total = 0\n"
                "3      for n in nums:\n"
                "4          total = total + n\n"
                "5      return total / len(nums)\n"
                "6  \n"
                "7  print(average([]))"
            ),
            "answer": "7",
            "explain": "Calling average([]) divides by len(nums) == 0, raising ZeroDivisionError. The bug is at the call site, not inside the function.",
        },
        {
            "code": (
                "1  def remove_evens(nums):\n"
                "2      for n in nums:\n"
                "3          if n % 2 == 0:\n"
                "4              nums.remove(n)\n"
                "5      return nums\n"
                "6  \n"
                "7  print(remove_evens([1, 2, 3, 4]))"
            ),
            "answer": "2",
            "explain": "Mutating a list (nums.remove) while iterating over it skips elements, since the iterator index advances but the list shrinks underneath it.",
        },
        {
            "code": (
                "1  items = {'a': 1, 'b': 2}\n"
                "2  \n"
                "3  def bump(key):\n"
                "4      items[key] = items[key] + 1\n"
                "5  \n"
                "6  bump('c')"
            ),
            "answer": "4",
            "explain": "items['c'] doesn't exist yet, so reading items[key] on the right-hand side raises KeyError before it can be assigned.",
        },
        {
            "code": (
                "1  def make_multipliers():\n"
                "2      fns = []\n"
                "3      for i in range(3):\n"
                "4          fns.append(lambda x: x * i)\n"
                "5      return fns\n"
                "6  \n"
                "7  print([f(10) for f in make_multipliers()])"
            ),
            "answer": "4",
            "explain": "The lambda captures the variable i by reference, not its value at creation time; by the time the lambdas run, i is 2 for all of them.",
        },
        {
            "code": (
                "1  def get_last(items):\n"
                "2      return items[len(items)]\n"
                "3  \n"
                "4  print(get_last([1, 2, 3]))"
            ),
            "answer": "2",
            "explain": "Valid indices only go up to len(items) - 1; items[len(items)] is one past the end and raises IndexError.",
        },
        {
            "code": (
                "1  class Counter:\n"
                "2      count = 0\n"
                "3      def increment(self):\n"
                "4          count += 1\n"
                "5  \n"
                "6  Counter().increment()"
            ),
            "answer": "4",
            "explain": "count inside increment refers to a local/global name, not self.count — it needs to be self.count += 1 to touch the instance/class attribute.",
        },
        {
            "code": (
                "1  def double(n):\n"
                "2      result = n * 2\n"
                "3  \n"
                "4  print(double(5) + 1)"
            ),
            "answer": "2",
            "explain": "double() computes result but never returns it, so it implicitly returns None; adding 1 to None raises TypeError.",
        },
        {
            "code": (
                "1  def factorial(n):\n"
                "2      return n * factorial(n - 1)\n"
                "3  \n"
                "4  print(factorial(5))"
            ),
            "answer": "2",
            "explain": "There's no base case to stop the recursion (e.g. `if n == 0: return 1`), so it recurses forever and raises RecursionError.",
        },
        {
            "code": (
                "1  def sum_list(nums):\n"
                "2      total = 0\n"
                "3      for i in range(len(nums) - 1):\n"
                "4          total += nums[i]\n"
                "5      return total\n"
                "6  \n"
                "7  print(sum_list([1, 2, 3, 4]))"
            ),
            "answer": "3",
            "explain": "range(len(nums) - 1) stops one short, so the loop never visits the last index and the sum is missing nums[-1].",
        },
    ],
}


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
    bank = PUZZLES[ptype]
    return ptype, bank[days % len(bank)]


def random_puzzle():
    ptype = random.choice(TYPE_ORDER)
    return ptype, random.choice(PUZZLES[ptype])


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
    label = "Guess the output" if ptype == "guess_output" else "Spot the bug (which line number?)"
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
