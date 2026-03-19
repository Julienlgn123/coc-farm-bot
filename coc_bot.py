"""
CLASH OF CLANS — FARM BOT
Menu interactif dans le terminal (CMD)
Détection automatique de fin de combat via OCR du timer
"""

import os, sys, json, time, random, threading, msvcrt, re

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

try:
    from PIL import Image, ImageFilter, ImageEnhance
    HAS_PIL = True
except ImportError:
    os.system("pip install pillow -q")
    try:
        from PIL import Image, ImageFilter, ImageEnhance
        HAS_PIL = True
    except:
        HAS_PIL = False

try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    os.system("pip install pytesseract -q")
    try:
        import pytesseract
        HAS_TESSERACT = True
    except:
        HAS_TESSERACT = False

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
#  COORDONNÉES BOUTONS
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

# ══════════════════════════════════════════════════════════════════════════════
#  RÉGION DU TIMER — À AJUSTER SELON TON ÉCRAN
#
#  C'est la zone (x, y, largeur, hauteur) où le timer de combat s'affiche.
#  Pour trouver tes coordonnées :
#    1. Lance le script avec le menu
#    2. Va dans Configuration → "Calibrer le timer"
#    3. Ou utilise la fonction de debug ci-dessous
#
#  Exemple sur résolution 1920×1080 avec CoC en fenêtre :
#  Le timer est généralement en haut au centre de l'écran de combat.
# ══════════════════════════════════════════════════════════════════════════════
TIMER_REGION = (903, 44, 101, 56)   # (x, y, largeur, hauteur) — coordonnees exactes confirmees

# Délais (secondes)
DEPLOY_CLICK_DELAY     = 0.03
WAIT_BEFORE_DEPLOY     = 5      # attente avant de déployer les troupes
WAIT_AFTER_QUIT        = 5      # attente après avoir quitté le combat
WAIT_AFTER_TIMER_ZERO  = 2      # attente après détection du timer à 0
OCR_POLL_INTERVAL      = 0.1    # fréquence de lecture du timer (secondes)
TIMER_FALLBACK_SECONDS = 180    # quitte et relance si pas detecte en 3 min

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIG FILE PATH (compatible PyInstaller .exe)
# ══════════════════════════════════════════════════════════════════════════════
def _get_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(_get_base_dir(), "coc_configs.json")

# ══════════════════════════════════════════════════════════════════════════════
#  UTILS AFFICHAGE
# ══════════════════════════════════════════════════════════════════════════════
W = 60

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
            with open(CONFIG_FILE) as f:
                data = json.load(f)
            return data
        except:
            pass
    return {}

def save_configs(c):
    with open(CONFIG_FILE, "w") as f:
        json.dump(c, f, indent=2)

def load_timer_region():
    """Charge la région du timer depuis le fichier de config si elle existe."""
    global TIMER_REGION
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                data = json.load(f)
            if "_timer_region" in data:
                TIMER_REGION = tuple(data["_timer_region"])
        except:
            pass

def save_timer_region(region):
    """Sauvegarde la région du timer dans le fichier de config."""
    global TIMER_REGION
    TIMER_REGION = region
    configs = load_configs()
    configs["_timer_region"] = list(region)
    save_configs(configs)

# ══════════════════════════════════════════════════════════════════════════════
#  OCR — LECTURE DU TIMER
# ══════════════════════════════════════════════════════════════════════════════

def preprocess_timer_image(img):
    """
    Pré-traitement de l'image pour améliorer la lecture OCR du timer.
    Le timer CoC est généralement blanc/jaune sur fond sombre.
    """
    w, h = img.size
    img = img.resize((w * 3, h * 3), Image.LANCZOS)
    img = img.convert("L")
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(3.0)
    img = img.point(lambda p: 255 if p > 100 else 0)
    return img


# ──────────────────────────────────────────────────────────────────────────────
#  DÉTECTION PAR LUMINOSITÉ (sans Tesseract)
#
#  Principe :
#  Quand le combat est EN COURS, le timer affiche un chiffre blanc/jaune
#  lumineux ("180s", "45s"…) → la zone TIMER_REGION est CLAIRE.
#  Quand le timer atteint "0s", le chiffre disparait ou devient très petit
#  → la zone devient SOMBRE.
#
#  On mesure la luminosité moyenne de la zone toutes les 0.5s.
#  On calibre automatiquement un seuil lors des premières secondes (combat actif).
#  Dès que la luminosité passe sous le seuil → fin de combat détectée.
# ──────────────────────────────────────────────────────────────────────────────

