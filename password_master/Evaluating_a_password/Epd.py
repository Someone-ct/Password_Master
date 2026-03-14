# ╔══════════════════════════════════════════════════════════════╗
# ║              Password Evaluator Module                       ║
# ╚══════════════════════════════════════════════════════════════╝

import os
import sys
import time
import string
from termcolor import colored, cprint

# ──────────────────────────────────────────────────────────────
# [1] EMOJI DETECTION  (resolved once at import time)
# ──────────────────────────────────────────────────────────────

def _detect_emoji_support() -> bool:
    enc = (getattr(sys.stdout, "encoding", "") or "").lower().replace("-", "")
    if os.name == "nt":
        modern = bool(
            os.environ.get("WT_SESSION")
            or os.environ.get("TERM_PROGRAM") == "vscode"
        )
        return modern and "utf8" in enc
    return "utf8" in enc

EMOJI_OK: bool = _detect_emoji_support()

def E(emoji: str, fallback: str = "") -> str:
    """Return emoji on capable terminals, plain text otherwise."""
    return emoji if EMOJI_OK else fallback


# ──────────────────────────────────────────────────────────────
# [2] CONFIGURATION
# ──────────────────────────────────────────────────────────────

PROGRAM_DIR   = os.path.dirname(os.path.abspath(__file__))
PASSWORDS_DIR = os.path.join(PROGRAM_DIR, "Passwords_Evaluations")
os.makedirs(PASSWORDS_DIR, exist_ok=True)

SCORE_VERY_STRONG = 90
SCORE_STRONG      = 75
SCORE_MEDIUM      = 50
SCORE_WEAK        = 30


# ──────────────────────────────────────────────────────────────
# [3] DATA CLASS
# ──────────────────────────────────────────────────────────────

class PasswordStats:
    def __init__(self, score: int, upper: bool, lower: bool,
                 digits: bool, symbols: bool, length: int):
        self.score   = score
        self.upper   = upper
        self.lower   = lower
        self.digits  = digits
        self.symbols = symbols
        self.length  = length

    def strength_label(self) -> str:
        if self.score >= SCORE_VERY_STRONG: return "VERY STRONG"
        if self.score >= SCORE_STRONG:      return "STRONG"
        if self.score >= SCORE_MEDIUM:      return "MEDIUM"
        if self.score >= SCORE_WEAK:        return "WEAK"
        return "VERY WEAK"

    def strength_colored(self) -> str:
        label = self.strength_label()
        color_map = {
            "VERY STRONG": "green",
            "STRONG":      "light_green",
            "MEDIUM":      "yellow",
            "WEAK":        "light_red",
            "VERY WEAK":   "red",
        }
        return colored(label, color_map[label])


# ──────────────────────────────────────────────────────────────
# [4] HELPERS
# ──────────────────────────────────────────────────────────────

def _bool_tag(value: bool) -> str:
    return (
        colored(f"{E('✔','[TRUE]')}  TRUE",  "green") if value
        else colored(f"{E('✖','[FALSE]')} FALSE", "red")
    )


def _divider(char: str = "─", color: str = "cyan", width: int = 60) -> None:
    print(colored(char * width, color))


def _ask_yes_no(prompt: str) -> bool:
    while True:
        ans = input(f"\n{prompt}\n==> ").strip().lower()
        if ans in ("y", "yes"): return True
        if ans in ("n", "no"):  return False
        print(colored(
            f"  {E('✖','X')}  Invalid input — please enter Y or N.", "red"
        ))


# ──────────────────────────────────────────────────────────────
# [5] DEFAULT FILENAME
# ──────────────────────────────────────────────────────────────

def _next_filename(folder: str) -> str:
    base = "Password_Evaluation"
    ext  = ".txt"

    if not os.path.exists(os.path.join(folder, base + ext)):
        return os.path.join(folder, base + ext)

    counter = 2
    while True:
        candidate = os.path.join(folder, f"{base}{counter}{ext}")
        if not os.path.exists(candidate):
            return candidate
        counter += 1


# ──────────────────────────────────────────────────────────────
# [6] EVALUATE PASSWORD
# ──────────────────────────────────────────────────────────────

