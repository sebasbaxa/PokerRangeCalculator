from collections import defaultdict
import random
import tkinter as tk
from tkinter import messagebox


#Classes to calulate poker hands and ranges
class Card:
    
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    

    def __eq__(self, other):
        return self.suit == other.suit and self.rank == other.rank

    def __str__(self):
        return f'{self.rank} of {self.suit}'

class Deck:
    
    def __init__(self):
        self.cards = []
        for suit in ['hearts', 'diamonds', 'clubs', 'spades']:
            for rank in range(2, 15):
                self.cards.append(Card(suit, rank))

    def remove_hand(self, hand):
        self.cards.remove(hand.card1)
        self.cards.remove(hand.card2)
    
    def add_hand(self, hand):
        self.cards.append(hand.card1)
        self.cards.append(hand.card2)

    def remove(self, card):
        self.cards.remove(card)

    def add(self, card):
        self.cards.append(card)

class utils:

    def find_straight_flush(self, cards):

        # Group cards by suit
        suits = defaultdict(list)
        for card in cards:
            suits[card.suit].append(card)

        # Check each suit for a straight flush
        for suit, suited_cards in suits.items():
            if len(suited_cards) < 5:
                continue

            # Sort cards by rank
            suited_cards.sort(key=lambda x: x.rank)

            # Add Ace as rank 1 if it exists
            if suited_cards[-1].rank == 14:
                suited_cards.append(Card(suited_cards[-1].suit, 1))

            # Check for straight flush
            for i in range(len(suited_cards) - 5, -1, -1):
                if (suited_cards[i].rank + 1 == suited_cards[i + 1].rank and
                    suited_cards[i].rank + 2 == suited_cards[i + 2].rank and
                    suited_cards[i].rank + 3 == suited_cards[i + 3].rank and
                    suited_cards[i].rank + 4 == suited_cards[i + 4].rank):
                    return suited_cards[i:i+5]

        return None

    def find_four_of_a_kind(self, cards):

        # Group cards by rank
        ranks = defaultdict(list)
        for card in cards:
            ranks[card.rank].append(card)

        # Check for four of a kind
        for rank, rank_cards in ranks.items():
            if len(rank_cards) == 4:
                return rank_cards

        return None

    def find_full_house(self, cards):

        # Group cards by rank
        ranks = defaultdict(list)
        for card in cards:
            ranks[card.rank].append(card)

        # Check for three of a kind
        highest_three = 0
        for rank, rank_cards in ranks.items():
            if len(rank_cards) == 3:
                if rank > highest_three:
                    highest_three = rank
        if highest_three == 0:
            return None
        three_of_a_kind = ranks[highest_three]

        if three_of_a_kind is None:
            return None

        # Check for a pair
        highest_pair = 0
        for rank, rank_cards in ranks.items():
            if len(rank_cards) >= 2 and rank_cards[0] != three_of_a_kind[0]:
                if rank > highest_pair:
                    highest_pair = rank
        if highest_pair == 0:
            return None
        pair = ranks[highest_pair]
        return three_of_a_kind + pair[:2]
        
    def find_flush(self, cards):

        # Group by suits
        suits = defaultdict(list)
        for card in cards:
            suits[card.suit].append(card)
        for suits, suited_cards in suits.items():
            if len(suited_cards) >= 5:
                suited_cards.sort(key=lambda x: x.rank)
                return suited_cards[-5:]

    def find_straight(self, cards):

        # Sort cards by rank
        cards.sort(key=lambda x: x.rank)

        # Add Ace as rank 1 if it exists
        if cards[-1].rank == 14:
            cards.append(Card(cards[-1].suit, 1))

        # Check for straight
        for i in range(len(cards) - 5, -1, -1):
            if (cards[i].rank + 1 == cards[i + 1].rank and
                cards[i].rank + 2 == cards[i + 2].rank and
                cards[i].rank + 3 == cards[i + 3].rank and
                cards[i].rank + 4 == cards[i + 4].rank):
                return cards[i:i+5]

        return None

    def find_three_of_a_kind(self, cards):

        # Group cards by rank
        ranks = defaultdict(list)
        for card in cards:
            ranks[card.rank].append(card)

        # Check for three of a kind
        highest_rank = 0
        for rank, rank_cards in ranks.items():
            if len(rank_cards) == 3 and rank > highest_rank:
                highest_rank = rank
        if highest_rank != 0:
            # Collect remaining cards that are not part of the three of a kind
            remaining_cards = [card for card in cards if card.rank != highest_rank]
            remaining_cards.sort(key=lambda x: x.rank, reverse=True)
            return ranks[highest_rank] + remaining_cards[:2]

        return None

    def find_two_pair(self, cards):
        
        # Group cards by rank
        ranks = defaultdict(list)
        for card in cards:
            ranks[card.rank].append(card)

        # Check for two pairs
        kicker = 0
        card = None
        pairs = []
        for rank, rank_cards in ranks.items():
            if len(rank_cards) >= 2:
                pairs.append(rank_cards)
            else:
                if rank > kicker:
                    kicker = rank
                    card = rank_cards[0]
        if len(pairs) >= 2:
            pairs.sort(key=lambda x: x[0].rank, reverse=True)
            return pairs[0] + pairs[1] + [card]

        return None

    def find_pair(self, cards):
        
        # Group cards by rank
        ranks = defaultdict(list)
        for card in cards:
            ranks[card.rank].append(card)

        # Check for a pair and get the top three cards
        top_rank = 0
        for rank, rank_cards in ranks.items():
            if len(rank_cards) == 2 and rank > top_rank:
                top_rank = rank
        top_pair = ranks[top_rank] 
        if top_pair:
             # Collect remaining cards that are not part of the pair
            remaining_cards = [card for card in cards if card.rank != top_rank]
            remaining_cards.sort(key=lambda x: x.rank, reverse=True)
            top_three_remaining = remaining_cards[:3]
            return top_pair + top_three_remaining
        return None

    def find_high_card(self, cards):
        cards.sort(key=lambda x: x.rank, reverse=True)
        return cards[:5]

    def find_best_hand(self, cards):

        # Check for straight flush
        straight_flush = self.find_straight_flush(cards)
        if straight_flush:
            return 9, straight_flush

        # Check for four of a kind
        four_of_a_kind = self.find_four_of_a_kind(cards)
        if four_of_a_kind:
            return 8, four_of_a_kind

        # Check for full house
        full_house = self.find_full_house(cards)
        if full_house:
            return 7, full_house

        # Check for flush
        flush = self.find_flush(cards)
        if flush:
            return 6, flush

        # Check for straight
        straight = self.find_straight(cards)
        if straight:
            return 5, straight

        # Check for three of a kind
        three_of_a_kind = self.find_three_of_a_kind(cards)
        if three_of_a_kind:
            return 4, three_of_a_kind

        # Check for two pair
        two_pair = self.find_two_pair(cards)
        if two_pair:
            return 3, two_pair

        # Check for pair
        pair = self.find_pair(cards)
        if pair:
            return 2, pair

        # High card
        high_card = self.find_high_card(cards)
        return 1, high_card

    def compare_combos(self, hand1, hand2):

        hand1_type = hand1[0]
        hand2_type = hand2[0]
        best_hand1 = hand1[1]
        best_hand2 = hand2[1]
        if hand1_type > hand2_type:
            return 1
        elif hand1_type < hand2_type:
            return -1
        else:
            for card1, card2 in zip(best_hand1, best_hand2):
                if card1.rank > card2.rank:
                    return 1
                elif card1.rank < card2.rank:
                    return -1
        return 0

    def display_best_hand(self, cards):
        hand_type, best_hand = self.find_best_hand(cards)
        print(hand_type)
        for card in best_hand:
            print(str(card))