def capture_timer_region():
    """Capture la zone TIMER_REGION et retourne l'image PIL ou None."""
    if not HAS_PYAUTOGUI or not HAS_PIL:
        return None
    try:
        x, y, w, h = TIMER_REGION
        return pyautogui.screenshot(region=(x, y, w, h))
    except Exception:
        return None


def get_zone_brightness(img):
    """
    Retourne la luminosité moyenne [0-255] de l'image.
    Les pixels blancs/jaunes (chiffre du timer) sont très lumineux.
    """
    gray = img.convert("L")
    pixels = list(gray.getdata())
    return sum(pixels) / len(pixels)


def get_bright_pixel_ratio(img, threshold=180):
    """
    Retourne le ratio [0.0-1.0] de pixels plus lumineux que `threshold`.
    Un gros chiffre blanc dans la zone → ratio élevé (~0.15 à 0.40).
    Zone vide/sombre → ratio très bas (~0.01 à 0.05).
    """
    gray = img.convert("L")
    pixels = list(gray.getdata())
    bright = sum(1 for p in pixels if p > threshold)
    return bright / len(pixels)

# ══════════════════════════════════════════════════════════════════════════════
#  BOT LOOP
# ══════════════════════════════════════════════════════════════════════════════
stop_event = threading.Event()

def wait_simple(secs, label=""):
    """Attente simple avec barre de progression."""
    if label:
        print(DIM + f"  ⏳ {label}" + RESET)
    end = time.time() + secs
    while time.time() < end:
        if stop_event.is_set():
            return
        rem  = int(end - time.time())
        m, s = divmod(rem, 60)
        done = secs - rem
        bar  = progress_bar(done, secs, 28)
        print(f"\r  {CYAN}{m:02d}:{s:02d}{RESET}  {bar}  ", end="", flush=True)
        time.sleep(0.5)
    print()


def wait_for_combat_end(fallback_seconds=TIMER_FALLBACK_SECONDS):
    """
    Attend la fin du combat en surveillant la luminosité de la zone du timer.

    Stratégie :
    - Pendant les 8 premières secondes (calibration) : mesure la luminosité
      de base quand le timer affiche un gros chiffre (zone claire).
    - Ensuite : si la luminosité chute sous 40% de la valeur de référence
      pendant 3 captures consécutives → fin de combat détectée.
    - Fallback temporel si PIL non disponible ou calibration impossible.
    """
    if not HAS_PYAUTOGUI or not HAS_PIL:
        warn("PIL non disponible — mode fallback temporel.")
        wait_simple(fallback_seconds, f"Attente fin de combat ({fallback_seconds}s)...")
        return not stop_event.is_set()

    print()

    start_time     = time.time()
    ref_brightness = None      # luminosite de reference (timer actif)
    ref_ratio      = None      # ratio pixels brillants de reference
    calibration_samples = []   # echantillons pendant la phase de calibration
    CALIBRATION_SECS = 8       # duree de la calibration en secondes
    DARK_THRESHOLD   = 0.50    # si luminosite < 50% de la ref → timer eteint
    RATIO_THRESHOLD  = 0.03    # ratio absolu sous lequel on considere la zone vide
    dark_count     = 0
    CONFIRM_COUNT  = 3
    FALLBACK_SECS  = 180           # 3 min sans detection → quitte et relance

    while not stop_event.is_set():
        elapsed = time.time() - start_time
        elapsed_m, elapsed_s = divmod(int(elapsed), 60)

        img = capture_timer_region()
        if img is None:
            time.sleep(OCR_POLL_INTERVAL)
            continue

        brightness = get_zone_brightness(img)
        ratio      = get_bright_pixel_ratio(img, threshold=180)

        # ── Phase calibration ────────────────────────────────────────────────
        if elapsed < CALIBRATION_SECS:
            calibration_samples.append((brightness, ratio))
            bar_w = int((elapsed / CALIBRATION_SECS) * 20)
            bar   = "\u2588" * bar_w + "\u2591" * (20 - bar_w)
            print(
                f"\r  Calibration {GREEN}{bar}{RESET}"
                f"  lum={brightness:.1f}  ratio={ratio:.3f}          ",
                end="", flush=True
            )
            time.sleep(OCR_POLL_INTERVAL)
            continue

        # Fin de calibration : calcul de la reference
        if ref_brightness is None and calibration_samples:
            ref_brightness = max(b for b, r in calibration_samples)
            ref_ratio      = max(r for b, r in calibration_samples)
            print()
            info(f"Ref : lum={ref_brightness:.1f}  seuil={ref_brightness * DARK_THRESHOLD:.1f}  ratio_min={RATIO_THRESHOLD:.3f}")
            print()

        if ref_brightness is None:
            warn("Calibration impossible — fallback.")
            wait_simple(FALLBACK_SECS, f"Attente ({FALLBACK_SECS}s)...")
            return not stop_event.is_set()

        lum_dark  = brightness < ref_brightness * DARK_THRESHOLD
        ratio_dark = ratio < RATIO_THRESHOLD
        is_dark   = lum_dark or ratio_dark

        # Chaque capture sombre incremente — jamais de reset
        if is_dark:
            dark_count += 1

        state_str = RED + "SOMBRE" + RESET if is_dark else GREEN + "ACTIF " + RESET
        print(
            f"\r  Timer {state_str}"
            f"  lum={brightness:5.1f}/{ref_brightness:.1f}"
            f"  ratio={ratio:.3f}"
            f"  [{dark_count}/{CONFIRM_COUNT}]"
            f"  ecoule {elapsed_m:02d}:{elapsed_s:02d}     ",
            end="", flush=True
        )

        if dark_count >= CONFIRM_COUNT:
            print()
            success("Timer a 0s detecte ! Fin du combat.")
            return True

        # 3 min sans aucune capture sombre → quitte et relance
        if elapsed > FALLBACK_SECS and dark_count == 0:
            print()
            warn("3 min sans detection sombre — relance du combat.")
            return not stop_event.is_set()

        time.sleep(OCR_POLL_INTERVAL)

    print()
    return False


