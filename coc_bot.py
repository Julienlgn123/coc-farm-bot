"""
CLASH OF CLANS — FARM BOT
Menu interactif dans le terminal (CMD)
"""

import os, sys, json, time, random, threading, msvcrt

try:
    import colorama
    from colorama import Fore, Back, Style
    colorama.init()
except ImportError:
    os.system("pip install colorama -q")
    import colorama
    from colorama import Fore, Back, Style
    colorama.init()

try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

# ══════════════════════════════════════════════════════════════════════════════
#  COULEURS
# ══════════════════════════════════════════════════════════════════════════════
GOLD   = Fore.YELLOW + Style.BRIGHT
CYAN   = Fore.CYAN   + Style.BRIGHT
GREEN  = Fore.GREEN  + Style.BRIGHT
RED    = Fore.RED    + Style.BRIGHT
ORANGE = Fore.YELLOW
WHITE  = Fore.WHITE  + Style.BRIGHT
DIM    = Fore.WHITE  + Style.DIM
BLUE   = Fore.BLUE   + Style.BRIGHT
RESET  = Style.RESET_ALL

# ══════════════════════════════════════════════════════════════════════════════
#  COORDONNÉES
# ══════════════════════════════════════════════════════════════════════════════
BTN_ATTACK        = (102,  977)
BTN_FIND_MATCH    = (296,  745)
BTN_LAUNCH_SEARCH = (1604, 926)
DEPLOY_POINT      = (191,  509)
BTN_QUIT_COMBAT   = (964,  891)

TROOP_POSITIONS = [
    (344,992),(475,990),(593,992),(725,993),(849,996),
    (968,1000),(1088,987),(1219,990),(1336,986),(1448,988),(1580,983),
]

DEPLOY_CLICK_DELAY = 0.03
WAIT_BEFORE_DEPLOY = 10
WAIT_AFTER_DEPLOY  = 190
WAIT_AFTER_QUIT    = 5
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coc_configs.json")

# ══════════════════════════════════════════════════════════════════════════════
#  UTILS AFFICHAGE
# ══════════════════════════════════════════════════════════════════════════════
W = 60  # largeur du cadre

def clr():
    os.system("cls" if os.name == "nt" else "clear")

def line(char="═", color=GOLD):
    print(color + char * W + RESET)

def box_top(color=GOLD):
    print(color + "╔" + "═" * (W-2) + "╗" + RESET)

def box_bot(color=GOLD):
    print(color + "╚" + "═" * (W-2) + "╝" + RESET)

def box_mid(color=GOLD):
    print(color + "╠" + "═" * (W-2) + "╣" + RESET)

def box_row(text="", color=GOLD, text_color=WHITE, align="center"):
    inner = W - 4
    if align == "center":
        padded = text.center(inner)
    elif align == "left":
        padded = " " + text.ljust(inner - 1)
    else:
        padded = text.rjust(inner) + " "
    print(color + "║ " + RESET + text_color + padded + RESET + color + " ║" + RESET)

def box_empty(color=GOLD):
    print(color + "║" + " " * (W-2) + "║" + RESET)

def title_banner():
    clr()
    box_top(GOLD)
    box_empty(GOLD)
    box_row("⚔  CLASH OF CLANS  ⚔", GOLD, GOLD)
    box_row("A U T O   F A R M   B O T", GOLD, ORANGE)
    box_empty(GOLD)
    box_mid(GOLD)

def section(title, color=CYAN):
    print()
    print(color + "┌─ " + RESET + WHITE + title + RESET + color + " " + "─" * (W - len(title) - 4) + RESET)

def opt(num, label, desc="", color=CYAN):
    num_str = f"  [{color}{num}{RESET}]"
    label_str = f" {WHITE}{label}{RESET}"
    desc_str  = f"  {DIM}{desc}{RESET}" if desc else ""
    print(num_str + label_str + desc_str)

def prompt(msg):
    print()
    print(CYAN + "  ▶  " + RESET + WHITE + msg + RESET + " ", end="")
    return input()

def success(msg):
    print(GREEN + "  ✓  " + RESET + msg)

def error(msg):
    print(RED + "  ✗  " + RESET + msg)

def info(msg):
    print(CYAN + "  •  " + RESET + DIM + msg + RESET)

