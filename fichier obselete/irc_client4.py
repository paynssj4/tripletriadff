from PIL import Image, ImageTk
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext, ttk
import irc.client
import logging
import threading
import json
import os
import random
import socket
from ai import AIPlayer
from card import Card  # Ajouter cette ligne en haut de votre fichier
from triple_triad_game import TripleTriadGame  # Importer la classe TripleTriadGame

logging.basicConfig(level=logging.INFO)

USERS_FILE = 'users.json'
CARDS_FILE = 'cards.json'

def create_initial_deck(cards_file: str, deck_size: int = 40):
    with open(cards_file, 'r') as f:
        all_cards_data = json.load(f)

    all_cards = [Card(card_data["name"], card_data["attribute"], card_data["numbers"], card_data["image"]) for card_data in all_cards_data]

    if len(all_cards) < deck_size:
        while len(all_cards) < deck_size:
            all_cards.append(random.choice(all_cards))

    deck = random.sample(all_cards, deck_size)
    return deck

class ScrolledFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.canvas = tk.Canvas(self, width=400, height=300)  # Définir des dimensions spécifiques pour le Canvas
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Utiliser Grid pour la disposition
        self.canvas.grid(row=0, column=0, sticky="ns")  # Ne pas utiliser "ew" pour éviter de remplir horizontalement
        self.scrollbar.grid(row=0, column=1, sticky="ns")

