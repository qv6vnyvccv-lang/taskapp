import tkinter as tk
from tkinter import ttk
import random

# --- CONFIGURAZIONE COLORI ---
COLOR_BG = "#ffffff"
COLOR_TASK_BG = "#e8f0fe"   # Light Blue
COLOR_TASK_FG = "#1967d2"   # Dark Blue
COLOR_ACCENT = "#1a73e8"    # Google Blue
COLOR_AI = "#9334e6"        # AI Purple (Google Gemini style)
COLOR_AI_LIGHT = "#f3e8fd"  # AI Light Background
COLOR_DELETE = "#5f6368"

# --- MOTORE AI SIMULATO (No external libs) ---
class SimpleAI:
    def analyze(self, text):
        text = text.lower()
        category = "Generale"
        color = "#9aa0a6" # Grigio default
        
        # Logica di categorizzazione
        if any(x in text for x in ["chiama", "email", "meeting", "riunione", "progetto", "inviare"]):
            category = "Lavoro"
            color = "#e37400" # Arancione
        elif any(x in text for x in ["compra", "spesa", "latte", "pane", "ordine", "amazon"]):
            category = "Shopping"
            color = "#1e8e3e" # Verde
        elif any(x in text for x in ["paga", "banca", "bolletta", "soldi"]):
            category = "Finanze"
            color = "#d93025" # Rosso
        elif any(x in text for x in ["studia", "leggi", "libro", "esame"]):
            category = "Studio"
            color = "#1a73e8" # Blu
            
        return category, color

    def suggest_subtasks(self, text):
        text = text.lower()
        suggestions = []
        
        if "festa" in text or "party" in text:
            suggestions = ["Compra bevande", "Invita amici", "Scegli musica", "Ordina pizza"]
        elif "viaggio" in text or "vacanza" in text:
            suggestions = ["Prenota volo", "Prenota hotel", "Fai valigia", "Controlla documenti"]
        elif "progetto" in text:
            suggestions = ["Definisci obiettivi", "Assegna task", "Meeting iniziale", "Scrivi bozza"]
        elif "spesa" in text:
            suggestions = ["Controlla frigo", "Prendi contanti", "Porta buste"]
            
        return suggestions

# --- UI COMPONENTS ---

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, bg=COLOR_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="TFrame")
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

class TaskCard(tk.Canvas):
    def __init__(self, parent, text, category, cat_color, delete_command):
        super().__init__(parent, bg=COLOR_BG, height=70, highlightthickness=0)
        self.parent = parent
        self.delete_command = delete_command
        self.pack(fill="x", pady=5, padx=10)
        
        self.bind("<Configure>", lambda e: self.draw_card(text, category, cat_color))
        self.draw_card(text, category, cat_color)
        
    def draw_card(self, text, category, cat_color):
        self.delete("all")
        w = self.winfo_width()
        if w < 50: w = 350
        h = 70
        r = 20 

        # Sfondo Card
        points = [r,0, w-r,0, w,0, w,r, w,h-r, w,h, w-r,h, r,h, 0,h, 0,h-r, 0,r, 0,0]
        self.create_polygon(points, smooth=True, fill=COLOR_TASK_BG, outline="")
        
        # Testo Task
        self.create_text(20, 25, text=text, fill=COLOR_TASK_FG, font=("Google Sans", 12, "bold"), anchor="w")
        
        # Chip Categoria (Pillola colorata)
        chip_w = len(category) * 8 + 20
        chip_x = 20
        chip_y = 45
        self.create_oval(chip_x, chip_y, chip_x+chip_w, chip_y+18, fill=cat_color, outline="")
        self.create_text(chip_x + chip_w/2, chip_y+9, text=category.upper(), fill="white", font=("Arial", 8, "bold"))
        
        # Pulsante X
        btn_x = w - 30
        btn_y = 35
        self.create_text(btn_x, btn_y, text="✕", fill=COLOR_DELETE, font=("Arial", 12, "bold"))
        self.tag_bind("all", "<Button-1>", self.check_click)
        
    def check_click(self, event):
        w = self.winfo_width()
        if event.x > w - 50:
            self.delete_command()

class ModernApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.ai_engine = SimpleAI()

        self.title("AI Task Manager")
        self.geometry("450x750")
        self.configure(bg=COLOR_BG)
        
        # Stili
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=COLOR_BG)
        style.configure("TEntry", fieldbackground="#f1f3f4", borderwidth=0)
        
        # Stile Bottone Normale
        style.configure("TButton", background=COLOR_ACCENT, foreground="white", borderwidth=0, font=("Arial", 10, "bold"))
        style.map("TButton", background=[('active', "#1557b0")])
        
        # Stile Bottone AI
        style.configure("AI.TButton", background=COLOR_AI, foreground="white", borderwidth=0, font=("Arial", 10, "bold"))
        style.map("AI.TButton", background=[('active', "#7c23c9")])

        # Header
        header = ttk.Frame(self)
        header.pack(fill="x", padx=24, pady=(30, 10))
        tk.Label(header, text="AI Tasks", bg=COLOR_BG, fg="#202124", font=("Google Sans", 24, "bold")).pack(anchor="w")
        tk.Label(header, text="Powered by Python Logic", bg=COLOR_BG, fg="#5f6368", font=("Arial", 10)).pack(anchor="w")

        # Input Area
        input_frame = ttk.Frame(self)
        input_frame.pack(fill="x", padx=24, pady=20)
        
        self.task_entry = ttk.Entry(input_frame, font=("Arial", 12))
        self.task_entry.pack(side="left", fill="x", expand=True, ipady=8)
        self.task_entry.bind("<Return>", self.add_task)
        
        # Bottone AI
        ai_btn = ttk.Button(input_frame, text="✨ AI", width=5, style="AI.TButton", command=self.ai_analyze)
        ai_btn.pack(side="right", padx=(5, 0))
        
        # Bottone Add
        add_btn = ttk.Button(input_frame, text="+", width=3, command=self.add_task)
        add_btn.pack(side="right", padx=(5, 0))

        # Area Suggerimenti (Nascosta di default)
        self.suggestion_frame = tk.Frame(self, bg=COLOR_AI_LIGHT, height=0)
        self.suggestion_frame.pack(fill="x", padx=24, pady=(0, 10))
        self.suggestion_label = tk.Label(self.suggestion_frame, text="", bg=COLOR_AI_LIGHT, fg=COLOR_AI, font=("Arial", 10, "italic"))
        self.suggestion_label.pack(pady=5)

        # Lista
        self.list_container = ScrollableFrame(self)
        self.list_container.pack(fill="both", expand=True, padx=14)

    def add_task(self, event=None, text_override=None):
        text = text_override if text_override else self.task_entry.get().strip()
        
        if text:
            # 1. AI Analysis
            cat, color = self.ai_engine.analyze(text)
            
            # 2. Create Widget
            card = TaskCard(
                self.list_container.scrollable_frame, 
                text, 
                cat,
                color,
                delete_command=lambda: self.remove_task(card)
            )
            card.update_idletasks()
            card.draw_card(text, cat, color)
            
            if not text_override:
                self.task_entry.delete(0, tk.END)
                self.hide_suggestions()

    def ai_analyze(self):
        text = self.task_entry.get().strip()
        if not text: return
        
        # Chiedi all'AI suggerimenti
        subtasks = self.ai_engine.suggest_subtasks(text)
        
        if subtasks:
            self.show_suggestions(subtasks)
        else:
            # Se non ci sono suggerimenti complessi, aggiungi semplicemente con categorizzazione
            self.add_task()

    def show_suggestions(self, subtasks):
        # Pulisci frame suggerimenti
        for widget in self.suggestion_frame.winfo_children():
            widget.destroy()
            
        tk.Label(self.suggestion_frame, text="✨ L'AI suggerisce di aggiungere:", bg=COLOR_AI_LIGHT, fg=COLOR_AI, font=("Arial", 9, "bold")).pack(anchor="w", padx=10, pady=5)
        
        for task in subtasks:
            btn = tk.Button(
                self.suggestion_frame, 
                text=f"+ {task}", 
                bg="white", 
                fg=COLOR_AI, 
                relief="flat",
                font=("Arial", 9),
                command=lambda t=task: self.add_from_suggestion(t)
            )
            btn.pack(fill="x", padx=10, pady=2)
            
        self.suggestion_frame.configure(height=200) # Mostra

    def hide_suggestions(self):
        for widget in self.suggestion_frame.winfo_children():
            widget.destroy()
        self.suggestion_frame.configure(height=0)

    def add_from_suggestion(self, text):
        self.add_task(text_override=text)

    def remove_task(self, card_widget):
        card_widget.destroy()
        self.list_container.canvas.configure(scrollregion=self.list_container.canvas.bbox("all"))

if __name__ == "__main__":
    app = ModernApp()
    app.mainloop()
