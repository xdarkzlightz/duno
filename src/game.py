from asyncio import TimeoutError
from random import randint, shuffle

from discord.utils import get

from embed import embed_hand, embed_turn
from player import Player


def card_matches(card, hand):
    """Checks if the colour/value matches the card in the players hand"""
    wilds = ["wild", "wild+4"]
    matches = False
    for player_card in hand:
        if matches:
            break
        elif player_card[0] in wilds:
            matches = True
        elif card[0] in wilds and player_card[0] == card[1]:
            matches = True
        elif player_card[0] == card[0] or player_card[1] == card[1]:
            matches = True
    return matches


class Game:
    """Game class for uno"""

    def __init__(self, owner_id, owner_name, channel_id, bot):
        self.owner_id = owner_id
        self.channel_id = channel_id
        self.players = {}
        self.turn_order = []
        self.turn = 0
        self.started = False
        self.current_card = None
        self.deck = None
        self.discard_pile = []
        self.previous_player = None
        self.last_message = None
        self.bot = bot
        self.deleted = False

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

        matches = card_matches(self.current_card,
                               self.players[self.turn_order[self.turn]].hand)
        while matches is False:
            matches = card_matches(
                self.current_card,
                self.players[self.turn_order[self.turn]].hand)

            self.give_cards(self.turn_order[self.turn], 1)

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
        self.previous_player = self.players[self.turn_order[self.turn]]

        if self.turn + 1 > len(self.turn_order) - 1:
            self.turn = 0
        else:
            self.turn += 1

        # If the player can't play then draw a card
        matches = card_matches(self.current_card,
                               self.players[self.turn_order[self.turn]].hand)
        while matches is False:
            matches = card_matches(
                self.current_card,
                self.players[self.turn_order[self.turn]].hand)

            self.give_cards(self.turn_order[self.turn], 1)

    async def start_afk_loop(self):
        """Starts an AFK timeout loop until a player plays"""

        # Add strikes, if a player reaches 3 strikes they get removed
        # Add game AFK timer using a similar way
        def pred(ctx):
            command_name = ctx.command.name
            if command_name == "play" and self.turn_order[
                    self.turn] == ctx.author.id:
                return True
            else:
                return False

        try:
            await self.bot.wait_for('command', check=pred, timeout=10.0)
        except TimeoutError:
            print(self.deleted)
            if self.deleted:
                return
            player = self.players[self.turn_order[self.turn]]
            player.strikes += 1
            self.next_turn()
            self.give_cards(player.player_id, 1)
            embed = embed_turn(
                action=f"{player.player_name} took to long to play", game=self)
            channel = await self.bot.fetch_channel(self.channel_id)
            last_message = await channel.fetch_message(self.last_message)
            await last_message.delete()
            msg = await channel.send(embed=embed)
            self.last_message = msg.id

            if player.strikes == 3:
                del self.players[player.player_id]
                self.turn_order.remove(player.player_id)
                await channel.send(player.player_name +
                                   " got kicked for being AFK")
                if len(self.players) == 1:
                    return

            if len(str(self.turn_order[self.turn])) == 18:
                member = get(channel.guild.members,
                             id=self.turn_order[self.turn])
                dm_channel = member.dm_channel
                if dm_channel is None:
                    await member.create_dm()
                    dm_channel = member.dm_channel
                embed = embed_hand(player_id=self.turn_order[self.turn],
                                   action="It's your turn!",
                                   game=self)
                await dm_channel.send(embed=embed)
            await self.start_afk_loop()

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
