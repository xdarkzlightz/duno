from random import randint, shuffle

from player import Player
"""
    TODO: Make it so wild cards or special cards can't be the starting card
    TODO: Add AFK timer
    TODO: Add game AFK timer
    TODO: Auto-draw if the player can't play a card
"""


class Game:
    """Game class for uno"""

    def __init__(self, owner_id, owner_name, channel_id):
        self.owner_id = owner_id
        self.channel_id = channel_id
        self.players = {}
        self.turn_order = []
        self.turn = 0
        self.started = False
        self.current_card = None
        self.deck = None
        self.discard_pile = []

        self.add_player(player_id=owner_id, player_name=owner_name)

    def add_player(self, player_id, player_name):
        """Adds a new player to the game"""
        self.players[player_id] = Player(player_id, player_name)
        print(f"A new player has been created: " +
              str(self.players[player_id].player_id))

    def start(self):
        """Starts the uno game"""
        self.create_deck()
        for player_id, player in self.players.items():
            self.turn_order.append(player_id)
            self.give_cards(player_id, 7)

        shuffle(self.turn_order)
        card = self.deck.pop()
        wilds = ["wild", "wild+4"]
        colours = ["red", "green", "blue", "yellow"]
        if card[0] in wilds:
            self.current_card = (card[0], colours[randint(0, 4)])
        else:
            self.current_card = card
        self.discard_pile.append(self.current_card)

        # If the player can't play then draw a card
        wilds = ["wild", "wild+4"]
        matches = False
        for card in self.players[self.turn_order[self.turn]].hand:
            if matches:
                break
            elif card[0] in wilds:
                matches = True
            elif card[0] == self.current_card[0] or card[
                    1] == self.current_card[1]:
                matches = True
        if matches is False:
            self.give_cards(self.turn_order[self.turn], 1)
            self.next_turn()

    def play(self, player_id, colour, value):
        """Plays a card from the specified players hand"""
        self.before_turn()
        wilds = ["wild", "wild+4"]
        player = self.players[player_id]

        if colour in wilds:
            player.hand.remove((colour, ))
            self.current_card = (colour, value)
            self.discard_pile.append((colour))
        else:
            player.hand.remove((colour, value))
            self.current_card = (colour, value)
            self.discard_pile.append((colour, value))

        self.next_turn()
        self.after_turn()

    def before_turn(self):
        """Runs before the turn"""

    def after_turn(self):
        """Runs after a turn"""
        # Do actions for any special cards
        value = self.current_card[1]
        if value == "skip":
            self.next_turn()
        elif value == "reverse":
            self.turn_order.reverse()
        elif value == "+2":
            self.give_cards(self.turn_order[self.turn], 2)
            self.next_turn()
        elif self.current_card[0] == "wild+4":
            self.give_cards(self.turn_order[self.turn], 4)
            self.next_turn()

    def next_turn(self):
        """Goes onto the next turn"""
        if self.turn + 1 > len(self.turn_order) - 1:
            self.turn = 0
        else:
            self.turn += 1

        # If the player can't play then draw a card
        wilds = ["wild", "wild+4"]
        matches = False
        for card in self.players[self.turn_order[self.turn]].hand:
            if matches:
                break
            elif card[0] in wilds:
                matches = True
            elif card[0] == self.current_card[0] or card[
                    1] == self.current_card[1]:
                matches = True
        if matches is False:
            self.give_cards(self.turn_order[self.turn], 1)
            self.next_turn()

    def give_cards(self, player_id, amount):
        """Gives the specified player x amount of cards"""
        player = self.players[player_id]
        for x in range(amount):
            if len(self.deck) == 0:
                self.deck = self.discard_pile.copy()
                del self.discard_pile[:]
            card = self.deck.pop()
            player.hand.append(card)
            self.discard_pile.append(card)

    def create_deck(self):
        """Creates the uno deck"""
        deck = []

        colours = ["red", "green", "blue", "yellow"]

        for colour in range(4):
            deck.append((colours[colour], "0"))
            for x in range(2):
                for value in range(1, 13):
                    val = None
                    if value < 10:
                        val = str(value)
                    else:
                        values = {10: "reverse", 11: "skip", 12: "+2"}
                        val = values[value]
                    deck.append((colours[colour], val))

        for num in range(2):
            for y in range(4):
                if num == 0:
                    deck.append(("wild", ))
                else:
                    deck.append(("wild+4", ))

        shuffle(deck)
        self.deck = deck