def warn(msg):
    print(ORANGE + "  !  " + RESET + msg)

def press_any():
    print()
    print(DIM + "  Appuie sur une touche pour continuer..." + RESET, end="", flush=True)
    msvcrt.getch()

def progress_bar(val, total, width=30, color=GREEN):
    filled = int(width * val / max(total, 1))
    bar = "█" * filled + "░" * (width - filled)
    pct = int(100 * val / max(total, 1))
    return color + bar + RESET + DIM + f" {pct:3d}%" + RESET

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGS
# ══════════════════════════════════════════════════════════════════════════════
def load_configs():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f: return json.load(f)
        except: pass
    return {}

def save_configs(c):
    with open(CONFIG_FILE, "w") as f: json.dump(c, f, indent=2)

# ══════════════════════════════════════════════════════════════════════════════
#  BOT LOOP
# ══════════════════════════════════════════════════════════════════════════════
stop_event = threading.Event()

def bot_loop(troop_counts):
    if not HAS_PYAUTOGUI:
        error("pyautogui manquant — pip install pyautogui"); return
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE    = 0.0

    def clic(x, y, label=""):
        pyautogui.moveTo(x+random.randint(-2,2), y+random.randint(-2,2),
                         duration=random.uniform(0.08,0.18))
        pyautogui.click()
        if label: print(ORANGE + f"  ► {label}" + RESET)
        time.sleep(random.uniform(0.06,0.12))

    def wait(secs, label=""):
        if label: print(DIM + f"  ⏳ {label}" + RESET)
        end = time.time() + secs
        while time.time() < end:
            if stop_event.is_set(): return
            rem   = int(end - time.time())
            m, s  = divmod(rem, 60)
            done  = secs - rem
            bar   = progress_bar(done, secs, 28)
            print(f"\r  {CYAN}{m:02d}:{s:02d}{RESET}  {bar}  ", end="", flush=True)
            time.sleep(0.5)
        print()

    loop = 0
    while not stop_event.is_set():
        loop += 1
        print()
        line("─", GOLD)
        print(GOLD + f"  BOUCLE #{loop}" + RESET)
        line("─", GOLD)

        try:
            clic(*BTN_ATTACK,        "Bouton Attaquer")
            time.sleep(0.5)
            clic(*BTN_FIND_MATCH,    "Trouver une partie")
            time.sleep(0.5)
            clic(*BTN_LAUNCH_SEARCH, "Lancer la recherche")
            time.sleep(0.8)
            if stop_event.is_set(): break

            wait(WAIT_BEFORE_DEPLOY, f"Attente {WAIT_BEFORE_DEPLOY}s avant déploiement...")
            if stop_event.is_set(): break

            print(CYAN + "  ━━  DÉPLOIEMENT DES TROUPES  ━━" + RESET)
            for i, count in enumerate(troop_counts):
                if stop_event.is_set(): break
                if count == 0: continue
                print(f"  {DIM}Slot {i+1:02d}{RESET}  {WHITE}{count} clics{RESET}  {progress_bar(count, 50, 20)}")
                pyautogui.moveTo(TROOP_POSITIONS[i][0], TROOP_POSITIONS[i][1], duration=0.07)
                pyautogui.click(); time.sleep(0.04)
                dx, dy = DEPLOY_POINT
                for _ in range(count):
                    if stop_event.is_set(): break
                    pyautogui.click(dx+random.randint(-5,5), dy+random.randint(-5,5))
                    time.sleep(DEPLOY_CLICK_DELAY)

            if stop_event.is_set(): break
            success("Toutes les troupes déployées !")

            wait(WAIT_AFTER_DEPLOY, "Attente fin de combat (3m10s)...")
            if stop_event.is_set(): break

            clic(*BTN_QUIT_COMBAT, "Quitter le combat")
            wait(WAIT_AFTER_QUIT,  f"Retour au village ({WAIT_AFTER_QUIT}s)...")
            success(f"Boucle #{loop} terminée !\n")

        except Exception as e:
            if "FailSafe" in type(e).__name__:
                print(); error("FAILSAFE — souris coin haut-gauche. Arrêt."); break
            error(f"Erreur : {e}"); time.sleep(5)

    print()
    line("═", RED)
    print(RED + f"  Bot arrêté après {loop} boucle(s)." + RESET)
    line("═", RED)

