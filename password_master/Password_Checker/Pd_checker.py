# ╔══════════════════════════════════════════════════════════════╗
# ║              Password Checker Module                         ║
# ╚══════════════════════════════════════════════════════════════╝

import os
import sys
import time
import threading
from termcolor import colored, cprint


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
    """Return emoji on capable terminals, plain text otherwise."""
    return emoji if EMOJI_OK else fallback


# ══════════════════════════════════════════════════════════════
# [2] CONFIGURATION
# ══════════════════════════════════════════════════════════════

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "pds checked")


# ══════════════════════════════════════════════════════════════
# [3] TERMINAL HELPERS
# ══════════════════════════════════════════════════════════════

def _divider(char: str = "─", color: str = "cyan", width: int = 62) -> None:
    print(colored(char * width, color))


def _section(title: str) -> None:
    print(colored(f"\n  ── {title} {'─' * max(0, 44 - len(title))}", "cyan"))


# ══════════════════════════════════════════════════════════════
# [4] BANNER
# ══════════════════════════════════════════════════════════════

def banner() -> None:
    _divider("═")
    cprint(
        f"  {E('🔍','[~]')}  Password Checker Module",
        "cyan", attrs=["bold"]
    )
    _divider("═")
    print()


# ══════════════════════════════════════════════════════════════
# [5] INPUT HELPERS
# ══════════════════════════════════════════════════════════════

def ask_yes_no(message: str) -> bool:
    while True:
        raw = input(f"\n{message}\n  ==> ").strip().lower()
        if raw in ("y", "yes"): return True
        if raw in ("n", "no"):  return False
        print(colored(
            f"  {E('✖','X')}  Invalid input — please enter Y or N.", "red"
        ))


def get_password() -> str:
    while True:
        pw = input(colored(
            f"\n  {E('🔑','[*]')}  Enter the password to check:\n  ==> ", "cyan"
        )).strip()

        if not pw:
            print(colored(
                f"  {E('✖','X')}  Password cannot be empty.", "red"
            ))
            continue

        if len(pw) < 4:
            print(colored(
                f"  {E('⚠','!')}  Very short password ({len(pw)} chars). "
                "Continue anyway? [Y/N]", "yellow"
            ))
            if ask_yes_no(""):
                return pw
            continue

        return pw


def get_wordlist_path() -> str:
    while True:
        path = input(colored(
            f"\n  {E('📂','[PATH]')}  Enter the wordlist file path:\n  ==> ", "cyan"
        )).strip()

        if not path:
            print(colored(f"  {E('✖','X')}  Path cannot be empty.", "red"))
            continue

        path = path.strip('"').strip("'")

        if not os.path.exists(path):
            print(colored(
                f"  {E('✖','X')}  Path not found:\n     {path}\n"
                "     Check for typos, wrong drive letter, or missing folder.", "red"
            ))
            continue

        if os.path.isdir(path):
            print(colored(
                f"  {E('✖','X')}  That path is a folder, not a file.\n"
                "     Please provide the full path including the filename.", "red"
            ))
            continue

        if not os.access(path, os.R_OK):
            print(colored(
                f"  {E('✖','X')}  No read permission for that file.\n"
                "     Try running the tool as Administrator / sudo.", "red"
            ))
            continue

        if os.path.getsize(path) == 0:
            print(colored(
                f"  {E('✖','X')}  The wordlist file is empty (0 bytes).", "red"
            ))
            continue

        ext = os.path.splitext(path)[1].lower()
        if ext not in (".txt", ".lst", ".list", ".dic", ".dict", ""):
            print(colored(
                f"  {E('⚠','!')}  Unusual extension: {ext!r}\n"
                "     Expected .txt / .lst / .dic — continue anyway? [Y/N]",
                "yellow"
            ))
            if not ask_yes_no(""):
                continue

        size_mb = os.path.getsize(path) / (1024 * 1024)
        print(colored(
            f"  {E('ℹ','i')}  File size: {size_mb:.2f} MB  ({path})",
            "cyan"
        ))

        return path


# ══════════════════════════════════════════════════════════════
# [6] PASSWORD STRENGTH ANALYSER
# ══════════════════════════════════════════════════════════════

