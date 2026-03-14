# ╔══════════════════════════════════════════════════════════════╗
# ║              Password Tool Suite  —  Main Entry              ║
# ╚══════════════════════════════════════════════════════════════╝

import os
import sys
import time
import shutil
import ascii_magic
from termcolor import colored, cprint

import Creating_a_password.Pdg  as pdg
import Evaluating_a_password.Epd  as epd
import Password_Checker.Pd_checker as pdc

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
    """Return emoji on capable terminals, plain fallback text otherwise."""
    return emoji if EMOJI_OK else fallback


# ══════════════════════════════════════════════════════════════
# [2] CONSTANTS
# ══════════════════════════════════════════════════════════════

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(SCRIPT_DIR, "img", "img.png")

MENU_ITEMS = {
    1: ("Create a password",             pdg.generate_pd),
    2: ("Evaluate a password",           epd.run),
    3: ("Search password in a wordlist", pdc.run_password_checker),
    4: ("Exit",                          None),
}

MENU_ICONS = {
    1: E("🔑", "[+]"),
    2: E("🔍", "[?]"),
    3: E("📋", "[~]"),
    4: E("🚪", "[x]"),
}

NOTE_MSG   = "NOTE: Enter the number of your choice only."
GITHUB_MSG = (
    f"  {E('⭐','*')}  If you liked this project, give it a star on GitHub "
    "and share it with your friends!"
)


# ══════════════════════════════════════════════════════════════
# [3] TERMINAL HELPERS
# ══════════════════════════════════════════════════════════════

def term_width() -> int:
    return shutil.get_terminal_size(fallback=(80, 24)).columns

def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")

def divider(char: str = "─", color: str = "cyan") -> None:
    print(colored(char * min(term_width(), 70), color))

def slow_print(text: str, delay: float = 0.025, color: str = "white") -> None:
    for ch in text:
        print(colored(ch, color), end="", flush=True)
        time.sleep(delay)
    print()

def fade_in(lines: list, color: str = "cyan", delay: float = 0.08) -> None:
    for line in lines:
        print(colored(line, color))
        time.sleep(delay)


# ══════════════════════════════════════════════════════════════
# [4] BANNER
# ══════════════════════════════════════════════════════════════

def show_banner() -> None:
    if os.path.isfile(IMAGE_PATH):
        try:
            ascii_magic.from_image(IMAGE_PATH).to_terminal(
                columns=80, char=" @#W$B%8&"
            )
            print()
            return
        except Exception:
            pass

    w = min(term_width(), 70)
    cprint("═" * w, "cyan")
    cprint("  Password Tool Suite".center(w), "cyan", attrs=["bold"])
    cprint("  Secure  ·  Fast  ·  Simple".center(w), "cyan")
    cprint("═" * w, "cyan")
    print()


# ══════════════════════════════════════════════════════════════
# [5] GITHUB STAR LINE
# ══════════════════════════════════════════════════════════════

def show_github_line() -> None:
    divider("─")
    cprint(GITHUB_MSG, "green")
    cprint(f"  {E('ℹ','i')}  {NOTE_MSG}", "yellow")
    divider("─")
    print()


# ══════════════════════════════════════════════════════════════
# [6] CLEAR-SCREEN PREFERENCE
# ══════════════════════════════════════════════════════════════

def ask_clear_screen() -> bool:
    print(colored(
        "\n  Clear the screen before showing the menu each time?\n"
        "  (Recommended for a cleaner look)",
        "cyan"
    ))
    while True:
        ans = input("  [y/n]  ==> ").strip().lower()
        if ans in ("y", "yes"): return True
        if ans in ("n", "no"):  return False
        print(colored(
            f"  {E('✖','X')}  Invalid input '{ans}' — please enter y or n.", "red"
        ))


# ══════════════════════════════════════════════════════════════
# [7] INTRO
# ══════════════════════════════════════════════════════════════

def intro() -> None:
    slow_print(
        f"\n  Welcome to Password Tool Suite! "
        f"{E('🔐','')} Your all-in-one password toolkit.\n",
        delay=0.03,
        color="cyan",
    )
    time.sleep(2)


# ══════════════════════════════════════════════════════════════
# [8] MENU
# ══════════════════════════════════════════════════════════════

def show_menu() -> None:
    w = min(term_width(), 70)
    cprint("  ┌" + "─" * (w - 4) + "┐", "cyan")
    cprint("  │" + "  M A I N   M E N U".center(w - 4) + "│", "cyan", attrs=["bold"])
    cprint("  ├" + "─" * (w - 4) + "┤", "cyan")

    for num, (label, _) in MENU_ITEMS.items():
        icon    = MENU_ICONS.get(num, "")
        content = f"  [{num}]  {icon}  {label}"
        padding = " " * max(0, w - 4 - len(content) + 2)
        line    = f"  │{content}{padding}│"
        color   = "red" if num == 4 else "white"
        cprint(line, color)

    cprint("  └" + "─" * (w - 4) + "┘", "cyan")
    print()


