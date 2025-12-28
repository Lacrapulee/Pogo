import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from game.board import Board
from ia.ai_player import AIPlayer
import math
import sys

CELL_SIZE = 140
PADDING = 18
PIECE_RADIUS = 18
STACK_GAP = 6
ANIM_STEPS_BASE = 14 
MIN_PIECE_RADIUS = 6
MIN_GAP = 2
MIN_SCALE_THRESHOLD = 0.6


class StartupScreen:
    def __init__(self, master):
        self.master = master
        self.frame = ttk.Frame(master, padding=16)
        # ecran de demarrage correspond à l'interface du jeu
        try:
            master.rowconfigure(0, weight=1)
            master.columnconfigure(0, weight=1)
        except Exception:
            pass
        self.frame.grid(row=0, column=0, sticky='nsew')

        # les modes de jeu
        ttk.Label(self.frame, text="POGO", font=(None, 20, 'bold')).pack(pady=(8,6))
        ttk.Label(self.frame, text="Choisissez un mode de jeu", font=(None, 11)).pack(pady=(0,12))

        btns = ttk.Frame(self.frame)
        btns.pack(pady=6)

        try:
            style = ttk.Style()
            style.configure('Mode.TButton', font=(None, 12, 'bold'), padding=8)
        except Exception:
            pass
        ttk.Button(btns, text="Solo (Humain vs Humain)", command=lambda: self.start('solo'), width=36, style='Mode.TButton').pack(pady=8)
        ttk.Button(btns, text="IA (Humain vs Ordinateur)", command=lambda: self.start('ia'), width=36, style='Mode.TButton').pack(pady=8)
        ttk.Button(btns, text="Quitter", command=self.quit, width=20, style='Mode.TButton').pack(pady=(10,4))

        ttk.Label(self.frame, text="Vous pouvez changer le mode plus tard via la barre d'outils.", font=(None, 9), foreground='#555').pack(pady=(6,2))

    def start(self, mode):
        self.frame.destroy()
        self.master.update_idletasks()
        w = self.master.winfo_width()
        h = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() - w) // 2
        y = (self.master.winfo_screenheight() - h) // 2
        self.master.geometry(f"+{x}+{y}")
        PogoGUI(self.master, mode=mode)

    def quit(self):
        # quitter proprement le jeu
        try:
            self.master.destroy()
        finally:
            sys.exit(0)


def launch_gui():
    root = tk.Tk()
    root.title("POGO - Interface Graphique")
    # centrer et définir une taille minimale de fenêtre
    window_w = CELL_SIZE * 3 + PADDING * 2 + 40
    window_h = window_w + 120
    root.minsize(window_w, window_h)
    try:
        style = ttk.Style()
        style.theme_use('clam')
    except Exception:
        pass

    # démarrer en plein écran par défaut
    try:
        root.attributes('-fullscreen', True)
        root.bind('<Escape>', lambda e: root.attributes('-fullscreen', False))
    except Exception:
        try:
            root.state('zoomed')
        except Exception:
            screen_w = root.winfo_screenwidth()
            screen_h = root.winfo_screenheight()
            w = min(screen_w - 80, max(window_w, int(screen_w * 0.7)))
            h = min(screen_h - 80, max(window_h, int(screen_h * 0.75)))
            root.geometry(f"{w}x{h}")

    # afficher l'écran de démarrage dans la fenêtre principale
    StartupScreen(root)

    # centrer la fenêtre à l'écran et lancer la boucle principale (si pas en plein écran)
    root.update_idletasks()
    if not getattr(root, 'attributes', lambda *a, **k: False)('-fullscreen'):
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        x = (screen_w - root.winfo_width()) // 2
        y = (screen_h - root.winfo_height()) // 2
        root.geometry(f"{root.winfo_width()}x{root.winfo_height()}+{x}+{y}")
    root.mainloop()