# ══════════════════════════════════════════════════════════════════════════════
#  MENUS
# ══════════════════════════════════════════════════════════════════════════════

def menu_main(configs):
    while True:
        title_banner()
        box_row("MENU PRINCIPAL", GOLD, WHITE)
        box_empty(GOLD)

        nb = len(configs)
        cfg_info = f"{nb} config(s) enregistrée(s)" if nb else "Aucune config"
        box_row(cfg_info, GOLD, DIM)
        box_bot(GOLD)

        section("OPTIONS")
        opt(1, "AUTO FARM",     "Lancer le bot de farming", GREEN)
        opt(2, "CONFIGURATION", "Gérer les configs de troupes", CYAN)
        opt(3, "QUITTER",       "", RED)

        choice = prompt("Ton choix (1/2/3) :")

        if choice == "1":
            configs = menu_farm(configs)
        elif choice == "2":
            configs = menu_config(configs)
        elif choice == "3":
            clr()
            print(GOLD + "  À bientôt chef !" + RESET)
            sys.exit(0)
        else:
            error("Choix invalide.")
            time.sleep(1)


def menu_config(configs):
    while True:
        title_banner()
        box_row("CONFIGURATION DES TROUPES", GOLD, CYAN)
        box_empty(GOLD)
        box_row("Définis le nombre de clics par slot de troupe.", GOLD, DIM)
        box_row("Les slots à 0 seront ignorés lors du déploiement.", GOLD, DIM)
        box_bot(GOLD)

        section("OPTIONS CONFIG", CYAN)
        opt(1, "Nouvelle configuration", "", GREEN)
        if configs:
            opt(2, "Modifier une config existante", "", CYAN)
            opt(3, "Supprimer une config", "", RED)
        opt(0, "Retour au menu principal", "", DIM)

        choice = prompt("Ton choix :")

        if choice == "1":
            configs = menu_new_config(configs)
        elif choice == "2" and configs:
            configs = menu_edit_config(configs)
        elif choice == "3" and configs:
            configs = menu_delete_config(configs)
        elif choice == "0":
            return configs
        else:
            error("Choix invalide."); time.sleep(1)


def menu_new_config(configs, existing_name=None, prefill=None):
    title_banner()
    box_row("NOUVELLE CONFIGURATION", GOLD, CYAN)
    box_bot(GOLD)

    section("SAISIE DES TROUPES", CYAN)
    print()

    counts = []
    pf = prefill or [0] * 11

    for i in range(11):
        while True:
            default = pf[i]
            val_str = prompt(f"  Slot {i+1:02d} — Troupe {i+1} (clics) [{default}] :")
            val_str = val_str.strip()
            if val_str == "":
                counts.append(default); break
            try:
                v = int(val_str)
                if v < 0: raise ValueError
                counts.append(v); break
            except:
                error("Entre un nombre entier ≥ 0.")

    # Résumé
    print()
    section("RÉSUMÉ", GREEN)
    total = 0
    for i, c in enumerate(counts):
        if c > 0:
            bar = progress_bar(c, max(counts+[1]), 20)
            print(f"  Slot {i+1:02d}  {WHITE}{c:>4} clics{RESET}  {bar}")
            total += c
        else:
            print(f"  {DIM}Slot {i+1:02d}  —  ignoré{RESET}")
    print()
    info(f"Total : {total} clics pour {sum(1 for c in counts if c>0)} slot(s) actif(s)")

    print()
    if existing_name:
        name = existing_name
    else:
        name = prompt("Nom de la configuration :").strip()
        if not name:
            error("Nom vide, annulé."); press_any(); return configs

    confirm = prompt(f"Sauvegarder « {name} » ? (o/n) :").strip().lower()
    if confirm == "o":
        configs[name] = counts
        save_configs(configs)
        success(f"Config « {name} » sauvegardée !")
    else:
        warn("Annulé.")
    press_any()
    return configs