def get_user_choice():
    raw = input(colored("  ==> ", "cyan")).strip()

    if not raw:
        print(colored(
            f"  {E('✖','X')}  No input detected — please enter a number.", "red"
        ))
        return None

    if "." in raw:
        print(colored(
            f"  {E('✖','X')}  Decimal numbers not allowed. Enter a whole number.", "red"
        ))
        return None

    if not raw.isdigit():
        print(colored(
            f"  {E('✖','X')}  '{raw}' is not a valid number.", "red"
        ))
        return None

    choice = int(raw)
    if choice not in MENU_ITEMS:
        print(colored(
            f"  {E('✖','X')}  '{choice}' is out of range — choose 1 to {len(MENU_ITEMS)}.",
            "red"
        ))
        return None

    return choice


# ══════════════════════════════════════════════════════════════
# [9] MODULE RUNNER
# ══════════════════════════════════════════════════════════════

def run_module(choice: int) -> None:
    label, func = MENU_ITEMS[choice]

    clear()
    divider("═")
    cprint(f"  {E('▶','>>>')}  {label}", "cyan", attrs=["bold"])
    divider("═")
    print()

    try:
        func()
    except KeyboardInterrupt:
        print(colored(
            f"\n\n  {E('⚠','!')}  Interrupted — returning to menu.", "yellow"
        ))

    print()
    divider()
    input(colored(f"  {E('↩','<')}  Press Enter to return to the menu...", "cyan"))


# ══════════════════════════════════════════════════════════════
# [10] EXIT
# ══════════════════════════════════════════════════════════════

def graceful_exit() -> None:
    clear()
    show_banner()
    divider()
    fade_in([
        "  Thank you for using Password Tool Suite!",
        f"  Don't forget that {E('⭐','*')} on GitHub.",
        f"  {E('🔒','[lock]')}  Stay safe and secure!",
    ], color="green", delay=0.12)
    divider()
    print()
    time.sleep(1.5)
    sys.exit(0)


# ══════════════════════════════════════════════════════════════
# [11] CTRL+C HANDLER  — asked when Ctrl+C is pressed at the menu
# ══════════════════════════════════════════════════════════════

def handle_ctrl_c() -> None:
    """
    Called whenever Ctrl+C is caught at the main menu level.
    Warns the user, reminds them of [4], and asks whether to exit.
    """
    print()
    divider("─", "yellow")
    cprint(
        f"  {E('⚠','!')}  You pressed Ctrl+C.",
        "yellow", attrs=["bold"]
    )
    cprint(
        f"  {E('💡','Tip')}  Tip: next time you can press [4] from the menu "
        "to exit cleanly.",
        "yellow"
    )
    divider("─", "yellow")

    # ask whether to actually exit
    while True:
        try:
            ans = input(colored(
                f"\n  {E('🚪','[?]')}  Do you want to exit the program? [Y/N]\n"
                "  ==> ", "cyan"
            )).strip().lower()
        except KeyboardInterrupt:
            # pressed Ctrl+C again while answering → just exit
            print()
            graceful_exit()

        if ans in ("y", "yes"):
            graceful_exit()

        if ans in ("n", "no"):
            print(colored(
                f"  {E('↩','<')}  Returning to the menu...\n", "cyan"
            ))
            return

        print(colored(
            f"  {E('✖','X')}  Please enter Y or N.", "red"
        ))


# ══════════════════════════════════════════════════════════════
# [12] MAIN
# ══════════════════════════════════════════════════════════════

def main() -> None:

    # ── [A] preference ───────────────────────────────────────────
    auto_clear = ask_clear_screen()

    # ── [B] startup ──────────────────────────────────────────────
    if auto_clear:
        clear()

    show_banner()
    intro()

    # ── [C] main loop ─────────────────────────────────────────────
    first = True

    while True:
        if auto_clear and not first:
            clear()
            show_banner()

        first = False

        show_github_line()
        show_menu()

        # ── get choice — catch Ctrl+C at menu level ───────────────
        try:
            choice = get_user_choice()
        except KeyboardInterrupt:
            handle_ctrl_c()
            continue

        if choice is None:
            time.sleep(1.8)
            continue

        if choice == 4:
            graceful_exit()

        run_module(choice)


if __name__ == "__main__":
    main()