class CardRange:
    
    def __init__(self):
        self.card_range = []
        
    def add(self, hand):
        self.card_range.append(hand)

    def remove(self, hand):
        self.card_range.remove(hand)
    
    def add_range(self, hands):
        for hand in hands:
            self.card_range.append(hand)
        
    def get_range(self):
        return [(str(hand)) for hand in self.card_range]
    
class Hand:
    def __init__(self, card1, card2):
        self.card1 = card1
        self.card2 = card2
    
    def __eq__(self, other):
        return self.card1 == other.card1 and self.card2 == other.card2

    def __str__(self):
        return f'{self.card1}, {self.card2}'
    
class simulate_range_vs_range:
    
    def __init__(self, hero, villian, board):
        self.hero = hero
        self.villian = villian
        self.board = board

    def simulate_flop_turn_river(self):
        deck = Deck()
        #get random hand from hero
        random_hero_hand = self.hero.card_range[random.randint(0, len(self.hero.card_range)-1)]

        #get random hand from villian
        random_villian_hand = self.villian.card_range[random.randint(0, len(self.villian.card_range)-1)]

        #check if villian and hero have any cards that are the same and redo if they do
        while random_hero_hand.card1 == random_villian_hand.card1 or random_hero_hand.card1 == random_villian_hand.card2 or random_hero_hand.card2 == random_villian_hand.card1 or random_hero_hand.card2 == random_villian_hand.card2:
            random_villian_hand = self.villian.card_range[random.randint(0, len(self.villian.card_range)-1)]

        #remove the hands from the deck
        deck.remove_hand(random_hero_hand)
        deck.remove_hand(random_villian_hand)

        #get random board
        random_board = []
        for i in range(5):
            rand_card = deck.cards[random.randint(0, len(deck.cards)-1)]
            random_board.append(rand_card)
            deck.remove(rand_card)
        
        #return the hands and the board
        return random_hero_hand, random_villian_hand, random_board