def bot_loop(troop_counts):
    if not HAS_PYAUTOGUI:
        error("pyautogui manquant — pip install pyautogui")
        return

    pyautogui.FAILSAFE = True
    pyautogui.PAUSE    = 0.0

    def clic(x, y, label=""):
        pyautogui.moveTo(
            x + random.randint(-2, 2),
            y + random.randint(-2, 2),
            duration=random.uniform(0.08, 0.18)
        )
        pyautogui.click()
        if label:
            print(ORANGE + f"  ► {label}" + RESET)
        time.sleep(random.uniform(0.06, 0.12))

    loop = 0
    while not stop_event.is_set():
        loop += 1
        print()
        line("─", GOLD)
        print(GOLD + f"  BOUCLE #{loop}" + RESET)
        line("─", GOLD)

        try:
            # ── 1. Lancer la recherche ───────────────────────────────────────
            clic(*BTN_ATTACK,        "Bouton Attaquer")
            time.sleep(0.5)
            clic(*BTN_FIND_MATCH,    "Trouver une partie")
            time.sleep(0.5)
            clic(*BTN_LAUNCH_SEARCH, "Lancer la recherche")
            time.sleep(0.8)
            if stop_event.is_set():
                break

            # ── 2. Attente avant déploiement ────────────────────────────────
            wait_simple(WAIT_BEFORE_DEPLOY, f"Attente {WAIT_BEFORE_DEPLOY}s avant déploiement...")
            if stop_event.is_set():
                break

            # ── 3. Déploiement des troupes ──────────────────────────────────
            print(CYAN + "  ━━  DÉPLOIEMENT DES TROUPES  ━━" + RESET)
            for i, count in enumerate(troop_counts):
                if stop_event.is_set():
                    break
                if count == 0:
                    continue
                print(
                    f"  {DIM}Slot {i+1:02d}{RESET}  "
                    f"{WHITE}{count} clics{RESET}  "
                    f"{progress_bar(count, 50, 20)}"
                )
                pyautogui.moveTo(
                    TROOP_POSITIONS[i][0],
                    TROOP_POSITIONS[i][1],
                    duration=0.07
                )
                pyautogui.click()
                time.sleep(0.04)
                dx, dy = DEPLOY_POINT
                for _ in range(count):
                    if stop_event.is_set():
                        break
                    pyautogui.click(
                        dx + random.randint(-5, 5),
                        dy + random.randint(-5, 5)
                    )
                    time.sleep(DEPLOY_CLICK_DELAY)

            if stop_event.is_set():
                break
            success("Toutes les troupes déployées !")

            # ── 4. Attente fin de combat (OCR timer) ────────────────────────
            print()
            combat_ended = wait_for_combat_end(fallback_seconds=TIMER_FALLBACK_SECONDS)

            if not combat_ended or stop_event.is_set():
                break

            # ── 5. Attente post-timer puis quitter ──────────────────────────
            wait_simple(WAIT_AFTER_TIMER_ZERO, f"Attente {WAIT_AFTER_TIMER_ZERO}s avant de quitter...")
            if stop_event.is_set():
                break

            clic(*BTN_QUIT_COMBAT, "Quitter le combat")
            wait_simple(WAIT_AFTER_QUIT, f"Retour au village ({WAIT_AFTER_QUIT}s)...")
            success(f"Boucle #{loop} terminée !\n")

        except Exception as e:
            if "FailSafe" in type(e).__name__:
                print()
                error("FAILSAFE — souris coin haut-gauche. Arrêt.")
                break
            error(f"Erreur : {e}")
            time.sleep(5)

    print()
    line("═", RED)
    print(RED + f"  Bot arrêté après {loop} boucle(s)." + RESET)
    line("═", RED)