class IRCClient:
    def __init__(self, root):
        self.root = root
        self.root.title("IRC Client")

        self.username = self.authenticate_user()
        if not self.username:
            return

        self.nickname = simpledialog.askstring("Create IRC Nickname", "Enter your IRC nickname:")
        if not self.nickname:
            messagebox.showerror("Error", "Nickname is required.")
            self.root.destroy()
            return

        self.channel = '#Dialogues'

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text=self.channel)

        self.inventory_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.inventory_tab, text="Inventaire")

        self.initialize_user_interface()
        self.connect_to_server()

        # Initialiser le socket pour la communication entre les joueurs
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('localhost', 0))  # Bind to any available port
        self.socket.listen(1)
        self.port = self.socket.getsockname()[1]

        # Démarrer le thread pour écouter les connexions entrantes
        threading.Thread(target=self.listen_for_connections, daemon=True).start()

    def authenticate_user(self):
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'w') as f:
                json.dump({}, f)

        with open(USERS_FILE, 'r') as f:
            users = json.load(f)

        response = messagebox.askyesno("Authentication", "Do you have an account?")
        if response:
            username = simpledialog.askstring("Login", "Enter your username:")
            password = simpledialog.askstring("Login", "Enter your password:", show='*')

            if username in users and users[username]['password'] == password:
                messagebox.showinfo("Login", "Login successful!")
                self.deck = [Card(**card_data) for card_data in users[username]['deck']]
                self.gold = users[username].get('gold', 100)
                self.experience = users[username].get('experience', 0)
                self.level = users[username].get('level', 1)
                return username
            else:
                messagebox.showerror("Login", "Invalid username or password.")
                return self.authenticate_user()
        else:
            username = simpledialog.askstring("Create Account", "Enter your username:")
            password = simpledialog.askstring("Create Account", "Enter your password:", show='*')

            if username in users:
                messagebox.showerror("Create Account", "Username already exists.")
                return self.authenticate_user()
            else:
                initial_deck = create_initial_deck(CARDS_FILE)

        users[username] = {
            'password': password,
            'deck': [card.to_dict() for card in initial_deck],
            'gold': 100,
            'experience': 0,
            'level': 1
        }
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f)
        messagebox.showinfo("Create Account", "Account created successfully!")
        self.deck = initial_deck
        self.gold = 100
        self.experience = 0
        self.level = 1
        return username

    def initialize_user_interface(self):
        self.initialize_main_tab()
        self.initialize_inventory_tab()

    def initialize_main_tab(self):
        self.chat_area = scrolledtext.ScrolledText(self.main_tab)
        self.chat_area.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_area.config(state=tk.DISABLED)

        self.message_entry = tk.Entry(self.main_tab)
        self.message_entry.pack(padx=10, pady=10, fill=tk.X)
        self.message_entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.main_tab, text="Send", command=self.send_message)
        self.send_button.pack(padx=10, pady=10)

        self.solo_game_button = tk.Button(self.main_tab, text="Start Solo Game", command=self.start_solo_game)
        self.solo_game_button.pack(padx=10, pady=10)

        self.status_label = tk.Label(self.main_tab, text="Connecting...", fg="blue")
        self.status_label.pack(padx=10, pady=10)

        self.user_list = tk.Listbox(self.main_tab)
        self.user_list.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)
        self.user_list.bind("<Button-3>", self.on_user_right_click)

        self.users = {}
        self.private_tabs = {}

    def initialize_inventory_tab(self):
        self.card_vars = {}
        self.card_checkbuttons = []
        self.card_images = {}
        self.selected_cards = []  # Liste pour suivre les cartes sélectionnées

        # Utiliser ScrolledFrame pour permettre le défilement et définir la taille
        self.scrolled_frame = ScrolledFrame(self.inventory_tab, width=400, height=300)
        self.scrolled_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

        # ScrolledFrame pour afficher les cartes sélectionnées
        self.selected_scrolled_frame = ScrolledFrame(self.inventory_tab, width=200, height=300)
        self.selected_scrolled_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        self.display_inventory()
        self.load_selected_cards()  # Charger les cartes sélectionnées au démarrage

        # Ajouter les boutons pour sauvegarder et supprimer la sélection
        self.save_button = tk.Button(self.inventory_tab, text="Save Selection", command=self.save_selected_cards)
        self.save_button.grid(row=1, column=0, padx=10, pady=10)

        self.clear_button = tk.Button(self.inventory_tab, text="Clear Selection", command=self.clear_selected_cards)
        self.clear_button.grid(row=1, column=1, padx=10, pady=10)

    def display_inventory(self):
        for widget in self.scrolled_frame.scrollable_frame.winfo_children():
            widget.destroy()

        inventory_label = tk.Label(self.scrolled_frame.scrollable_frame, text="Your Cards")
        inventory_label.pack(pady=10)

        for card in self.deck:
            card_var = tk.BooleanVar()
            self.card_vars[card.name] = card_var
            
            frame = tk.Frame(self.scrolled_frame.scrollable_frame)
            frame.pack(anchor="w", padx=5, pady=5)
            
            try:
                # Charger l'image de la carte
                img = Image.open(card.image)
                img = img.resize((62, 62), Image.Resampling.LANCZOS)
                img = ImageTk.PhotoImage(img)
                self.card_images[card.name] = img
                
                label = tk.Label(frame, image=img)
                label.pack(side=tk.LEFT)
            except FileNotFoundError:
                logging.error(f"Image file not found: {card.image}")
                label = tk.Label(frame, text="Image not found")
                label.pack(side=tk.LEFT)

            cb = tk.Checkbutton(frame, text=str(card), variable=card_var,
                                command=lambda c=card, v=card_var: self.update_selected_cards(c, v))
            cb.pack(side=tk.LEFT)

            self.card_checkbuttons.append(cb)

        refresh_button = tk.Button(self.scrolled_frame.scrollable_frame, text="Refresh", command=self.display_inventory)
        refresh_button.pack(pady=10)

        self.gold_label = tk.Label(self.scrolled_frame.scrollable_frame, text=f"Gold: {self.gold}")
        self.gold_label.pack()

    def update_selected_cards(self, card, card_var):
        if card_var.get():
            if len(self.selected_cards) < 5:
                self.selected_cards.append(card)
            else:
                messagebox.showwarning("Selection Limit", "You can only select up to 5 cards.")
                card_var.set(False)
        else:
            if card in self.selected_cards:
                self.selected_cards.remove(card)

        self.display_selected_cards()
        self.save_selected_cards()  # Enregistrer les cartes sélectionnées

    def display_selected_cards(self):
        for widget in self.selected_scrolled_frame.scrollable_frame.winfo_children():
            widget.destroy()

        selected_label = tk.Label(self.selected_scrolled_frame.scrollable_frame, text="Selected Cards")
        selected_label.pack(pady=10)

        for card in self.selected_cards:
            try:
                img = self.card_images[card.name]
                label = tk.Label(self.selected_scrolled_frame.scrollable_frame, image=img, text=str(card), compound="top")
                label.pack(pady=5)
            except KeyError:
                label = tk.Label(self.selected_scrolled_frame.scrollable_frame, text=str(card))
                label.pack(pady=5)

    def save_selected_cards(self):
        selected_cards_data = [card.to_dict() for card in self.selected_cards]
        with open('selected_cards.json', 'w') as f:
            json.dump(selected_cards_data, f)
        messagebox.showinfo("Save Selected Cards", "Selected cards have been saved successfully!")

    def clear_selected_cards(self):
        self.selected_cards.clear()
        for card_var in self.card_vars.values():
            card_var.set(False)
        self.display_selected_cards()

    def load_selected_cards(self):
        if os.path.exists('selected_cards.json'):
            with open('selected_cards.json', 'r') as f:
                selected_cards_data = json.load(f)
            self.selected_cards = [Card(**card_data) for card_data in selected_cards_data]
            self.display_selected_cards()
        else:
            messagebox.showwarning("Load Selected Cards", "No saved selected cards found.")

    def start_solo_game(self):
        # Charger les cartes sélectionnées pour l'utilisateur actuel
        if os.path.exists('selected_cards.json'):
          with open('selected_cards.json', 'r') as f:
               selected_cards_data = json.load(f)
          player_cards = [Card(**card_data) for card_data in selected_cards_data]

          # Créer un joueur IA avec un deck aléatoire
          ai_deck = create_initial_deck(CARDS_FILE)  # Utilisez la même fonction pour créer un deck pour l'IA
          ai_player = AIPlayer(ai_deck)

          # Ouvrir une nouvelle fenêtre pour le jeu Triple Triad contre l'IA
          game_window = tk.Toplevel(self.root)
          game = TripleTriadGame(game_window, player_cards, ai_player.hand, ai_player)
        else:
          messagebox.showwarning("Solo Game", "No saved selected cards found.")

    def listen_for_connections(self):
        while True:
            conn, addr = self.socket.accept()
            data = conn.recv(1024)
            if data:
                message = data.decode('utf-8')
                if message.startswith('DEFY'):
                    opponent, cards_json = message.split(':', 1)
                    opponent_cards = json.loads(cards_json)
                    self.accept_defy(opponent, opponent_cards)

    def connect_to_server(self):
        self.server = 'irc.libera.chat'
        self.port = 6667

        self.reactor = irc.client.Reactor()
        try:
            self.connection = self.reactor.server().connect(self.server, self.port, self.nickname)
            self.connection.encoding = 'utf-8'
            self.connection.errors = 'ignore'
            self.connection.add_global_handler("welcome", self.on_connect)
            self.connection.add_global_handler("pubmsg", self.on_pubmsg)
            self.connection.add_global_handler("privmsg", self.on_privmsg)
            self.connection.add_global_handler("join", self.on_join)
            self.connection.add_global_handler("part", self.on_part)
            self.connection.add_global_handler("quit", self.on_quit)
            self.connection.add_global_handler("nick", self.on_nick)
            self.connection.add_global_handler("namreply", self.on_names)
            logging.info("Connected to the server")
        except irc.client.ServerConnectionError as e:
            logging.error(f"Could not connect to server: {e}")
            self.status_label.config(text="Connection Failed", fg="red")

    def on_connect(self, connection, event):
        logging.info("Server connection established.")
        connection.join(self.channel)
        self.status_label.config(text="Connected", fg="green")
        logging.info("Joined channel")

    def on_pubmsg(self, connection, event):
        message = f"[{event.target}] {event.source.nick}: {event.arguments[0]}"
        self.display_message(self.chat_area, message)
        logging.info(f"Message received: {message}")

    def on_privmsg(self, connection, event):
        sender = event.source.nick
        message = f"[Private] {sender}: {event.arguments[0]}"
        if sender not in self.private_tabs:
            self.create_private_tab(sender)
        self.display_message(self.private_tabs[sender]['chat_area'], message)

        # Vérifier si le message est une acceptation de défi
        if event.arguments[0].strip() == "/accept":
            self.initiate_defy(sender)
        logging.info(f"Private message received: {message}")

    def send_message(self, event=None):
        message = self.message_entry.get()
        if message:
            self.connection.privmsg(self.channel, message)
            self.display_message(self.chat_area, f"[You]: {message}")
            self.message_entry.delete(0, tk.END)
            logging.info(f"Message sent: {message}")

    def send_private_message(self, target):
        message = simpledialog.askstring("Private Message", f"Enter message to {target}:")
        if message:
            self.connection.privmsg(target, message)
            if target not in self.private_tabs:
                self.create_private_tab(target)
            self.display_message(self.private_tabs[target]['chat_area'], f"[Private to {target}]: {message}")
            logging.info(f"Private message sent to {target}: {message}")

    def display_message(self, chat_area, message):
        chat_area.config(state=tk.NORMAL)
        chat_area.insert(tk.END, message + "\n")
        chat_area.yview(tk.END)
        chat_area.config(state=tk.DISABLED)

    def on_join(self, connection, event):
        logging.info(f"{event.source.nick} joined the channel")
        self.users[event.source.nick] = event.source.nick
        self.update_user_list()

    def on_part(self, connection, event):
        logging.info(f"{event.source.nick} left the channel")
        if event.source.nick in self.users:
            del self.users[event.source.nick]
            self.update_user_list()

    def on_quit(self, connection, event):
        logging.info(f"{event.source.nick} quit the channel")
        if event.source.nick in self.users:
            del self.users[event.source.nick]
            self.update_user_list()

    def on_nick(self, connection, event):
        logging.info(f"{event.source.nick} changed nick to {event.target}")
        if event.source.nick in self.users:
            self.users[event.target] = self.users.pop(event.source.nick)
            self.update_user_list()

    def on_names(self, connection, event):
        logging.info("Received names list")
        users = event.arguments[2].split()
        for user in users:
            self.users[user] = user
        self.update_user_list()

    def update_user_list(self):
        self.user_list.delete(0, tk.END)
        for user in sorted(self.users.keys()):
            self.user_list.insert(tk.END, user)

    def on_user_right_click(self, event):
        index = self.user_list.nearest(event.y)
        target = self.user_list.get(index)

        menu = tk.Menu(self.user_list, tearoff=0)
        menu.add_command(label="Send Private Message", command=lambda: self.send_private_message(target))
        menu.add_command(label="Defy", command=lambda: self.defy_user(target))
        menu.post(event.x_root, event.y_root)

   
    
    def defy_user(self, target):
        # Envoyer un message de défi à l'utilisateur cible
        self.connection.privmsg(target, f"I challenge you to a Triple Triad game! Type '/accept' to accept.")
        # Envoyer les cartes sélectionnées au joueur défié via socket
        selected_cards_data = [card.to_dict() for card in self.selected_cards]
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', self.port))
            s.sendall(f'DEFY:{json.dumps(selected_cards_data)}'.encode('utf-8'))

    def accept_defy(self, opponent, opponent_cards):
        # Charger les cartes sélectionnées pour l'utilisateur actuel
        if os.path.exists('selected_cards.json'):
            with open('selected_cards.json', 'r') as f:
                selected_cards_data = json.load(f)
            player_cards = [Card(**card_data) for card_data in selected_cards_data]

            # Ouvrir une nouvelle fenêtre pour le jeu Triple Triad
            game_window = tk.Toplevel(self.root)
            game = TripleTriadGame(game_window, player_cards, opponent_cards)
        else:
            messagebox.showwarning("Defy", "No saved selected cards found.")

    def create_private_tab(self, user):
        if user in self.private_tabs:
            return

        private_tab = ttk.Frame(self.notebook)
        self.notebook.add(private_tab, text=f"Private - {user}")

        chat_area = scrolledtext.ScrolledText(private_tab)
        chat_area.pack(expand=True, fill=tk.BOTH)
        chat_area.config(state=tk.DISABLED)

        self.private_tabs[user] = {'frame': private_tab, 'chat_area': chat_area}

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        threading.Thread(target=self.reactor.process_forever, daemon=True).start()
        self.root.mainloop()

    def quit(self):
        self.connection.quit("Goodbye!")
        self.root.destroy()

def main():
    root = tk.Tk()
    client = IRCClient(root)
    client.run()

if __name__ == "__main__":
    main()