class RunSimulations:

    def __init__(self, hero_range, villian_range, board, num_simulations):
        self.hero_range = hero_range
        self.villian_range = villian_range
        self.board = board
        self.num_simulations = num_simulations
    
    def run(self):
        hero_wins = 0
        villian_wins = 0
        split = 0

        #run the simulations
        for i in range(self.num_simulations):
            #get random hands and board
            simulation = simulate_range_vs_range(self.hero_range, self.villian_range, self.board).simulate_flop_turn_river()
            board = simulation[2]
            hero_hand = simulation[0]
            villian_hand = simulation[1]
            hero_combo = board + [hero_hand.card1, hero_hand.card2]
            villian_combo = board + [villian_hand.card1, villian_hand.card2]

            #find the best hand for each player
            hero_best_combo = utils().find_best_hand(hero_combo)
            villian_best_combo = utils().find_best_hand(villian_combo)

            #compare the best hands
            if utils().compare_combos(hero_best_combo, villian_best_combo) == 1:
                hero_wins += 1
            elif utils().compare_combos(hero_best_combo, villian_best_combo) == -1:
                villian_wins += 1
            else:
                split += 1

        hero_win_rate = hero_wins/self.num_simulations
        villian_win_rate = villian_wins/self.num_simulations
        split_rate = split/self.num_simulations
        return hero_win_rate, villian_win_rate, split_rate
        
class MakeRange:

    def pocket_pair(self, rank):
        hands = []
        used_suits = []
        for suit1 in ['hearts', 'diamonds', 'clubs', 'spades']:
            card1 = Card(suit1, rank)
            for suit2 in ['hearts', 'diamonds', 'clubs', 'spades']:
                if suit2 != card1.suit and suit2 not in used_suits:
                    card2 = Card(suit2, rank) 
                    hands.append(Hand(card1, card2))   
                    used_suits.append(suit1) 
        return hands

    def suited_hand(self, rank1, rank2):
        hands = []
        for suit in ['hearts', 'diamonds', 'clubs', 'spades']:
            card1 = Card(suit, rank1)
            card2 = Card(suit, rank2)
            hands.append(Hand(card1, card2))
        return hands
    
    def offsuit_hand(self, rank1, rank2):
        hands = []
        used_suits = []
        for suit1 in ['hearts', 'diamonds', 'clubs', 'spades']:
            for suit2 in ['hearts', 'diamonds', 'clubs', 'spades']:
                if suit1 != suit2 and suit2 not in used_suits:
                    card1 = Card(suit1, rank1)
                    card2 = Card(suit2, rank2)
                    hands.append(Hand(card1, card2))
                    used_suits.append(suit1)
        return hands
    
    def full_range(self):
        hands = []
        for rank in range(2, 15):
            for hand in self.pocket_pair(rank):
                hands.append(hand)
        for rank1 in range(2, 15):
            for rank2 in range(2, 15):
                if rank1 != rank2:
                    for hand in self.suited_hand(rank1, rank2):
                        hands.append(hand)
                    for hand in self.offsuit_hand(rank1, rank2):
                        hands.append(hand)
        return hands
    