# ══════════════════════════════════════════════════════════════════════════════
#  CALIBRATION DU TIMER
# ══════════════════════════════════════════════════════════════════════════════

def menu_calibrate_timer():
    """
    Aide l'utilisateur à définir la zone du timer sur son écran.
    Affiche un aperçu OCR en temps réel pour valider la région.
    """
    title_banner()
    box_row("CALIBRATION DU TIMER", GOLD, CYAN)
    box_empty(GOLD)
    box_row("Définit la zone de capture du timer de combat.", GOLD, DIM)
    box_bot(GOLD)

    if not HAS_PIL or not HAS_TESSERACT:
        section("DÉPENDANCES MANQUANTES", RED)
        error("Pillow et/ou pytesseract non installés.")
        info("pip install pillow pytesseract")
        info("Puis installe Tesseract OCR : https://github.com/UB-Mannheim/tesseract/wiki")
        press_any()
        return

    section("RÉGION ACTUELLE", CYAN)
    x, y, w, h = TIMER_REGION
    print(f"  {WHITE}x={x}  y={y}  largeur={w}  hauteur={h}{RESET}")
    print()

    section("MODIFIER LA RÉGION", CYAN)
    info("Entre les nouvelles coordonnées (laisse vide pour garder la valeur actuelle)")
    print()

    def ask_int(label, default):
        val = prompt(f"{label} [{default}] :").strip()
        if val == "":
            return default
        try:
            return int(val)
        except:
            return default

    nx = ask_int("  x (coin gauche)", x)
    ny = ask_int("  y (coin haut)",   y)
    nw = ask_int("  largeur",         w)
    nh = ask_int("  hauteur",         h)
    new_region = (nx, ny, nw, nh)

    section("TEST OCR EN DIRECT", GREEN)
    info("Place-toi en combat dans CoC pour voir le timer.")
    info("Appuie sur Q pour arrêter le test et sauvegarder.")
    print()

    test_stop = threading.Event()

    def ocr_test_loop():
        import msvcrt as _m
        while not test_stop.is_set():
            # Vérifier si 'q' pressé (non-bloquant)
            if _m.kbhit():
                ch = _m.getch().lower()
                if ch == b'q':
                    test_stop.set()
                    break

            # Capture et OCR
            try:
                screenshot = pyautogui.screenshot(region=(nx, ny, nw, nh))
                processed  = preprocess_timer_image(screenshot)
                cfg        = r"--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789s"
                raw        = pytesseract.image_to_string(processed, config=cfg).strip()
                secs       = parse_timer_seconds(raw)

                if secs is not None:
                    m, s = divmod(secs, 60)
                    status = f"{GREEN}{m}:{s:02d} ({secs}s){RESET}"
                    zero   = f"  {RED}← FIN DÉTECTÉE{RESET}" if secs == 0 else ""
                else:
                    status = f"{RED}Non reconnu{RESET}"
                    zero   = ""

                print(
                    f"\r  OCR brut: {CYAN}\"{raw}\"{RESET}   "
                    f"Interprété: {status}{zero}        ",
                    end="", flush=True
                )
            except Exception as e:
                print(f"\r  Erreur OCR: {e}        ", end="", flush=True)

            time.sleep(1.5)

    t = threading.Thread(target=ocr_test_loop, daemon=True)
    t.start()
    t.join()

    print()
    confirm = prompt(f"Sauvegarder la région ({nx},{ny},{nw},{nh}) ? (o/n) :").strip().lower()
    if confirm == "o":
        save_timer_region(new_region)
        success("Région du timer sauvegardée !")
    else:
        warn("Annulé — région inchangée.")
    press_any()

