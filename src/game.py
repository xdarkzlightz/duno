from random import shuffle

from player import Player
"""
    TODO: Make it so wild cards or special cards can't be the starting card
    TODO: Create before/after turn functions for special cards
    TODO: Add AFK timer
    TODO: Add game AFK timer
    TODO: Make special cards work
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
            for num in range(7):
                card = self.deck.pop()
                player.hand.append(card)
                self.discard_pile.append(card)

        shuffle(self.turn_order)
        print(self.turn_order)
        self.current_card = self.deck.pop()
        self.discard_pile.append(self.current_card)
        print(self.current_card)

    def play(self, player_id, colour, value):
        """Plays a card from the specified players hand"""
        wilds = ["wild", "wild+4"]
        player = self.players[player_id]

        if colour in wilds:
            player.hand.remove((colour, ))
            self.current_card = (colour, value)
        else:
            player.hand.remove((colour, value))
            self.current_card = (colour, value)

        self.next_turn()

    def next_turn(self):
        """Goes onto the next turn"""
        if self.turn + 1 > len(self.turn_order) - 1:
            self.turn = 2
        else:
            self.turn += 1

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
        print(deck)
        self.deck = deck