class Cell:
    def __init__(self, title):
        self.title = title
        self.hands = []

    def add_hand(self, hand):
        self.hands.append(hand)
    
    def display_hands(self):
        for hand in self.hands:
            print(hand)

class Viewer:
    def __init__(self):
        self.grid = [[None] * 13 for _ in range(13)]
        self.rank_map = {14: 'A', 13: 'K', 12: 'Q', 11: 'J', 10: 'T'}
        self.ranks = [14, 13, 12, 11, 10] + list(range(9, 1, -1))  # Ranks from Ace (14) to 2
        self.value_grid = [[0] * 13 for _ in range(13)]

        for i in range(13):
            for j in range(13):
                rank_i = self.rank_map.get(self.ranks[i], str(self.ranks[i]))
                rank_j = self.rank_map.get(self.ranks[j], str(self.ranks[j]))
                if i == j:
                    # Pocket pairs
                    self.grid[i][j] = Cell(f'{rank_i}{rank_j}: ')
                    for hand in MakeRange().pocket_pair(self.ranks[i]):
                        self.grid[i][j].add_hand(hand)
                elif i < j:
                    # Suited hands
                    self.grid[i][j] = Cell(f'{rank_j}{rank_i}s: ')
                    for hand in MakeRange().suited_hand(self.ranks[i], self.ranks[j]):
                        self.grid[i][j].add_hand(hand)
                    # Offsuit hands
                else:
                    self.grid[i][j] = Cell(f'{rank_i}{rank_j}o: ')
                    for hand in MakeRange().offsuit_hand(self.ranks[i], self.ranks[j]):
                        self.grid[i][j].add_hand(hand)

    def display_grid(self):
        for i in range(13):
            row = []
            for j in range(13):
                cell = self.grid[i][j]
                win_rate = self.value_grid[i][j]
                row.append(f'{cell.title:<6}{win_rate:>6.2f}')
            print('|'.join(row))
    
    def find_hand_position(self, hand):
        rank1 = hand.card1.rank
        rank2 = hand.card2.rank
        suit1 = hand.card1.suit
        suit2 = hand.card2.suit

        if rank1 == rank2:  # Pocket pair
            i = self.ranks.index(rank1)
            return i, i
        elif suit1 == suit2:  # Suited hand
            i = self.ranks.index(rank1)
            j = self.ranks.index(rank2)
            return (i, j) if rank1 > rank2 else (j, i)
        else:  # Offsuit hand
            i = self.ranks.index(rank1)
            j = self.ranks.index(rank2)
            return (j, i) if rank1 > rank2 else (i, j)

    def update_win(self, hand, win_rate):
        i, j = self.find_hand_position(hand)
        new_win_rate = (self.value_grid[i][j] + win_rate) / 2
        self.value_grid[i][j] = new_win_rate
    
    def reset(self):
        self.value_grid = [[0] * 13 for _ in range(13)]