# ══════════════════════════════════════════════════════════════════════════════
#  MENUS
# ══════════════════════════════════════════════════════════════════════════════

def menu_main(configs):
    load_timer_region()   # Charge la région sauvegardée au démarrage

    while True:
        title_banner()
        box_row("MENU PRINCIPAL", GOLD, WHITE)
        box_empty(GOLD)

        nb       = len([k for k in configs if not k.startswith("_")])
        cfg_info = f"{nb} config(s) enregistrée(s)" if nb else "Aucune config"

        # Statut OCR
        ocr_ok = HAS_PIL and HAS_TESSERACT
        ocr_status = f"OCR timer : {'✓ actif' if ocr_ok else '✗ désactivé (fallback)'}"
        box_row(cfg_info,   GOLD, DIM)
        box_row(ocr_status, GOLD, GREEN if ocr_ok else RED)
        box_row(f"Zone timer : {TIMER_REGION}", GOLD, DIM)
        box_bot(GOLD)

        section("OPTIONS")
        opt(1, "AUTO FARM",          "Lancer le bot de farming",          GREEN)
        opt(2, "CONFIGURATION",      "Gérer les configs de troupes",      CYAN)
        opt(3, "CALIBRER LE TIMER",  "Définir la zone OCR du timer",      ORANGE)
        opt(4, "QUITTER",            "",                                   RED)

        choice = prompt("Ton choix (1/2/3/4) :")

        if choice == "1":
            configs = menu_farm(configs)
        elif choice == "2":
            configs = menu_config(configs)
        elif choice == "3":
            menu_calibrate_timer()
        elif choice == "4":
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

    print()
    section("RÉSUMÉ", GREEN)
    total = 0
    for i, c in enumerate(counts):
        if c > 0:
            bar = progress_bar(c, max(counts + [1]), 20)
            print(f"  Slot {i+1:02d}  {WHITE}{c:>4} clics{RESET}  {bar}")
            total += c
        else:
            print(f"  {DIM}Slot {i+1:02d}  —  ignoré{RESET}")
    print()
    info(f"Total : {total} clics pour {sum(1 for c in counts if c > 0)} slot(s) actif(s)")

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

    names = [k for k in configs if not k.startswith("_")]
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
    except:
        pass
    return configs


def menu_delete_config(configs):
    title_banner()
    box_row("SUPPRIMER UNE CONFIG", GOLD, RED)
    box_bot(GOLD)
    section("CONFIGS DISPONIBLES", RED)

    names = [k for k in configs if not k.startswith("_")]
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

    user_configs = {k: v for k, v in configs.items() if not k.startswith("_")}

    if user_configs:
        names = list(user_configs.keys())
        for i, name in enumerate(names):
            active = [(j, c) for j, c in enumerate(user_configs[name]) if c > 0]
            total  = sum(c for _, c in active)
            slots  = "  ".join([f"S{j+1}:{c}" for j, c in active]) if active else "vide"
            print(f"  {GREEN}[{i+1}]{RESET} {WHITE}{name}{RESET}")
            print(f"      {DIM}{slots}{RESET}  {CYAN}({total} clics / {len(active)} slots){RESET}")
            print()
        opt(len(names) + 1, "Mode défaut", "50 clics × 11 slots", ORANGE)
        opt(0, "Retour", "", DIM)

        choice = prompt("Ton choix :")
        try:
            c = int(choice)
            if c == 0:
                return configs
            elif 1 <= c <= len(names):
                counts = user_configs[names[c - 1]]
            elif c == len(names) + 1:
                counts = [50] * 11
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
            counts = [50] * 11
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
        except:
            pass
    threading.Thread(target=esc_listener, daemon=True).start()

    # Compte à rebours
    for i in range(5, 0, -1):
        print(f"\r  {GOLD}{i}...{RESET}  ", end="", flush=True)
        time.sleep(1)
    print(f"\r  {GREEN}GO !{RESET}        ")
    print()

    bot_loop(counts)

    print()
    press_any()
    return configs

# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    configs = load_configs()
    menu_main(configs)