def analyze_password_strength(password: str) -> tuple:
    """Returns (label, color)."""
    score = 0
    if len(password) >= 8:             score += 1
    if len(password) >= 12:            score += 1
    if any(c.isdigit()     for c in password): score += 1
    if any(c.isupper()     for c in password): score += 1
    if any(not c.isalnum() for c in password): score += 1

    table = {
        0: ("Very Weak",   "red"),
        1: ("Very Weak",   "red"),
        2: ("Weak",        "red"),
        3: ("Medium",      "yellow"),
        4: ("Strong",      "green"),
        5: ("Very Strong", "green"),
    }
    return table.get(score, ("Unknown", "white"))


# ══════════════════════════════════════════════════════════════
# [7] CORE SCAN — live speed + early-exit + progress thread
# ══════════════════════════════════════════════════════════════

def _progress_printer(state: dict, interval: float = 10.0) -> None:
    while not state["stop"].wait(timeout=interval):
        if state.get("done"):
            break
        checked = state.get("checked", 0)
        speed   = state.get("speed",   0.0)
        elapsed = state.get("elapsed", 0.0)
        pct     = state.get("pct",     "?")
        print(colored(
            f"\n  {E('📊','[UPDATE]')}  Checked: {checked:,}  |  "
            f"Speed: {speed:,.0f} p/s  |  "
            f"Elapsed: {elapsed:.1f}s  |  "
            f"Progress: {pct}\n",
            "yellow"
        ))


def check_password_in_wordlist(password: str, wordlist_path: str) -> dict:
    found_exact     = False
    exact_line      = None
    similar_matches = []
    total_checked   = 0
    pw_lower        = password.lower()

    file_size = os.path.getsize(wordlist_path)
    try:
        with open(wordlist_path, "rb") as fh:
            sample = fh.read(4096)
        newlines  = sample.count(b"\n") or 1
        avg_len   = len(sample) / newlines
        est_lines = int(file_size / avg_len) if avg_len else 0
    except Exception:
        est_lines = 0

    start_time    = time.perf_counter()
    last_tick     = start_time
    last_count    = 0
    current_speed = 0.0

    state = {
        "done":    False,
        "stop":    threading.Event(),
        "checked": 0,
        "speed":   0.0,
        "elapsed": 0.0,
        "pct":     "?%",
    }
    printer = threading.Thread(
        target=_progress_printer, args=(state,), daemon=True
    )
    printer.start()

    print(colored(
        f"  {E('🔎','[SCAN]')}  Scanning started — "
        "auto progress update every 10 s.\n",
        "cyan"
    ))

    interrupted = False

    try:
        with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as fh:
            for line_number, raw_line in enumerate(fh, start=1):
                word = raw_line.rstrip("\r\n")
                total_checked += 1

                if word == password:
                    found_exact = True
                    exact_line  = line_number
                    print(colored(
                        f"\n\n  {E('✔','FOUND')}  Exact match found at line "
                        f"{line_number} — stopping scan early.",
                        "green"
                    ))
                    break

                elif word.lower() == pw_lower:
                    similar_matches.append((line_number, word))

                if total_checked % 50_000 == 0:
                    now      = time.perf_counter()
                    delta_t  = now - last_tick
                    delta_n  = total_checked - last_count
                    current_speed = delta_n / delta_t if delta_t > 0 else 0.0
                    elapsed  = now - start_time

                    last_tick  = now
                    last_count = total_checked

                    pct_str = (
                        f"{total_checked / est_lines * 100:.1f}%"
                        if est_lines else "?%"
                    )

                    state.update({
                        "checked": total_checked,
                        "speed":   current_speed,
                        "elapsed": elapsed,
                        "pct":     pct_str,
                    })

                    print(colored(
                        f"  Checked: {total_checked:>12,}  |  "
                        f"Speed: {current_speed:>10,.0f} p/s  |  "
                        f"Elapsed: {elapsed:6.1f}s  |  {pct_str}",
                        "yellow"
                    ), end="\r")

    except PermissionError:
        print(colored(
            f"\n  {E('✖','X')}  Lost read permission mid-scan.", "red"
        ))
    except KeyboardInterrupt:
        interrupted = True
        print(colored(
            f"\n\n  {E('⚠','!')}  Scan interrupted by user (Ctrl+C).", "yellow"
        ))

    state["done"] = True
    state["stop"].set()
    printer.join(timeout=1)

    total_elapsed = time.perf_counter() - start_time

    return {
        "found":       found_exact,
        "line":        exact_line,
        "similar":     similar_matches,
        "checked":     total_checked,
        "elapsed":     total_elapsed,
        "interrupted": interrupted,
        "est_lines":   est_lines,
    }