# GUI code
class HandSelector:
    def __init__(self, root, range_obj, selected_buttons):
        self.root = root
        self.range_obj = range_obj
        self.make_range = MakeRange()
        self.selected_buttons = selected_buttons
        self.buttons = {}
        self.rank_map = {14: 'A', 13: 'K', 12: 'Q', 11: 'J', 10: 'T'} # Map for converting ranks
        self.create_hand_grid()

    def create_hand_grid(self):
        # Create a new window for the grid
        grid_window = tk.Toplevel(self.root)
        grid_window.title("Select Hands")
        grid_window.geometry("800x650")

        # Create a frame for the grid
        grid_frame = tk.Frame(grid_window)
        grid_frame.pack(pady=10)

        # Generate all possible hands
        ranks = list(range(14, 1, -1))  # Ace (14) to 2
        self.buttons = {}  # Store button references to disable them later

        for i, rank1 in enumerate(ranks):
            for j, rank2 in enumerate(ranks):
                # Convert ranks to characters
                rank1_label = self.rank_map.get(rank1, str(rank1))
                rank2_label = self.rank_map.get(rank2, str(rank2))


                if i == j:
                    # Pocket pairs
                    hand_label = f"{rank1_label}{rank1_label}"
                    hands = self.make_range.pocket_pair(rank1)
                elif i < j:
                    # Suited hands
                    hand_label = f"{rank2_label}{rank1_label}s"
                    hands = self.make_range.suited_hand(rank1, rank2)
                else:
                    # Offsuit hands
                    hand_label = f"{rank1_label}{rank2_label}o"
                    hands = self.make_range.offsuit_hand(rank1, rank2)

                # Create a button for the hand
                button = tk.Button(
                    grid_frame,
                    text=hand_label,
                    width=6,
                    height=2,
                    command=lambda h=hands, b=(i, j): self.add_to_range(h, b)
                )
                button.grid(row=i, column=j, padx=2, pady=2)

                # Store the button reference
                self.buttons[(i, j)] = button

                # Check to see if hand is already in the range
                if self.is_button_selected((i, j)):
                    button.config(text="Selected", state="disabled", bg="gray", fg="white")

    # button to add all hands to the range
        add_all_button = tk.Button(
            grid_window,
            text="Add All Hands",
            command=self.add_all_hands,
            bg="green",
            fg="white",
            font=("Arial", 12, "bold")
        )
        add_all_button.pack(pady=10)
    
    def is_button_selected(self, button_coords):
        for coords in self.selected_buttons:
            if coords == button_coords:
                return True
        return False
   

    def add_to_range(self, hands, button_coords):
        # Add the hand to the range
        self.range_obj.add_range(hands)

        # Disable the button and change its appearance
        button = self.buttons[button_coords]
        button.config(text="Selected", state="disabled", bg="gray", fg="white")
        self.selected_buttons.append(button_coords)  # Store the selected button coordinates
    
    def add_all_hands(self):
        # Iterate through all buttons and add their corresponding hands to the range
        for coords, button in self.buttons.items():
            if button["state"] != "disabled":  # Only process buttons that are not already selected
                rank1, rank2 = coords
                # Adjust rank index
                rank1 = 14 - rank1
                rank2 = 14 - rank2

                if rank1 == rank2:
                    hands = self.make_range.pocket_pair(rank1) 
                elif rank1 < rank2:
                    hands = self.make_range.suited_hand(rank1, rank2)
                else:
                    hands = self.make_range.offsuit_hand(rank1, rank2)

                self.range_obj.add_range(hands)
                button.config(text="Selected", state="disabled", bg="gray", fg="white")
                self.selected_buttons.append(coords)  # Store the selected button coordinates

class HandGridDisplay:
    def __init__(self, root, viewer):
        self.root = root
        self.viewer = viewer
        self.labels = [[None] * 13 for _ in range(13)]  # Store label references for updating

        self.create_hand_grid()

    def create_hand_grid(self):
        # Create a frame for the grid
        grid_frame = tk.Frame(self.root)
        grid_frame.pack(pady=10)

        # Generate the grid of hands
        for i in range(13):
            for j in range(13):
                cell = self.viewer.grid[i][j]
                hand_label = cell.title.strip(": ")  # Get the hand label (e.g., "AA", "AKs", "KQo")
                win_rate = self.viewer.value_grid[i][j]  # Initial win rate (0.00)

                # Create a label for each hand
                label = tk.Label(
                    grid_frame,
                    text=f"{hand_label}\n{win_rate:.2f}%",
                    width=7,
                    height=3,
                    relief="solid",
                    bg="white",
                    fg="black"
                )
                label.grid(row=i, column=j, padx=2, pady=2)

                # Store the label reference for updating later
                self.labels[i][j] = label

    def update_hand_win_rate(self, hand, win_rate):
        # Find the position of the hand in the grid
        i, j = self.viewer.find_hand_position(hand)

        # Update the win rate in the viewer's value grid
        self.viewer.update_win(hand, win_rate)

        # Update the corresponding label text
        self.labels[i][j].config(
            text=f"{self.viewer.grid[i][j].title.strip(': ')}\n{self.viewer.value_grid[i][j]*100:.2f}%"
        )

        # Change the background colors based on win rate
        if self.viewer.value_grid[i][j] > 0.8:
            self.labels[i][j].config(bg="green", fg="white")
        elif self.viewer.value_grid[i][j] > 0.6:
            self.labels[i][j].config(bg="orange", fg="black")
        elif self.viewer.value_grid[i][j] > 0.45:
            self.labels[i][j].config(bg="yellow", fg="black")
        else:
            self.labels[i][j].config(bg="white", fg="black")

