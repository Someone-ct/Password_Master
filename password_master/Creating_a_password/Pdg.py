# ╔══════════════════════════════════════════════════════════════╗
# ║              Password Generator Module                       ║
# ╚══════════════════════════════════════════════════════════════╝

import os
import sys
import time
import secrets
from termcolor import colored, cprint

import Creating_a_password.parts as parts


# ══════════════════════════════════════════════════════════════
# [1] EMOJI DETECTION
# ══════════════════════════════════════════════════════════════

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
    return emoji if EMOJI_OK else fallback


# ══════════════════════════════════════════════════════════════
# [2] CONFIGURATION
# ══════════════════════════════════════════════════════════════

PROGRAM_DIR   = os.path.dirname(os.path.abspath(__file__))
PASSWORDS_DIR = os.path.join(PROGRAM_DIR, "passwords")
os.makedirs(PASSWORDS_DIR, exist_ok=True)

MAX_LENGTH = 512


# ══════════════════════════════════════════════════════════════
# [3] HELPERS
# ══════════════════════════════════════════════════════════════

def _divider(char: str = "─", color: str = "cyan", width: int = 60) -> None:
    print(colored(char * width, color))


def _ask_yes_no(prompt: str) -> bool:
    while True:
        ans = input(f"\n{prompt}\n  ==> ").strip().lower()
        if ans in ("y", "yes"): return True
        if ans in ("n", "no"):  return False
        print(colored(
            f"  {E('✖','X')}  Invalid input — please enter Y or N.", "red"
        ))


# ══════════════════════════════════════════════════════════════
# [4] AUTO FILENAME
# ══════════════════════════════════════════════════════════════

def _next_filename(folder: str) -> str:
    base = "Password"
    ext  = ".txt"

    if not os.path.exists(os.path.join(folder, base + ext)):
        return os.path.join(folder, base + ext)

    counter = 2
    while True:
        candidate = os.path.join(folder, f"{base}{counter}{ext}")
        if not os.path.exists(candidate):
            return candidate
        counter += 1


# ══════════════════════════════════════════════════════════════
# [5] SAVE PATH RESOLVER
# ══════════════════════════════════════════════════════════════

def _resolve_save_path() -> str | None:
    print(colored(
        f"\n  {E('💾','[SAVE]')}  Enter a path/filename to save the password,\n"
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
                "  Enter a custom path, or press Enter again to accept.", "yellow"
            ))
            continue

        if not raw.endswith(".txt"):
            raw += ".txt"

        folder   = os.path.dirname(raw)
        filename = os.path.basename(raw)

        if not folder:
            path = os.path.join(PASSWORDS_DIR, filename)
            print(colored(
                f"\n  {E('ℹ','i')}  No directory given — saving as:\n  {path}", "cyan"
            ))
        else:
            path   = os.path.abspath(raw)
            folder = os.path.dirname(path)

            if not os.path.isdir(folder):
                print(colored(
                    f"  {E('✖','X')}  Directory not found:\n     {folder}\n"
                    "  Check the path or press Enter for the default folder.", "red"
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
                f"\n  {E('⚠','!')}  File already exists ({size_kb:.1f} KB):\n     {path}",
                "yellow"
            ))
            if not _ask_yes_no("Overwrite it? [Y/N]"):
                print(colored(
                    "  Enter a different filename, or press Enter for auto-name.",
                    "yellow"
                ))
                continue

        return path


# ══════════════════════════════════════════════════════════════
# [6] GET PASSWORD LENGTH
# ══════════════════════════════════════════════════════════════

def _get_length() -> int:
    while True:
        raw = input(colored(
            f"\n  {E('📏','[LEN]')}  Enter the desired password length:\n  ==> ",
            "cyan"
        )).strip()

        if not raw:
            print(colored(f"  {E('✖','X')}  Length cannot be empty.", "red"))
            continue

        if "." in raw:
            print(colored(
                f"  {E('✖','X')}  Decimal numbers are not allowed.", "red"
            ))
            continue

        if not raw.lstrip("-").isdigit():
            print(colored(
                f"  {E('✖','X')}  Invalid input — whole numbers only.", "red"
            ))
            continue

        length = int(raw)

        if length < 1:
            print(colored(
                f"  {E('✖','X')}  Length must be at least 1.", "red"
            ))
            continue

        if length > MAX_LENGTH:
            print(colored(
                f"  {E('⚠','!')}  Maximum allowed length is {MAX_LENGTH}.", "yellow"
            ))
            continue

        return length


# ══════════════════════════════════════════════════════════════
# [7] GENERATE PASSWORD
# ══════════════════════════════════════════════════════════════

def _build_password(length: int) -> str:
    parts.Uchoice()

    charset = list(parts.parts)

    if not charset:
        import string
        charset = list(string.ascii_letters + string.digits + string.punctuation)
        print(colored(
            f"  {E('⚠','!')}  No character set selected — "
            "using full printable ASCII as fallback.", "yellow"
        ))

    return "".join(secrets.choice(charset) for _ in range(length))


# ══════════════════════════════════════════════════════════════
# [8] DISPLAY PASSWORD
# ══════════════════════════════════════════════════════════════

def _display_password(password: str) -> None:
    print()
    _divider("─")
    cprint(f"  {E('🔑','[RESULT]')}  GENERATED PASSWORD", "cyan", attrs=["bold"])
    _divider("─")
    print(f"\n  {colored(password, 'green', attrs=['bold'])}\n")
    print(f"  Length : {colored(str(len(password)), 'cyan')} characters")
    _divider("─")


# ══════════════════════════════════════════════════════════════
# [9] WRITE REPORT
# ══════════════════════════════════════════════════════════════

def _write_report(path: str, password: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("===== Generated Password =====\n\n")
        f.write(f"Generated on : {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Length       : {len(password)} characters\n\n")
        f.write(f"Password     : {password}\n\n")
        f.write("=" * 30 + "\n")


# ══════════════════════════════════════════════════════════════
# [10] PUBLIC ENTRY POINT
# ══════════════════════════════════════════════════════════════

def generate_pd() -> None:
    length   = _get_length()
    password = _build_password(length)

    _display_password(password)
    time.sleep(1)

    if not _ask_yes_no(f"  {E('💾','[?]')}  Save the generated password? [Y/N]"):
        return

    path = _resolve_save_path()
    if path is None:
        print(colored(f"  {E('✖','X')}  Save cancelled.", "yellow"))
        return

    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        _write_report(path, password)
        print(colored(
            f"\n  {E('✔','OK')}  Password saved to:\n  {path}", "green"
        ))
    except PermissionError:
        print(colored(
            f"  {E('✖','X')}  Permission denied — try a different location.", "red"
        ))
    except OSError as exc:
        print(colored(f"  {E('✖','X')}  Could not save file: {exc}", "red"))

    time.sleep(2)
