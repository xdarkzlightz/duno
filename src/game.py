from random import shuffle

from player import Player


class Game:
    """Game class for uno"""

    # A dictionary of all the players in the game
    players = {}

    turn_order = []
    turn = 0

    def __init__(self, owner_id, owner_name, channel_id):
        self.owner_id = owner_id
        self.channel_id = channel_id
        self.add_player(player_id=owner_id, player_name=owner_name)

    def add_player(self, player_id, player_name):
        """Adds a new player to the game"""
        self.players[player_id] = Player(player_id, player_name)
        print(f"A new player has been created: " +
              str(self.players[player_id].player_id))

    def start(self):
        """Starts the uno game"""
        self.create_deck()
        for player_id, val in self.players:
            self.turn_order.append(player_id)
        shuffle(self.turn_order)

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
