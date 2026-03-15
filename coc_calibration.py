"""
COC Calibration Tool — Affiche l'écran en direct avec coords souris en temps réel
"""

import tkinter as tk
from PIL import Image, ImageTk
import mss
import threading
import time

# ── Config ────────────────────────────────────────────────────────────────────
GRID_STEP = 100   # Espacement grille (en pixels réels de l'écran)
FPS       = 15    # Rafraîchissement

class CalibrationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 COC Calibration — Coords en temps réel")
        self.root.configure(bg="#0a0a0f")

        # ── Résolution écran principal ────────────────────────────────────────
        with mss.mss() as sct:
            m = sct.monitors[1]
            self.SCREEN_W = m["width"]
            self.SCREEN_H = m["height"]

        print(f"✅ Résolution écran : {self.SCREEN_W} x {self.SCREEN_H}")

        # Taille de la fenêtre = 75% de l'écran
        self.WIN_W = int(self.SCREEN_W * 0.75)
        self.WIN_H = int(self.SCREEN_H * 0.75)

        self.mouse_real_x = 0
        self.mouse_real_y = 0
        self.click_markers = []
        self.running = True
        self.current_frame = None

        self._build_ui()
        self._start_capture_thread()
        self.root.bind("<Escape>", lambda e: self._quit())
        self.root.bind("<c>",      self._clear_markers)
        self.root.bind("<C>",      self._clear_markers)
        self.root.protocol("WM_DELETE_WINDOW", self._quit)
        self._render_loop()

    # ── Construction UI ───────────────────────────────────────────────────────

    def _build_ui(self):
        # Barre du haut
        top = tk.Frame(self.root, bg="#060610", height=40)
        top.pack(fill="x", side="top")
        top.pack_propagate(False)

        tk.Label(top, text="◈  COC CALIBRATION",
                 bg="#060610", fg="#00ffaa",
                 font=("Courier New", 12, "bold")).pack(side="left", padx=16)

        tk.Label(top, text=f"Écran : {self.SCREEN_W} × {self.SCREEN_H}  |  Clique pour marquer  |  C = effacer  |  ESC = quitter",
                 bg="#060610", fg="#334455",
                 font=("Courier New", 9)).pack(side="left", padx=8)

        # Canvas
        self.canvas = tk.Canvas(self.root, width=self.WIN_W, height=self.WIN_H,
                                bg="#111118", highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Motion>",   self._on_mouse_move)
        self.canvas.bind("<Button-1>", self._on_click)

        # Barre du bas — coords
        bot = tk.Frame(self.root, bg="#04040e", height=56)
        bot.pack(fill="x", side="bottom")
        bot.pack_propagate(False)

        # Gros affichage X / Y
        self.var_x = tk.StringVar(value="X :  ---")
        self.var_y = tk.StringVar(value="Y :  ---")
        self.var_click = tk.StringVar(value="")
        self.var_log   = tk.StringVar(value="Clics : 0")

        tk.Label(bot, textvariable=self.var_x, bg="#04040e", fg="#00ffaa",
                 font=("Courier New", 24, "bold"), width=11, anchor="e").pack(side="left", padx=(20,0))
        tk.Label(bot, text="  /  ", bg="#04040e", fg="#1a2233",
                 font=("Courier New", 24, "bold")).pack(side="left")
        tk.Label(bot, textvariable=self.var_y, bg="#04040e", fg="#00ccff",
                 font=("Courier New", 24, "bold"), width=11, anchor="w").pack(side="left")
        tk.Label(bot, textvariable=self.var_click, bg="#04040e", fg="#ffcc00",
                 font=("Courier New", 13)).pack(side="left", padx=28)
        tk.Label(bot, textvariable=self.var_log, bg="#04040e", fg="#334455",
                 font=("Courier New", 11)).pack(side="right", padx=16)

        # Taille fenêtre
        self.root.geometry(f"{self.WIN_W}x{self.WIN_H + 40 + 56}")

    # ── Thread de capture écran ───────────────────────────────────────────────

    def _start_capture_thread(self):
        def capture():
            with mss.mss() as sct:
                mon = sct.monitors[1]
                while self.running:
                    shot  = sct.grab(mon)
                    img   = Image.frombytes("RGB", shot.size, shot.rgb)
                    self.current_frame = img
                    time.sleep(1 / FPS)
        threading.Thread(target=capture, daemon=True).start()

    # ── Boucle de rendu ───────────────────────────────────────────────────────

    def _render_loop(self):
        if not self.running:
            return

        cw = self.canvas.winfo_width()  or self.WIN_W
        ch = self.canvas.winfo_height() or self.WIN_H
        sx = cw / self.SCREEN_W
        sy = ch / self.SCREEN_H

        self.canvas.delete("all")

        # ── Screenshot ────────────────────────────────────────────────────────
        if self.current_frame:
            frame = self.current_frame.resize((cw, ch), Image.BILINEAR)
            self._tk_img = ImageTk.PhotoImage(frame)
            self.canvas.create_image(0, 0, anchor="nw", image=self._tk_img)

        # ── Grille ────────────────────────────────────────────────────────────
        for rx in range(0, self.SCREEN_W + 1, GRID_STEP):
            cx    = int(rx * sx)
            thick = 2 if rx % (GRID_STEP * 2) == 0 else 1
            col   = "#1f4433" if thick == 2 else "#142b22"
            self.canvas.create_line(cx, 0, cx, ch, fill=col, width=thick)
            if thick == 2 and 0 < rx < self.SCREEN_W:
                self.canvas.create_text(cx + 3, 12, text=str(rx),
                                         fill="#2e7755", font=("Courier New", 8), anchor="w")

        for ry in range(0, self.SCREEN_H + 1, GRID_STEP):
            cy    = int(ry * sy)
            thick = 2 if ry % (GRID_STEP * 2) == 0 else 1
            col   = "#1f4433" if thick == 2 else "#142b22"
            self.canvas.create_line(0, cy, cw, cy, fill=col, width=thick)
            if thick == 2 and 0 < ry < self.SCREEN_H:
                self.canvas.create_text(3, cy + 3, text=str(ry),
                                         fill="#2e7755", font=("Courier New", 8), anchor="nw")

        # ── Curseur ───────────────────────────────────────────────────────────
        mx = int(self.mouse_real_x * sx)
        my = int(self.mouse_real_y * sy)

        # Lignes de visée
        self.canvas.create_line(mx, 0, mx, ch, fill="#0d3322", width=1)
        self.canvas.create_line(0, my, cw, my, fill="#0d3322", width=1)

        # Croix centrale
        S = 14
        self.canvas.create_line(mx-S, my, mx+S, my, fill="#00ffaa", width=2)
        self.canvas.create_line(mx, my-S, mx, my+S, fill="#00ffaa", width=2)

        # Bulle coordonnées
        txt  = f" ({self.mouse_real_x}, {self.mouse_real_y}) "
        bx   = mx + 16
        by   = my - 22
        bx   = min(bx, cw - 130)
        by   = max(by, 4)
        self.canvas.create_rectangle(bx-2, by-2, bx+124, by+17,
                                      fill="#081510", outline="#00ffaa", width=1)
        self.canvas.create_text(bx + 60, by + 7, text=txt,
                                 fill="#00ffaa", font=("Courier New", 10, "bold"), anchor="center")

        # ── Marqueurs clics ───────────────────────────────────────────────────
        for i, (rx, ry) in enumerate(self.click_markers):
            mcx = int(rx * sx)
            mcy = int(ry * sy)
            R = 9
            self.canvas.create_oval(mcx-R, mcy-R, mcx+R, mcy+R,
                                     outline="#ff4466", width=2)
            self.canvas.create_line(mcx-R, mcy, mcx+R, mcy, fill="#ff4466", width=1)
            self.canvas.create_line(mcx, mcy-R, mcx, mcy+R, fill="#ff4466", width=1)
            self.canvas.create_text(mcx + 14, mcy - 13,
                                     text=f"#{i+1}  ({rx}, {ry})",
                                     fill="#ffdd44", font=("Courier New", 9, "bold"), anchor="w")

        self.root.after(int(1000 / FPS), self._render_loop)

    # ── Événements ────────────────────────────────────────────────────────────

    def _on_mouse_move(self, event):
        cw = self.canvas.winfo_width()  or self.WIN_W
        ch = self.canvas.winfo_height() or self.WIN_H
        self.mouse_real_x = max(0, min(self.SCREEN_W - 1, int(event.x / (cw / self.SCREEN_W))))
        self.mouse_real_y = max(0, min(self.SCREEN_H - 1, int(event.y / (ch / self.SCREEN_H))))
        self.var_x.set(f"X :  {self.mouse_real_x}")
        self.var_y.set(f"Y :  {self.mouse_real_y}")

    def _on_click(self, event):
        rx, ry = self.mouse_real_x, self.mouse_real_y
        self.click_markers.append((rx, ry))
        self.var_click.set(f"📌  ({rx}, {ry})")
        self.var_log.set(f"Clics : {len(self.click_markers)}")
        print(f"🖱️  Clic #{len(self.click_markers)} → x={rx}, y={ry}")

    def _clear_markers(self, event=None):
        self.click_markers.clear()
        self.var_click.set("")
        self.var_log.set("Clics : 0")
        print("🗑️  Marqueurs effacés")

    def _quit(self):
        self.running = False
        if self.click_markers:
            print("\n📋 Récap des clics :")
            for i, (x, y) in enumerate(self.click_markers):
                print(f"  [{i+1}]  x={x},  y={y}")
        self.root.destroy()


# ── Lancement ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app  = CalibrationApp(root)
    root.mainloop()