# ══════════════════════════════════════════════════════════════
# [8] DISPLAY RESULTS
# ══════════════════════════════════════════════════════════════

def display_results(password: str, wordlist: str, result: dict) -> None:
    strength_label, strength_color = analyze_password_strength(password)
    avg_speed = (
        result["checked"] / result["elapsed"]
        if result["elapsed"] > 0 else 0
    )

    print()
    _divider("─")
    cprint(f"  {E('📋','[RESULTS]')}  RESULTS", "cyan", attrs=["bold"])
    _divider("─")

    print(f"  {E('🔑','Password')}  Password : {colored(password, 'magenta')}")
    print(f"  {E('💪','Strength')}  Strength : {colored(strength_label, strength_color)}")
    print(f"  {E('📂','Wordlist')}  Wordlist : {wordlist}")

    _section("Statistics")
    print(f"  Passwords checked  : {result['checked']:,}")
    if result["est_lines"]:
        coverage = min(result["checked"] / result["est_lines"] * 100, 100)
        print(f"  Coverage (approx)  : {coverage:.1f}%")
    print(f"  Average speed      : {avg_speed:,.0f} passwords / second")
    print(f"  Time elapsed       : {result['elapsed']:.2f} seconds")
    if result.get("interrupted"):
        print(colored(
            f"  {E('⚠','!')}  Scan was interrupted early.", "yellow"
        ))

    _section("Search Results")
    if result["found"]:
        print(colored(
            f"  {E('✔','[FOUND]')}  Exact password FOUND at line {result['line']}!",
            "green", attrs=["bold"]
        ))
    else:
        print(colored(
            f"  {E('✖','[NOT FOUND]')}  Exact password NOT found in wordlist.",
            "red"
        ))

    if result["similar"]:
        count = len(result["similar"])
        print(colored(
            f"\n  {E('⚠','!')}  Similar passwords found ({count}):", "yellow"
        ))
        for line, word in result["similar"][:20]:
            print(
                f"     Line {colored(str(line), 'yellow'):>8} "
                f": {colored(word, 'magenta')}"
            )
        if count > 20:
            print(colored(f"     {E('…','...')} and {count - 20} more.", "yellow"))
    else:
        print(colored(
            f"  {E('–','-')}  No similar (case-insensitive) passwords found.",
            "yellow"
        ))

    _divider("─")
    print()


# ══════════════════════════════════════════════════════════════
# [9] SAVE LOGIC
# ══════════════════════════════════════════════════════════════

def _auto_filename() -> str:
    """First unused slot: pdc result.txt → pdc result 2.txt …"""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    base = "pdc result"
    ext  = ".txt"

    path = os.path.join(RESULTS_DIR, base + ext)
    if not os.path.exists(path):
        return path

    counter = 2
    while True:
        path = os.path.join(RESULTS_DIR, f"{base} {counter}{ext}")
        if not os.path.exists(path):
            return path
        counter += 1


def _check_overwrite(path: str) -> bool:
    if not os.path.exists(path):
        return True
    size_kb = os.path.getsize(path) / 1024
    print(colored(
        f"\n  {E('⚠','!')}  WARNING: File already exists:\n"
        f"     {path}\n"
        f"     Size: {size_kb:.1f} KB — overwriting will erase it permanently!",
        "yellow"
    ))
    return ask_yes_no("Overwrite? [Y/N]")


