# ⚔️ COC Farm Bot

> Bot de farming automatique pour **Clash of Clans** — déploie toutes tes troupes en boucle, sans intervention.

---

## 📋 Sommaire

- [Comment ça fonctionne](#-comment-ça-fonctionne)
- [Résolution d'écran requise](#-résolution-décran-requise)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Compiler en .exe](#-compiler-en-exe)
- [Push sur GitHub](#-push-sur-github)

---

## ⚙️ Comment ça fonctionne

Le bot utilise **PyAutoGUI** pour simuler des clics de souris à des coordonnées précises sur ton écran. Il tourne en boucle dans le terminal et reproduit exactement les mêmes actions qu'un joueur humain.

### Séquence d'une boucle complète

```
1.  Clic sur "Attaquer"              (102, 977)
2.  Clic sur "Trouver une partie"    (296, 745)
3.  Clic sur "Lancer la recherche"   (1604, 926)
     │
     └─ Attente 10s  (chargement du village ennemi)
     │
4.  Pour chaque troupe (Slot 1 → 11) :
       • Clic sur la troupe dans la barre du bas
       • N clics rapides sur le point de déploiement  (191, 509)
     │
     └─ Attente 3 minutes 10s  (durée du combat)
     │
5.  Clic sur "Quitter le combat"     (964, 891)
     │
     └─ Attente 5s  (retour au village)
     │
     └─ RECOMMENCE
```

### Système de configurations

Tu peux sauvegarder plusieurs **profils de troupes** dans `coc_configs.json`.
Chaque profil définit le **nombre de clics** à effectuer pour chaque slot de troupe.
Les slots à `0` sont ignorés — le bot les saute automatiquement.

Exemple de config :
```json
{
  "Ma config": [30, 30, 0, 0, 50, 50, 0, 0, 0, 0, 20]
}
```
Slot 1 : 30 clics, Slot 2 : 30 clics, Slot 5 : 50 clics, etc.

### Arrêt d'urgence

| Méthode | Effet |
|---------|-------|
| `ESC` dans le terminal | Arrêt propre après l'action en cours |
| Souris coin haut-gauche | Arrêt immédiat (PyAutoGUI FailSafe) |

---

## 🖥️ Résolution d'écran requise

> **Les coordonnées sont calibrées pour une résolution de `1920 x 1080` (Full HD).**

Le bot clique sur des pixels fixes. Si ta résolution est différente, les clics seront décalés et le bot ne fonctionnera pas correctement.

| Résolution | Compatibilité |
|------------|--------------|
| 1920 x 1080 | Fonctionne parfaitement |
| Autre résolution | Recalibration nécessaire |

### Recalibrer pour une autre résolution

Lance l'outil de calibration fourni :

```bash
python coc_calibration.py
```

Une fenêtre s'ouvre avec ton écran en direct + une grille de coordonnées.
Survole les boutons avec ta souris pour lire leurs coordonnées exactes,
puis mets à jour les valeurs en haut de `coc_bot.py`.

### Écran principal uniquement

Le bot capture et clique **toujours sur l'écran principal** (moniteur n°1).
Si tu as plusieurs écrans, assure-toi que **Clash of Clans est en plein écran sur l'écran principal**.

Pour vérifier quel est ton écran principal sous Windows :
> Paramètres → Système → Affichage → sélectionne l'écran → coche "En faire l'écran principal"

---

## 📦 Installation

### Prérequis

- Python **3.10+** — [télécharger ici](https://www.python.org/downloads/)
- Clash of Clans sur PC (BlueStacks, LDPlayer, ou version Windows)
- Résolution **1920 x 1080**, plein écran

### Installer les dépendances

```bash
pip install pyautogui colorama keyboard mss pillow
```

### Cloner le projet

```bash
git clone https://github.com/TON_USERNAME/coc-farm-bot.git
cd coc-farm-bot
```

---

## 🚀 Utilisation

```bash
python coc_bot.py
```

Le menu s'ouvre dans le terminal :

```
╔══════════════════════════════════════════════════════════╗
║          ⚔  CLASH OF CLANS  ⚔                           ║
║          A U T O   F A R M   B O T                       ║
╠══════════════════════════════════════════════════════════╣
║  MENU PRINCIPAL                                          ║
╚══════════════════════════════════════════════════════════╝

  [1]  AUTO FARM       Lancer le bot de farming
  [2]  CONFIGURATION   Gérer les configs de troupes
  [3]  QUITTER
```

### Créer une configuration

1. Choisis `[2] CONFIGURATION`
2. Choisis `[1] Nouvelle configuration`
3. Entre le nombre de clics pour chaque slot (0 = ignoré)
4. Donne un nom à la config et confirme

### Lancer le farm

1. Choisis `[1] AUTO FARM`
2. Sélectionne une config (ou mode défaut = 50 clics x 11 slots)
3. Tu as **5 secondes** pour basculer sur Clash of Clans
4. Le bot tourne en boucle — appuie sur `ESC` pour stopper

---

## 🔨 Compiler en .exe

Pour distribuer le bot sans que Python soit installé :

### 1. Corriger la ligne du fichier de config

Dans `coc_bot.py`, remplace :
```python
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coc_configs.json")
```
Par :
```python
CONFIG_FILE = os.path.join(
    os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)),
    "coc_configs.json"
)
```

### 2. Compiler

```bash
pip install pyinstaller
pyinstaller --onefile --console coc_bot.py
```

### 3. Résultat

Le fichier `dist\coc_bot.exe` est autonome.
Le `coc_configs.json` sera créé automatiquement à côté du `.exe` au premier lancement.

---

## 🐙 Push sur GitHub

### Première fois — créer le dépôt

**1. Crée un compte sur [github.com](https://github.com) si ce n'est pas déjà fait.**

**2. Crée un nouveau dépôt :**
- Clique sur **"New repository"** (bouton vert en haut à droite)
- Nom du dépôt : `coc-farm-bot`
- Visibilité : Public ou Private (ton choix)
- Ne coche rien d'autre
- Clique **"Create repository"**

**3. Installe Git si pas encore fait :**
→ [git-scm.com/download/win](https://git-scm.com/download/win)

**4. Ouvre un CMD dans ton dossier `coc\` :**

```bash
# Initialise Git dans le dossier
git init

# Crée un .gitignore pour exclure les fichiers inutiles
echo __pycache__/ >> .gitignore
echo *.pyc >> .gitignore
echo dist/ >> .gitignore
echo build/ >> .gitignore
echo *.spec >> .gitignore
echo coc_configs.json >> .gitignore

# Ajoute tous les fichiers
git add .

# Premier commit
git commit -m "Initial commit - COC Farm Bot"

# Lie ton dossier au depot GitHub
# Remplace TON_USERNAME par ton pseudo GitHub
git remote add origin https://github.com/TON_USERNAME/coc-farm-bot.git

# Envoie le code
git branch -M main
git push -u origin main
```

**5. Vérifie sur GitHub** — tu verras tous tes fichiers en ligne avec le README affiché automatiquement.

---

### Mettre à jour après une modification

Chaque fois que tu modifies le bot :

```bash
# Voir les fichiers modifiés
git status

# Ajouter les modifications
git add .

# Décrire ce que tu as changé
git commit -m "Ajout de la fonctionnalité X"

# Envoyer sur GitHub
git push
```

---

### Récupérer le projet sur un autre PC

```bash
git clone https://github.com/TON_USERNAME/coc-farm-bot.git
cd coc-farm-bot
pip install pyautogui colorama keyboard mss pillow
python coc_bot.py
```

---

## 📁 Structure des fichiers

```
coc-farm-bot/
├── coc_bot.py           <- Bot principal + menu CMD
├── coc_calibration.py   <- Outil pour trouver les coordonnees
├── coc_configs.json     <- Configs sauvegardees (cree automatiquement)
└── README.md            <- Ce fichier
```

---

## Avertissement

Ce bot est destiné à un usage personnel uniquement.
L'utilisation de bots peut violer les conditions d'utilisation de Clash of Clans.
Utilise-le à tes propres risques.