class PogoGUI:
    def __init__(self, master, mode='solo'):
        self.master = master
        self.board = Board()
        self.current_player = 'W'
        self.history = []

        # modes de jeu : solo ou ia
        self.mode = mode
        self.ai = None
        if self.mode == 'ia':
            self.ai = AIPlayer('B')

        # état
        self.selected = None  # (start_idx, n_pieces)
        self.highlighted = []
        self.hover = None
        self.animating = False

        # permet de détruire l'ui du jeu
        self._closing = False
        self.root_frame = ttk.Frame(self.master)
        self.root_frame.grid(row=0, column=0, sticky='nsew')
        try:
            self.master.rowconfigure(0, weight=1)
            self.master.columnconfigure(0, weight=1)
        except Exception:
            pass

        self.CELL_SIZE = CELL_SIZE
        self.PADDING = PADDING
        self.PIECE_RADIUS = PIECE_RADIUS
        self.STACK_GAP = STACK_GAP
        self._board_origin_x = 0
        self._board_origin_y = 0

        self.root_frame.rowconfigure(0, weight=1)
        for i in range(4):
            try:
                self.root_frame.columnconfigure(i, weight=1)
            except Exception:
                pass
        self.root_frame.bind('<Configure>', lambda e: self._on_resize())

        self.canvas_container = ttk.Frame(self.root_frame)
        self.canvas_container.grid(row=0, column=0, columnspan=4, sticky='nsew')
        try:
            self.canvas_container.columnconfigure(0, weight=0)
            self.canvas_container.columnconfigure(1, weight=1)
            self.canvas_container.columnconfigure(2, weight=0)
            self.canvas_container.rowconfigure(0, weight=1)
        except Exception:
            pass

        canvas_size = self.CELL_SIZE * 3 + self.PADDING * 2
        self.canvas = tk.Canvas(self.canvas_container, width=canvas_size, height=canvas_size, bg="#f6f7fb", highlightthickness=0)
        self.canvas.grid(row=0, column=1, sticky='nsew', padx=6, pady=(6, 4))
        try:
            self.canvas_container.columnconfigure(1, weight=1)
            self.canvas_container.rowconfigure(0, weight=1)
        except Exception:
            pass
        self.root_frame.update_idletasks()
        try:
            self.canvas.config(width=min(self.root_frame.winfo_width()-40, canvas_size), height=max(240, self.root_frame.winfo_height()-200))
        except Exception:
            pass
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Leave>", lambda e: self._set_hover(None))
        self.toolbar = ttk.Frame(self.root_frame)
        self.toolbar.grid(row=1, column=0, columnspan=4, sticky='we', padx=8, pady=(0,8))
        self.toolbar_inner = ttk.Frame(self.toolbar)
        self.toolbar_inner.pack(anchor='center')

        self.new_button = ttk.Button(self.toolbar_inner, text="Nouvelle partie", command=self._confirm_new)
        self.new_button.grid(row=0, column=0, padx=6)
        self.undo_button = ttk.Button(self.toolbar_inner, text="Annuler (u)", command=self.undo)
        self.undo_button.grid(row=0, column=1, padx=6)
        self.undo_button.state(['disabled'])
        self.help_button = ttk.Button(self.toolbar_inner, text="Aide", command=self.show_help)
        self.help_button.grid(row=0, column=2, padx=6)
        # affichage du mode
        self.mode_label = ttk.Label(self.toolbar_inner, text=("Mode: IA (IA joue Noir)" if self.mode == 'ia' else "Mode: Solo"), font=(None, 11, 'bold'))
        self.mode_label.grid(row=0, column=3, padx=12, pady=2)
        try:
            self.turn_canvas = tk.Canvas(self.toolbar_inner, width=18, height=18, highlightthickness=0, bg='')
            self.turn_dot = self.turn_canvas.create_oval(2,2,16,16, fill='#ffffff', outline='#9aa0a6')
            self.turn_canvas.grid(row=0, column=4, padx=(6,8), pady=2)
        except Exception:
            self.turn_canvas = None
            self.turn_dot = None
        self.speed_label = ttk.Label(self.toolbar_inner, text="Vitesse")
        self.speed_label.grid(row=0, column=5, padx=(12,2))
        self.speed_scale = ttk.Scale(self.toolbar_inner, from_=0.4, to=2.0, value=1.0, orient='horizontal')
        self.speed_scale.grid(row=0, column=6, padx=6)
        self.quit_button = ttk.Button(self.toolbar_inner, text="Retour menu", command=self._to_startup)
        self.quit_button.grid(row=0, column=7, padx=(6,0))

        # variable de statut (conservée pour l'indicateur de tour)
        self.status_var = tk.StringVar(value=f"Joueur : {'Blanc (W)' if self.current_player == 'W' else 'Noir (B)'}")

        self.instruction_var = tk.StringVar(value="Astuce : Cliquez sur une pile pour commencer. Sélectionnez le nombre de pièces puis cliquez sur une case verte pour déplacer.")
        self.instr_widget = ttk.Label(self.root_frame, textvariable=self.instruction_var, anchor='center', justify='center', foreground='#333')
        self.instr_widget.grid(row=4, column=0, columnspan=4, sticky='we', padx=8, pady=(0,12))
        
        self.palette = {
            'bg': '#f6f7fb',
            'cell': '#ffffff',
            'cell_border': '#c6c9d6',
            'cell_shadow': '#dfe3ee',
            'highlight': '#60c66b',
            'selected': '#4d89ff'
        }

        master.bind('<u>', lambda e: self.undo())
        master.bind('<Control-n>', lambda e: self._confirm_new())

        self.draw_board()
        try:
            self._update_turn_dot()
        except Exception:
            pass

    def cell_bbox(self, idx):
        r, c = divmod(idx, 3)
        x0 = self._board_origin_x + self.PADDING + c * self.CELL_SIZE
        y0 = self._board_origin_y + self.PADDING + r * self.CELL_SIZE
        return x0, y0, x0 + self.CELL_SIZE, y0 + self.CELL_SIZE

    def cell_center(self, idx):
        x0, y0, x1, y1 = self.cell_bbox(idx)
        return (x0 + x1) / 2, (y0 + y1) / 2

    def idx_from_coords(self, x, y):
        bx = x - self._board_origin_x - self.PADDING
        by = y - self._board_origin_y - self.PADDING
        if bx < 0 or by < 0:
            return None
        c = int(bx // self.CELL_SIZE)
        r = int(by // self.CELL_SIZE)
        if not (0 <= c < 3 and 0 <= r < 3):
            return None
        x0 = self._board_origin_x + self.PADDING + c * self.CELL_SIZE
        y0 = self._board_origin_y + self.PADDING + r * self.CELL_SIZE
        if x0 <= x <= x0 + self.CELL_SIZE and y0 <= y <= y0 + self.CELL_SIZE:
            return int(r * 3 + c)
        return None

    def _update_turn_dot(self):
        try:
            if not getattr(self, 'turn_canvas', None) or self.turn_dot is None:
                return
            if self.current_player == 'W':
                fill = '#ffffff'
                outline = '#9aa0a6'
            else:
                fill = '#111111'
                outline = '#d6d6d6'
            self.turn_canvas.itemconfig(self.turn_dot, fill=fill, outline=outline)
        except Exception:
            pass

    def piece_top_y(self, idx, pile_index):
        x0, y0, x1, y1 = self.cell_bbox(idx)
        base_y = y1 - (self.PIECE_RADIUS + 6)
        n = len(self.board.get_pile(idx))
        return base_y - (n - 1 - pile_index) * (2 * self.PIECE_RADIUS + self.STACK_GAP)

    def _set_hover(self, idx):
        if self.hover == idx:
            return
        self.hover = idx
        try:
            # changer le curseur pour indiquer que c'est cliquable
            self.canvas.configure(cursor='hand2' if idx is not None else '')
        except Exception:
            pass
        self.draw_board()

    def _ease_out(self, t):
        return 1 - (1 - t) * (1 - t)

    def _update_undo_state(self):
        if self.history:
            self.undo_button.state(['!disabled'])
        else:
            self.undo_button.state(['disabled'])

    def _on_resize(self):
        try:
            try:
                self.root_frame.update_idletasks()
            except Exception:
                pass

            frame_w = max(200, self.root_frame.winfo_width())
            frame_h = max(200, self.root_frame.winfo_height())

            th = 0
            sh = 0
            ih = 0
            if getattr(self, 'toolbar', None):
                try:
                    th = max(self.toolbar.winfo_reqheight(), self.toolbar.winfo_height())
                except Exception:
                    th = self.toolbar.winfo_height() if self.toolbar.winfo_height() else 0
            if getattr(self, 'status_bar_widget', None):
                try:
                    sh = max(self.status_bar_widget.winfo_reqheight(), self.status_bar_widget.winfo_height())
                except Exception:
                    sh = self.status_bar_widget.winfo_height() if self.status_bar_widget.winfo_height() else 0
            if getattr(self, 'instr_widget', None):
                try:
                    ih = max(self.instr_widget.winfo_reqheight(), self.instr_widget.winfo_height())
                except Exception:
                    ih = self.instr_widget.winfo_height() if self.instr_widget.winfo_height() else 0

            # calculer l'espace disponible pour le canvas
            extra_margin = max(8, int(self.CELL_SIZE * 0.04))
            avail_h = frame_h - th - sh - ih - extra_margin
            avail_w = frame_w - 2 * self.PADDING - extra_margin

            if avail_h < 120:
                avail_h = 120
            if avail_w < 120:
                avail_w = 120

            # définir la taille du canvas pour remplir l'espace
            try:
                self.canvas.config(width=avail_w, height=avail_h)
            except Exception:
                pass

            cell_w = int((avail_w) / 3)
            cell_h = int((avail_h) / 3)
            max_by_frame = int((frame_h * 0.8) / 3)
            new_size = max(60, min(min(400, max_by_frame), min(cell_w, cell_h)))

            if abs(new_size - self.CELL_SIZE) > 2:
                self.CELL_SIZE = new_size
                self.PIECE_RADIUS = max(MIN_PIECE_RADIUS, int(self.CELL_SIZE * 0.12))
                self.STACK_GAP = max(2, int(self.CELL_SIZE * 0.04))
                canvas_w = min(avail_w, int(frame_w * 0.8))
                canvas_h = min(avail_h, int(frame_h * 0.8))
                try:
                    self.canvas.config(width=canvas_w, height=canvas_h)
                except Exception:
                    pass
                self.draw_board()
        except Exception:
            pass

    def _confirm_new(self):
        if self.animating:
            return
        if messagebox.askyesno("Nouvelle partie", "Commencer une nouvelle partie ?"):
            self.new_game()

    def new_game(self):
        if self.animating:
            return
        self.board.setup_board()
        self.current_player = 'W'
        self.history.clear()
        self.selected = None
        self.highlighted = []
        # mettre à jour l'indicateur de tour visible
        self.status_var.set(f"Joueur : {'Blanc (W)' if self.current_player == 'W' else 'Noir (B)'}")
        self._update_turn_dot()
        self._update_undo_state()
        self.draw_board()

    def _to_startup(self):
        if self.animating:
            messagebox.showinfo("Patientez", "Une animation est en cours — attendez la fin pour retourner au menu.")
            return
        if not messagebox.askyesno("Retour au menu", "Retourner au menu principal ? La partie en cours sera perdue."):
            return
        self._closing = True
        try:
            self.root_frame.destroy()
        except Exception:
            pass
        StartupScreen(self.master)

    def undo(self):
        if self.animating:
            return
        if not self.history:
            return
        self.board = self.history.pop()
        self.selected = None
        self.highlighted = []
        self.current_player = 'B' if self.current_player == 'W' else 'W'
        self.status_var.set(f"Joueur : {'Blanc (W)' if self.current_player == 'W' else 'Noir (B)'}")
        self._update_turn_dot()
        self._update_undo_state()
        self.instruction_var.set("Annulation effectuée.")
        self.draw_board()

    def ask_piece_count(self, idx, max_move):
        win = tk.Toplevel(self.master)
        win.title("Choisir nombre")
        win.resizable(False, False)
        cx, cy = self.cell_center(idx)
        x = int(self.master.winfo_rootx() + cx - 60)
        y = int(self.master.winfo_rooty() + cy - 30)
        win.geometry(f"+{x}+{y}")
        choice = {'n': None}

        frm = ttk.Frame(win, padding=8)
        frm.pack()
        ttk.Label(frm, text=f"Combien déplacer (1-{max_move})").pack()
        btns = ttk.Frame(frm)
        btns.pack(pady=6)
        for i in range(1, max_move + 1):
            b = ttk.Button(btns, text=str(i), command=lambda v=i: (choice.__setitem__('n', v), win.destroy()))
            b.pack(side='left', padx=4)
        ttk.Button(frm, text="Annuler", command=win.destroy).pack(pady=(6,0))
        win.grab_set()
        self.master.wait_window(win)
        return choice['n']

    def show_help(self):
        # aide pour comprendre les règles du jeu
        msg = ("But : Contrôler le sommet des piles (avoir au moins une de vos couleurs visible au sommet des cases).\n\n"
               "A votre tour :\n"
               "- Cliquez sur une pile dont la couleur au sommet est la vôtre.\n"
               "- Choisissez le nombre de pièces à déplacer (1 à 3, selon la hauteur).\n"
               "- Cliquez sur une case mise en surbrillance (verte) : la distance doit être exactement le nombre de pièces déplacées (déplacements orthogonaux uniquement).\n\n"
               "Règles supplémentaires :\n"
               "- Pas de demi-tour immédiat dans un même mouvement (pas de 180°).\n"
               "- Le joueur qui couvre toutes les piles adverses gagne.\n\n"
               "Astuce : les points verts au centre des cases indiquent les destinations possibles ; un message-guide s'affiche en bas.")
        messagebox.showinfo("Aide - Règles du jeu", msg)

    # tout ce qui est dessin du plateau et des pièces
    def draw_board(self):
        self.canvas.delete("all")
        offset = max(4, int(self.CELL_SIZE * 0.04))
        board_w = self.CELL_SIZE * 3 + 2 * self.PADDING
        board_h = self.CELL_SIZE * 3 + 2 * self.PADDING
        try:
            actual_w = self.canvas.winfo_width()
            actual_h = self.canvas.winfo_height()
        except Exception:
            actual_w, actual_h = board_w, board_h
        self._board_origin_x = max(0, int((actual_w - board_w) / 2))
        self._board_origin_y = max(0, int((actual_h - board_h) / 2))
        sx = self._board_origin_x + self.PADDING
        sy = self._board_origin_y + self.PADDING
        cell_radius = max(10, int(self.CELL_SIZE * 0.06))
        try:
            self._create_rounded_rect(sx - offset, sy - offset, sx + 3 * self.CELL_SIZE + offset, sy + 3 * self.CELL_SIZE + offset, radius=cell_radius, fill=self.palette['cell_shadow'], outline='')
        except Exception:
            self.canvas.create_rectangle(sx - offset, sy - offset, sx + 3 * self.CELL_SIZE + offset, sy + 3 * self.CELL_SIZE + offset, fill=self.palette['cell_shadow'], outline='')

        for r in range(3):
            for c in range(3):
                idx = r * 3 + c
                x0, y0, x1, y1 = self.cell_bbox(idx)
                self._create_rounded_rect(x0, y0, x1, y1, radius=max(8, int(self.CELL_SIZE * 0.06)), fill=self.palette['cell'], outline=self.palette['cell_border'], width=max(1, int(self.CELL_SIZE*0.015)), tags=(f'cell{idx}',))
                self.canvas.create_text(x0 + 8, y0 + 8, anchor='nw', text=str(idx), fill='#b0b6c8', font=(None, max(8, int(self.CELL_SIZE * 0.04))))

                if self.hover == idx and not self.selected:
                    pad = max(3, int(self.CELL_SIZE * 0.02))
                    try:
                        self._create_rounded_rect(x0+pad, y0+pad, x1-pad, y1-pad, radius=max(6, int(self.CELL_SIZE*0.04)), fill='#f1fbf6', outline='#b0b6c8', width=max(1, int(self.CELL_SIZE*0.01)))
                    except Exception:
                        self.canvas.create_rectangle(x0+pad, y0+pad, x1-pad, y1-pad, outline='#b0b6c8', width=2)

                if self.selected and self.selected[0] == idx:
                    pad2 = max(4, int(self.CELL_SIZE * 0.03))
                    self.canvas.create_rectangle(x0+pad2, y0+pad2, x1-pad2, y1-pad2, outline=self.palette['selected'], width=4)

                pile = self.board.get_pile(idx)
                cx = (x0 + x1) / 2
                total_n = len(pile)
                radius, gap, visible = self._stack_metrics(idx, total_n)
                if visible >= total_n:
                    for i, piece in enumerate(pile):
                        y = self._final_y_for_index(idx, i, total_n, radius, gap)
                        if piece == 'W':
                            fill = '#ffffff'
                            outline = '#9aa0a6'
                        else:
                            fill = '#111111'
                            outline = '#d6d6d6'
                        self.canvas.create_oval(cx - radius, y - radius, cx + radius, y + radius, fill=fill, outline=outline, width=max(1, int(radius*0.12)))
                else:
                    start = total_n - visible
                    for pile_i in range(start, total_n):
                        piece = pile[pile_i]
                        y = self._final_y_for_index(idx, pile_i, total_n, radius, gap)
                        if piece == 'W':
                            fill = '#ffffff'
                            outline = '#9aa0a6'
                        else:
                            fill = '#111111'
                            outline = '#d6d6d6'
                        self.canvas.create_oval(cx - radius, y - radius, cx + radius, y + radius, fill=fill, outline=outline, width=max(1, int(radius*0.12)))
                    hidden = total_n - visible
                    badge_x = x0 + max(12, int(self.CELL_SIZE*0.08))
                    badge_y = y1 - max(18, int(self.CELL_SIZE*0.12))
                    self.canvas.create_rectangle(badge_x-8, badge_y-12, badge_x+30, badge_y+12, fill='#333', outline='')
                    self.canvas.create_text(badge_x+11, badge_y, text=f"+{hidden}", fill='white', font=(None, max(10, int(self.CELL_SIZE*0.06)), 'bold'))

                if idx in self.highlighted:
                    pad3 = max(6, int(self.CELL_SIZE*0.04))
                    self.canvas.create_rectangle(x0+pad3, y0+pad3, x1-pad3, y1-pad3, outline=self.palette['highlight'], width=max(2, int(self.CELL_SIZE*0.02)))
                    mx, my = cx, (y0 + y1) / 2
                    try:
                        self.canvas.create_oval(mx-int(self.CELL_SIZE*0.07), my-int(self.CELL_SIZE*0.07), mx+int(self.CELL_SIZE*0.07), my+int(self.CELL_SIZE*0.07), fill=self.palette['highlight'], outline='', stipple='gray25')
                    except Exception:
                        self.canvas.create_oval(mx-int(self.CELL_SIZE*0.07), my-int(self.CELL_SIZE*0.07), mx+int(self.CELL_SIZE*0.07), my+int(self.CELL_SIZE*0.07), fill=self.palette['highlight'], outline='')
                    self.canvas.create_text(mx, my, text=str(idx), fill='white', font=(None, max(10, int(self.CELL_SIZE*0.06)), 'bold'))

        self.canvas.create_text(PADDING + 8, CELL_SIZE * 3 + PADDING - 6, anchor='sw', text=self.status_var.get(), fill='#222')

    def _create_rounded_rect(self, x1, y1, x2, y2, radius=8, **kwargs):
        points = [ (x1+radius, y1), (x2-radius, y1), (x2, y1+radius), (x2, y2-radius), (x2-radius, y2), (x1+radius, y2), (x1, y2-radius), (x1, y1+radius) ]
        self.canvas.create_rectangle(x1+radius, y1, x2-radius, y2, **kwargs)
        self.canvas.create_rectangle(x1, y1+radius, x2, y2-radius, **kwargs)
        self.canvas.create_arc(x2-2*radius, y1, x2, y1+2*radius, start=0, extent=90, style='pieslice', **kwargs)
        self.canvas.create_arc(x2-2*radius, y2-2*radius, x2, y2, start=270, extent=90, style='pieslice', **kwargs)
        self.canvas.create_arc(x1, y2-2*radius, x1+2*radius, y2, start=180, extent=90, style='pieslice', **kwargs)
        self.canvas.create_arc(x1, y1, x1+2*radius, y1+2*radius, start=90, extent=90, style='pieslice', **kwargs)

    def _stack_metrics(self, idx, total_n):
        x0, y0, x1, y1 = self.cell_bbox(idx)
        cell_h = y1 - y0
        available = cell_h - 28
        if total_n <= 0:
            return PIECE_RADIUS, STACK_GAP, 0
        needed = total_n * (2 * PIECE_RADIUS) + (total_n - 1) * STACK_GAP
        s = min(1.0, available / needed) if needed > 0 else 1.0
        if s >= MIN_SCALE_THRESHOLD:
            radius = max(MIN_PIECE_RADIUS, PIECE_RADIUS * s)
            gap = max(MIN_GAP, STACK_GAP * s)
            visible = total_n
            return radius, gap, visible
        visible = max(1, int((available + STACK_GAP) // (2 * PIECE_RADIUS + STACK_GAP)))
        radius = PIECE_RADIUS
        gap = STACK_GAP
        if visible > total_n:
            visible = total_n
        return radius, gap, visible

    def _final_y_for_index(self, idx, piece_index, total_n, radius, gap):
        x0, y0, x1, y1 = self.cell_bbox(idx)
        base_y = y1 - 12
        return base_y - (total_n - 1 - piece_index) * (2 * radius + gap)

    def on_mouse_move(self, event):
        idx = self.idx_from_coords(event.x, event.y)
        self._set_hover(idx)

    def on_canvas_click(self, event):
        if self.animating:
            return
        idx = self.idx_from_coords(event.x, event.y)
        if idx is None:
            try:
                mark = self.canvas.create_oval(event.x-6, event.y-6, event.x+6, event.y+6, outline='#d9534f', width=2)
                self.master.after(500, lambda m=mark: self.canvas.delete(m))
            except Exception:
                pass
            return

        if not self.selected:
            owner = self.board.get_top_owner(idx)
            if owner != self.current_player:
                messagebox.showinfo("Action invalide", "Sélectionnez une pile dont vous contrôlez le sommet.")
                return
            max_move = min(3, len(self.board.get_pile(idx)))
            if max_move == 0:
                messagebox.showinfo("Action invalide", "La pile sélectionnée est vide.")
                return
            n = self.ask_piece_count(idx, max_move)
            if n is None:
                return

            valid_moves = self.board.get_valid_moves(self.current_player)
            dests = [m[2] for m in valid_moves if m[0] == idx and m[1] == n]
            if not dests:
                messagebox.showinfo("Aucun coup", "Aucune destination valide pour ce nombre de pièces.")
                return

            self.selected = (idx, n)
            self.highlighted = dests
            self.instruction_var.set(f"Sélection: {idx} avec {n} pièce(s). Cliquez sur une case verte pour valider.")
            self.draw_board()
            return

        start_idx, n = self.selected
        if idx not in self.highlighted:
            owner = self.board.get_top_owner(idx)
            if owner == self.current_player:
                self.selected = None
                self.highlighted = []
                self.draw_board()
                self.on_canvas_click(event)
                return
            messagebox.showinfo("Destination invalide", "Cliquez sur une des destinations mises en surbrillance ou annulez.")
            self.instruction_var.set("Erreur : cliquez sur une des cases vertes ou annulez la sélection.")
            return

        try:
            self.history.append(self.board.clone())
            self._update_undo_state()
            self.animating = True
            self.instruction_var.set(f"Déplacement de {n} pièce(s) de {start_idx} vers {idx}...")
            self._animate_move(start_idx, n, idx)
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
            self.selected = None
            self.highlighted = []
            self.animating = False
            self.draw_board()
            return

    def _animate_move(self, start_idx, n, dest_idx):
        orig_pile = list(self.board.get_pile(start_idx))
        paquet = self.board.retire_paquet(start_idx, n)
        self.selected = None
        self.highlighted = []
        self.draw_board()

        start_cx, start_cy = self.cell_center(start_idx)
        dest_cx, dest_cy = self.cell_center(dest_idx)

        start_len = len(orig_pile)
        radius_for_anim, gap_for_anim, _ = self._stack_metrics(start_idx, start_len)
        cell_half = self.CELL_SIZE / 2

        moving_items = []
        for i in range(n):
            piece_idx = start_len - n + i
            y = self._final_y_for_index(start_idx, piece_idx, start_len, radius_for_anim, gap_for_anim)
            x = start_cx
            color = '#ffffff' if paquet[i] == 'W' else '#111111'
            outline = '#9aa0a6' if paquet[i] == 'W' else '#d6d6d6'
            item = self.canvas.create_oval(x - radius_for_anim, y - radius_for_anim, x + radius_for_anim, y + radius_for_anim, fill=color, outline=outline, width=max(1, int(radius_for_anim*0.12)))
            moving_items.append((item, color))

        dest_len = len(self.board.get_pile(dest_idx))
        target_positions = []
        total_after = dest_len + n
        dest_radius, dest_gap, dest_visible = self._stack_metrics(dest_idx, total_after)
        for i in range(n):
            piece_final_index = dest_len + (n - 1 - i)
            final_y = self._final_y_for_index(dest_idx, piece_final_index, total_after, dest_radius, dest_gap)
            final_x = dest_cx
            target_positions.append((final_x, final_y))
        if dest_radius != radius_for_anim:
            adjusted = []
            for fx, fy in target_positions:
                adjusted.append((fx, fy))
            target_positions = adjusted

        speed = float(self.speed_scale.get())
        steps = max(6, int(ANIM_STEPS_BASE / speed))

        def step(frame=0):
            if getattr(self, '_closing', False):
                for item, _ in moving_items:
                    try:
                        self.canvas.delete(item)
                    except Exception:
                        pass
                self.animating = False
                return

            t = frame / steps
            ease = self._ease_out(t)

            if frame >= steps:
                self.board.place_paquet(dest_idx, paquet)
                self.animating = False
                self.current_player = 'B' if self.current_player == 'W' else 'W'
                self.status_var.set(f"Joueur : {'Blanc (W)' if self.current_player == 'W' else 'Noir (B)'}")
                self._update_turn_dot()
                self.instruction_var.set("Astuce : Cliquez sur une pile pour commencer. Sélectionnez le nombre puis cliquez sur une case verte.")
                self.draw_board()
                winner = self.board.is_game_over()
                if winner:
                    self._flash_winner(winner)
                    return

                if self.mode == 'ia' and self.ai and self.current_player == self.ai.player_color and not getattr(self, '_closing', False):
                    self.master.after(350, self._do_ai_move)
                return

            for i, (item, piece_color) in enumerate(moving_items):
                tx, ty = target_positions[i]
                coords = self.canvas.coords(item)
                if not coords or len(coords) < 4:
                    continue
                sx = (coords[0] + coords[2]) / 2
                sy = (coords[1] + coords[3]) / 2
                nx = sx + (tx - sx) * ease
                ny = sy + (ty - sy) * ease
                x0, y0, x1, y1 = nx - radius_for_anim, ny - radius_for_anim, nx + radius_for_anim, ny + radius_for_anim
                self.canvas.coords(item, x0, y0, x1, y1)
            self.master.after(16, lambda f=frame+1: step(f))

        step()

    def _flash_winner(self, winner):
        original = self.canvas['bg']
        def flash(n=0):
            if n >= 6:
                self.canvas.config(bg=original)
                messagebox.showinfo("Fin de partie", f"BRAVO ! Le joueur {winner} a gagné la partie !")
                return
            self.canvas.config(bg='#ffe08a' if n % 2 == 0 else original)
            self.master.after(180, lambda: flash(n+1))
        flash()

    def _do_ai_move(self):
        if not self.ai or self.animating or getattr(self, '_closing', False):
            return
        # l'ia choisit un coup
        move = self.ai.get_best_move(self.board)
        if not move:
            # l'ia passe
            if getattr(self, '_closing', False):
                return
            self.instruction_var.set("IA ne peut jouer. Tour passé.")
            self.current_player = 'B' if self.current_player == 'W' else 'W'
            self.status_var.set(f"Joueur : {'Blanc (W)' if self.current_player == 'W' else 'Noir (B)'}")
            self._update_turn_dot()
            return
        start, n, dest = move
        self.history.append(self.board.clone())
        self._update_undo_state()
        self.instruction_var.set(f"IA joue : {n} pièce(s) de {start} vers {dest}...")
        self.animating = True
        self._animate_move(start, n, dest)