def _build_report(password: str, wordlist: str, result: dict) -> str:
    strength_label, _ = analyze_password_strength(password)
    avg_speed = (
        result["checked"] / result["elapsed"]
        if result["elapsed"] > 0 else 0
    )
    lines = [
        "Password Checker Results",
        "=" * 50,
        f"Date             : {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"Password         : {password}",
        f"Strength         : {strength_label}",
        f"Wordlist         : {wordlist}",
        "",
        f"Passwords checked: {result['checked']:,}",
        f"Average speed    : {avg_speed:,.0f} p/s",
        f"Time elapsed     : {result['elapsed']:.2f} seconds",
    ]
    if result.get("est_lines"):
        coverage = min(result["checked"] / result["est_lines"] * 100, 100)
        lines.append(f"Coverage (approx): {coverage:.1f}%")
    if result.get("interrupted"):
        lines.append("NOTE             : Scan was interrupted early.")

    lines.append("")

    if result["found"]:
        lines += [
            "STATUS           : FOUND",
            f"Line number      : {result['line']}",
        ]
    else:
        lines.append("STATUS           : NOT FOUND")

    if result["similar"]:
        lines.append(f"\nSimilar passwords ({len(result['similar'])}):")
        for ln, word in result["similar"]:
            lines.append(f"  Line {ln}: {word}")
    else:
        lines.append("\nNo similar passwords found.")

    lines.append("\n" + "=" * 50)
    return "\n".join(lines) + "\n"


def _resolve_save_path(raw: str):
    raw = raw.strip('"').strip("'")

    if not raw.endswith(".txt"):
        raw += ".txt"

    parent = os.path.dirname(raw)

    if not parent:
        os.makedirs(RESULTS_DIR, exist_ok=True)
        resolved = os.path.join(RESULTS_DIR, raw)
        print(colored(
            f"\n  {E('ℹ','i')}  No directory given — saving in:\n"
            f"     {RESULTS_DIR}",
            "cyan"
        ))
        return resolved

    resolved = os.path.abspath(raw)
    parent   = os.path.dirname(resolved)

    if not os.path.isdir(parent):
        print(colored(
            f"  {E('✖','X')}  Directory not found:\n     {parent}", "red"
        ))
        return None

    if not os.access(parent, os.W_OK):
        print(colored(
            f"  {E('✖','X')}  No write permission in:\n     {parent}", "red"
        ))
        return None

    return resolved


def save_results(password: str, wordlist: str, result: dict) -> None:
    print(colored(
        f"\n  {E('💾','[SAVE]')}  Enter a path/filename to save the results,\n"
        "  or press Enter to save automatically in the tool folder.",
        "cyan"
    ))

    while True:
        raw = input("  ==> ").strip()

        if not raw:
            auto_path = _auto_filename()
            print(colored(
                f"\n  {E('📂','[DIR]')}  Will save to:\n  {auto_path}", "cyan"
            ))
            if not ask_yes_no("Confirm? [Y/N]"):
                print(colored(
                    f"  {E('–','-')}  Cancelled — enter a custom path "
                    "or press Enter again.", "yellow"
                ))
                continue
            path = auto_path
            break

        path = _resolve_save_path(raw)

        if path is None:
            print(colored(
                "  Fix the path and try again, or press Enter for auto-save.",
                "yellow"
            ))
            continue

        if not _check_overwrite(path):
            print(colored(
                "  Overwrite cancelled — try a different name.", "yellow"
            ))
            continue

        break

    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(_build_report(password, wordlist, result))
        print(colored(
            f"\n  {E('✔','OK')}  Results saved to:\n     {path}", "green"
        ))
    except PermissionError:
        print(colored(
            f"  {E('✖','X')}  Permission denied — try a different location.", "red"
        ))
    except OSError as exc:
        print(colored(
            f"  {E('✖','X')}  Could not save: {exc}", "red"
        ))


# ══════════════════════════════════════════════════════════════
# [10] PUBLIC ENTRY POINT
# ══════════════════════════════════════════════════════════════

def run_password_checker() -> None:
    banner()

    password      = get_password()
    wordlist_path = get_wordlist_path()

    result = check_password_in_wordlist(password, wordlist_path)

    display_results(password, wordlist_path, result)

    if ask_yes_no(f"  {E('💾','[?]')}  Save results to a file? [Y/N]"):
        save_results(password, wordlist_path, result)

    _divider()
    print(colored(
        f"  {E('✔','Done')}  All done. Goodbye!\n", "cyan"
    ))
    time.sleep(1)