class SimulationSettings:
    def __init__(self, root, runs_ref):
        self.root = root
        self.runs_ref = runs_ref

        # Create a new window
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Adjust Simulation Settings")
        settings_window.geometry("400x300")

        # Create a frame for the grid
        settings_frame = tk.Frame(settings_window)
        settings_frame.pack(pady=10)

        # Create a label and entry for the number of simulations
        self.label = tk.Label(settings_window, text="Number of Simulations per hand:")
        self.label.pack(pady=10)

        self.entry = tk.Entry(settings_window)
        self.entry.pack(pady=10)
        self.entry.insert(0, str(self.runs_ref["num_simulations"]))

        # Create a button to set the number of simulations
        self.set_button = tk.Button(
            settings_window,
            text="Set",
            command=self.set_num_simulations,
            bg="blue",
            fg="white",
            font=("Arial", 12, "bold")
        )
        self.set_button.pack(pady=10)

    def set_num_simulations(self):
        try:
            self.runs_ref["num_simulations"] = int(self.entry.get())
            messagebox.showinfo("Success", f"Number of simulations set to {self.runs_ref['num_simulations']}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")


hero_range = CardRange()
hero_selected = []
villian_range = CardRange()
villian_selected = []
runs = {"num_simulations": 100}
viewer = Viewer()

# Create the tkinter window
root = tk.Tk()
root.title("Range Calculator")
root.geometry("800x800")

# menu bar
menu = tk.Menu(root)

# sub menus
ranges = tk.Menu(menu, tearoff=False)
ranges.add_command(label="Hero Range", command=lambda: HandSelector(root, hero_range, hero_selected))
ranges.add_command(label="Villain Range", command=lambda: HandSelector(root, villian_range, villian_selected))
menu.add_cascade(label="Ranges", menu=ranges)

sumulation = tk.Menu(menu, tearoff=False)
sumulation.add_command(label="Set Number of Runs", command=lambda: SimulationSettings(root, runs))
menu.add_cascade(label="Simulation", menu=sumulation)

root.configure(menu=menu)

#display grid of hands
hand_grid_display = HandGridDisplay(root, viewer)

#run simulations and update grid
def calculate():
    for hand in hero_range.card_range:
        temp_range = CardRange()
        temp_range.add(hand)
        sim_results = RunSimulations(temp_range, villian_range, [], runs["num_simulations"]).run()
        viewer.update_win(hand, sim_results[0])
        hand_grid_display.update_hand_win_rate(hand, sim_results[0])

# function to reset the ranges
def reset_ranges():
    hero_range.card_range = []
    villian_range.card_range = []
    hero_selected.clear()
    villian_selected.clear()
    viewer.reset()
    for i in range(13):
        for j in range(13):
            hand_grid_display.labels[i][j].config(
                text=f"{viewer.grid[i][j].title.strip(': ')}\n0.00%",
                bg="white",
                fg="black"
            )
    messagebox.showinfo("Success", "Ranges have been reset.")

# button to run the calculation
calculate_button = tk.Button(
    root,
    text="Run Calculation",
    command=calculate,
    bg="blue",
    fg="white",
    font=("Arial", 12, "bold")
)
calculate_button.place(relx=0.4, rely=0.95, anchor="center")

# reset button to reset the ranges
reset_button = tk.Button(
    root,
    text="Reset Ranges",
    command=reset_ranges,
    bg="red",
    fg="white",
    font=("Arial", 12, "bold")
)

reset_button.place(relx=0.6, rely=0.95, anchor="center")

# Run the tkinter main loop
root.mainloop()