def menu_edit_config(configs):
    title_banner()
    box_row("MODIFIER UNE CONFIG", GOLD, CYAN)
    box_bot(GOLD)
    section("CONFIGS DISPONIBLES", CYAN)

    names = list(configs.keys())
    for i, n in enumerate(names):
        active = sum(1 for c in configs[n] if c > 0)
        total  = sum(configs[n])
        print(f"  {CYAN}[{i+1}]{RESET} {WHITE}{n}{RESET}  {DIM}({active} slots, {total} clics){RESET}")

    opt(0, "Retour", "", DIM)
    choice = prompt("Config à modifier (numéro) :")
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(names):
            name = names[idx]
            return menu_new_config(configs, existing_name=name, prefill=configs[name])
    except: pass
    return configs


def menu_delete_config(configs):
    title_banner()
    box_row("SUPPRIMER UNE CONFIG", GOLD, RED)
    box_bot(GOLD)
    section("CONFIGS DISPONIBLES", RED)

    names = list(configs.keys())
    for i, n in enumerate(names):
        print(f"  {RED}[{i+1}]{RESET} {WHITE}{n}{RESET}")
    opt(0, "Retour", "", DIM)

    choice = prompt("Config à supprimer (numéro) :")
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(names):
            name = names[idx]
            confirm = prompt(f"Supprimer « {name} » ? (o/n) :").strip().lower()
            if confirm == "o":
                del configs[name]; save_configs(configs)
                success(f"« {name} » supprimée.")
            else:
                warn("Annulé.")
    except:
        error("Choix invalide.")
    press_any()
    return configs


def menu_farm(configs):
    title_banner()
    box_row("AUTO FARM", GOLD, GREEN)
    box_bot(GOLD)

    section("CHOISIR UN MODE", GREEN)

    if configs:
        names = list(configs.keys())
        print(f"  {DIM}0 configs disponibles :{RESET}")
        print()
        for i, name in enumerate(names):
            active = [(j,c) for j,c in enumerate(configs[name]) if c > 0]
            total  = sum(c for _,c in active)
            slots  = "  ".join([f"S{j+1}:{c}" for j,c in active]) if active else "vide"
            print(f"  {GREEN}[{i+1}]{RESET} {WHITE}{name}{RESET}")
            print(f"      {DIM}{slots}{RESET}  {CYAN}({total} clics / {len(active)} slots){RESET}")
            print()
        opt(len(names)+1, "Mode défaut", "50 clics × 11 slots", ORANGE)
        opt(0, "Retour", "", DIM)

        choice = prompt("Ton choix :")
        try:
            c = int(choice)
            if c == 0:
                return configs
            elif 1 <= c <= len(names):
                counts = configs[names[c-1]]
            elif c == len(names)+1:
                counts = [50]*11
            else:
                error("Choix invalide."); press_any(); return configs
        except:
            error("Choix invalide."); press_any(); return configs
    else:
        warn("Aucune configuration — mode défaut (50 clics par slot).")
        opt(1, "Lancer en mode défaut", "50 clics × 11 slots", GREEN)
        opt(0, "Retour au menu", "", DIM)
        choice = prompt("Ton choix (1/0) :")
        if choice == "1":
            counts = [50]*11
        else:
            return configs

    # ── Confirmation & démarrage ─────────────────────────────────────────────
    clr()
    title_banner()
    box_row("DÉMARRAGE DU BOT", GOLD, GREEN)
    box_empty(GOLD)
    box_row("Le bot va démarrer dans 5 secondes.", GOLD, WHITE)
    box_row("Bascule sur Clash of Clans maintenant !", GOLD, ORANGE)
    box_empty(GOLD)
    box_row("ESC  →  arrêt d'urgence", GOLD, DIM)
    box_row("Souris coin haut-gauche  →  failsafe", GOLD, DIM)
    box_bot(GOLD)
    print()

    stop_event.clear()

    # Thread qui écoute ESC
    def esc_listener():
        try:
            import keyboard
            keyboard.wait("esc")
            if not stop_event.is_set():
                stop_event.set()
                print()
                warn("ESC pressé — arrêt en cours...")
        except: pass
    threading.Thread(target=esc_listener, daemon=True).start()

    # Compte à rebours
    for i in range(5, 0, -1):
        print(f"\r  {GOLD}{i}...{RESET}  ", end="", flush=True)
        time.sleep(1)
    print(f"\r  {GREEN}GO !{RESET}        ")
    print()

    # Lancement bot
    bot_loop(counts)

    print()
    press_any()
    return configs

# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    configs = load_configs()
    menu_main(configs)