def evaluate_password() -> tuple:
    while True:
        password = input(colored(
            f"\n  {E('🔑','[*]')}  Enter your password:\n  ==> ", "cyan"
        ))
        if password:
            break
        print(colored(
            f"  {E('✖','X')}  Password cannot be empty.", "red"
        ))

    score      = 0
    has_lower  = any(c.islower()             for c in password)
    has_upper  = any(c.isupper()             for c in password)
    has_digit  = any(c.isdigit()             for c in password)
    has_symbol = any(c in string.punctuation for c in password)
    length     = len(password)

    if length >= 12: score += 15
    if length >= 16: score += 30
    if has_lower:    score += 10
    if has_upper:    score += 10
    if has_digit:    score += 10
    if has_symbol:   score += 25

    score = min(score, 100)

    stats = PasswordStats(score, has_upper, has_lower, has_digit, has_symbol, length)

    print()
    _divider("─")
    cprint(f"  {E('📊','[RESULTS]')}  EVALUATION RESULTS", "cyan", attrs=["bold"])
    _divider("─")

    print(f"  {E('💪','Strength')}  Password strength : {stats.strength_colored()}")
    print()
    print(f"  Uppercase letters : {_bool_tag(stats.upper)}")
    print(f"  Lowercase letters : {_bool_tag(stats.lower)}")
    print(f"  Numbers           : {_bool_tag(stats.digits)}")
    print(f"  Symbols           : {_bool_tag(stats.symbols)}")
    print(f"  Length            : {colored(str(length), 'cyan')} characters")
    print(f"  Score             : {colored(str(score) + '%', 'magenta')}")

    tips = []
    if not has_upper:  tips.append("add uppercase letters")
    if not has_lower:  tips.append("add lowercase letters")
    if not has_digit:  tips.append("include numbers")
    if not has_symbol: tips.append("use special characters (!@#…)")
    if length < 12:    tips.append("make it at least 12 characters long")

    if tips:
        print()
        cprint(f"  {E('💡','[TIPS]')}  Suggestions to improve:", "yellow")
        for tip in tips:
            print(colored(f"     {E('•','-')} {tip}", "yellow"))

    _divider("─")

    return password, stats


# ──────────────────────────────────────────────────────────────
# [7] SAVE PATH RESOLVER
# ──────────────────────────────────────────────────────────────

def _resolve_save_path() -> str | None:
    print(colored(
        f"\n  {E('💾','[SAVE]')}  Enter a file path to save the evaluation,\n"
        "  or press Enter to save automatically in the module folder.",
        "cyan"
    ))

    while True:
        raw = input("  ==> ").strip().strip('"').strip("'")

        if not raw:
            auto = _next_filename(PASSWORDS_DIR)
            print(colored(
                f"\n  {E('📂','[DIR]')}  Will save to:\n  {auto}", "cyan"
            ))
            if _ask_yes_no("Confirm? [Y/N]"):
                return auto
            print(colored(
                "  Enter a custom path below, or press Enter again "
                "to accept the default.", "yellow"
            ))
            continue

        if not raw.endswith(".txt"):
            raw += ".txt"

        folder   = os.path.dirname(raw)
        filename = os.path.basename(raw)

        if not folder:
            path = os.path.join(PASSWORDS_DIR, filename)
            print(colored(
                f"\n  {E('ℹ','i')}  No directory given — saving as:\n  {path}",
                "cyan"
            ))
        else:
            path   = os.path.abspath(raw)
            folder = os.path.dirname(path)

            if not os.path.isdir(folder):
                print(colored(
                    f"  {E('✖','X')}  Directory not found:\n     {folder}", "red"
                ))
                print(colored(
                    "  Check the path and try again, or press Enter "
                    "for the default folder.", "yellow"
                ))
                continue

            if not os.access(folder, os.W_OK):
                print(colored(
                    f"  {E('✖','X')}  No write permission in:\n     {folder}", "red"
                ))
                continue

        if os.path.exists(path):
            size_kb = os.path.getsize(path) / 1024
            print(colored(
                f"\n  {E('⚠','!')}  File already exists ({size_kb:.1f} KB):\n"
                f"     {path}",
                "yellow"
            ))
            if not _ask_yes_no("Overwrite it? [Y/N]"):
                print(colored(
                    "  Enter a different filename, or press Enter for auto-name.",
                    "yellow"
                ))
                continue

        return path


# ──────────────────────────────────────────────────────────────
# [8] WRITE REPORT
# ──────────────────────────────────────────────────────────────

def _write_report(path: str, password: str, stats: PasswordStats) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("===== Password Evaluation =====\n\n")
        f.write(f"Password        : {password}\n")
        f.write(f"Evaluation date : {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("Details:\n")
        f.write(f"  Uppercase letters : {'TRUE' if stats.upper   else 'FALSE'}\n")
        f.write(f"  Lowercase letters : {'TRUE' if stats.lower   else 'FALSE'}\n")
        f.write(f"  Numbers           : {'TRUE' if stats.digits  else 'FALSE'}\n")
        f.write(f"  Symbols           : {'TRUE' if stats.symbols else 'FALSE'}\n")
        f.write(f"  Length            : {stats.length} characters\n")
        f.write(f"  Score             : {stats.score}%\n\n")
        f.write(f"Password strength : {stats.strength_label()}\n")
        f.write("=" * 31 + "\n")


# ──────────────────────────────────────────────────────────────
# [9] PUBLIC ENTRY POINT
# ──────────────────────────────────────────────────────────────

def run() -> None:
    password, stats = evaluate_password()

    if not _ask_yes_no(f"  {E('💾','[?]')}  Save the evaluation results? [Y/N]"):
        return

    path = _resolve_save_path()
    if path is None:
        print(colored(f"  {E('✖','X')}  Save cancelled.", "yellow"))
        return

    try:
        _write_report(path, password, stats)
        print(colored(
            f"\n  {E('✔','OK')}  Evaluation saved to:\n  {path}", "green"
        ))
    except PermissionError:
        print(colored(
            f"  {E('✖','X')}  Permission denied — try a different location.", "red"
        ))
    except OSError as exc:
        print(colored(f"  {E('✖','X')}  Could not save file: {exc}", "red"))

    time.sleep(3)
