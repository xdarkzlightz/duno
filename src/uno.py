import typing
from random import randint

from discord import Embed
from discord.errors import Forbidden
from discord.ext import commands
from discord.utils import get

from checks import card_matches, check_win, game_exists, valid_card
from embed import embed_hand, embed_turn
from game import Game
"""
    TODO: Delete old game messages, send a new one whenever players message
"""


def get_action_response(author, game):
    """Gets a response for an action"""
    wilds = ["wild", "wild+4"]
    specials = ["skip", "+2", "reverse"]
    colour = game.current_card[0]
    value = game.current_card[1]
    previous_player = game.previous_player.player_name

    if colour in wilds:
        colour_change = f"{author} changed the colour to {value}"
        plus_four = f" and made {previous_player} draw 4 cards"
        return colour_change if colour == "wild" else colour_change + plus_four
    elif value in specials:
        if value == "+2":
            return f"{author} made {previous_player} draw 2 cards"
        elif value == "skip":
            return f"{author} skipped {previous_player}"
        elif value == "reverse":
            return f"{author} reversed the turn rotation"
    else:
        return f"{author} played a card"


class Uno(commands.Cog):
    games = {}

    def __init__(self, bot):
        self.bot = bot
        self.dev_su_id = None

    @commands.Cog.listener()
    async def on_command(self, ctx):
        try:
            await ctx.message.delete()
        except Forbidden:
            pass

    @commands.command()
    async def create(self, ctx):
        """Creates a new game"""
        if ctx.channel.id in self.games.keys():
            await ctx.send("A game already exists in the channel!" +
                           " You should join it! `;join`")
            return None

        # Creates a new game and adds it to the games dict
        self.games[ctx.channel.id] = Game(owner_id=ctx.author.id,
                                          owner_name=ctx.author.display_name,
                                          channel_id=ctx.channel.id)
        # Log that a new game has been created
        print(f"New game created: {self.games[ctx.channel.id].channel_id}")
        # Send the new game message
        await ctx.send("Game created, players can join it with `;join`!")

    @commands.command()
    async def join(self, ctx):
        """Joins a game"""
        exists = await game_exists(ctx, self.games)
        if exists is False:
            return None

        game = self.games[ctx.channel.id]
        if ctx.author.id in game.players.keys():
            await ctx.send("You're already in the game!")
            return None

        game.add_player(player_id=ctx.author.id,
                        player_name=ctx.author.display_name)
        print(f"A player has joined game: {game.channel_id}, " +
              "player: {game.players[ctx.author.id].player_id}")

        # Retrieve a list of player names
        players = []
        for player_id, player in game.players.items():
            players.append(player.player_name)
        # Send the joined game message
        embed = Embed(title=f"{ctx.author.display_name} has joined the game!",
                      colour=0x5aea2a)
        embed.add_field(name="Players", value="\n".join(players))
        await ctx.send(embed=embed)

    @commands.command()
    async def players(self, ctx):
        """Shows all the players in the game"""
        exists = await game_exists(ctx, self.games)
        if exists is False:
            return None

        game = self.games[ctx.channel.id]

        players = []
        for player_id, player in game.players.items():
            players.append(player.player_name)

        embed = Embed(colour=0x0fb0d8)
        embed.add_field(name="Players", value="\n".join(players))
        embed.set_footer(text=f"Total: {len(players)}")

        await ctx.send(embed=embed)

    @commands.command()
    async def start(self, ctx):
        """Starts the game"""
        exists = await game_exists(ctx, self.games)
        if exists is False:
            return None
        game = self.games[ctx.channel.id]
        if len(game.players) == 1:
            await ctx.send(
                "Hey don't be alone! You need some friends to play this game! "
                + "(Cannot start game with 1 player)")
            return None

        game.start()

        for player_id, player in game.players.items():
            if len(str(player_id)) == 18:
                member = get(ctx.guild.members, id=player_id)
                dm_channel = member.dm_channel
                if dm_channel is None:
                    await member.create_dm()
                    dm_channel = member.dm_channel
                embed = embed_hand(action="Game started glhf!",
                                   player_id=player_id,
                                   game=game)
                print(dm_channel)
                await dm_channel.send(embed=embed)

        embed = embed_turn(action="Game started, GLHF!", game=game)
        await ctx.send(embed=embed)

    @commands.command()
    async def leave(self, ctx):
        """
        Leaves a game,
        if you're the only person in the game then the game gets deleted
        """
        exists = await game_exists(ctx, self.games)
        if exists is False:
            return None
        game = self.games[ctx.channel.id]

        player_id = ctx.author.id
        if self.dev_su_id is not None:
            player_id = self.dev_su_id

        del game.players[player_id]
        if len(game.players) == 0:
            del self.games[ctx.channel.id]
            await ctx.send("Game removed!")
        else:
            await ctx.send(f"{ctx.author.name} has left the game!")

    @commands.command()
    async def hand(self, ctx):
        """Sends you a dm with your cards"""
        exists = await game_exists(ctx, self.games)
        if exists is False:
            return None
        player_id = ctx.author.id
        if self.dev_su_id is not None:
            player_id = self.dev_su_id

        game = self.games[ctx.channel.id]
        embed = embed_hand(action="As requested!",
                           player_id=player_id,
                           game=game)
        dm_channel = ctx.author.dm_channel
        if dm_channel is None:
            await ctx.author.create_dm()
            dm_channel = ctx.author.dm_channel

        await dm_channel.send(embed=embed)

    @commands.command()
    async def play(self, ctx, colour, value):
        """Lets you play a card in your hand"""
        exists = await game_exists(ctx, self.games)
        if exists is False:
            return None
        game = self.games[ctx.channel.id]

        player_id = ctx.author.id
        if self.dev_su_id is not None:
            player_id = self.dev_su_id

        if player_id != game.turn_order[game.turn]:
            await ctx.send("It's not your turn!")
            return None

        valid = await valid_card(player_id=player_id,
                                 colour=colour,
                                 value=value,
                                 game=game,
                                 ctx=ctx)
        if valid is False:
            return None

        matches = await card_matches(colour=colour,
                                     value=value,
                                     card=game.current_card,
                                     ctx=ctx)
        if matches is False:
            return None

        game.play(player_id, colour, value)

        won = await check_win(ctx=ctx, player_id=player_id, game=game)
        if won:
            del self.games[ctx.channel.id]
            return None

        if len(str(game.turn_order[game.turn])) == 18:
            member = get(ctx.guild.members, id=game.turn_order[game.turn])
            dm_channel = member.dm_channel
            if dm_channel is None:
                await member.create_dm()
                dm_channel = member.dm_channel
            embed = embed_hand(player_id=game.turn_order[game.turn],
                               action="It's your turn!",
                               game=game)
            await dm_channel.send(embed=embed)

        action = get_action_response(ctx.author.display_name, game)
        embed = embed_turn(action=action, game=game)
        await ctx.send(embed=embed)

    @commands.command()
    async def uno(self, ctx):
        """
        Let's everyone know you have uno
        / Calls out the first person who doesn't uno
        """
        exists = await game_exists(ctx, self.games)
        if exists is False:
            return None
        game = self.games[ctx.channel.id]

        player_id = ctx.author.id
        if self.dev_su_id is not None:
            player_id = self.dev_su_id

        player = game.players[player_id]

        if len(player.hand) == 1:
            await ctx.send(f"{player.player_name} has one card left!")
            player.uno = True
            return None
        callout = False
        for player_id, player in game.players.items():
            if len(player.hand) == 1 and player.uno is False:
                await ctx.send(f"{player.player_name} got called out!")
                for num in range(2):
                    card = game.deck.pop()
                    player.hand.append(card)
                callout = True
                break
        if callout is False:
            await ctx.send("You do not have uno and didn't call out anyone.")

    # Dev commands
    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx):
        """Reloads uno (dev only)"""
        self.bot.reload_extension("uno")
        await ctx.send("Uno has been reloaded")

    @commands.command()
    @commands.is_owner()
    async def addPlayer(self, ctx):
        """Adds a new player to the game (dev only)"""
        exists = await game_exists(ctx, self.games)
        if exists is False:
            return None
        game = self.games[ctx.channel.id]
        name = f"Test Player {len(game.players) + 1}"
        player_id = randint(1000, 9999)
        game.add_player(player_id=player_id, player_name=name)

        await ctx.send(f"Test player added with the id of {player_id}")

    @commands.command()
    @commands.is_owner()
    async def su(self, ctx, player_id: int):
        """Lets you execute commands as other players (dev only)"""
        exists = await game_exists(ctx, self.games)
        if exists is False:
            return None
        if player_id == ctx.author.id:
            self.dev_su_id = None
            await ctx.send("Su dev override disabled")
            return None
        self.dev_su_id = player_id
        await ctx.send(f"Su dev override active for {player_id}")

    @commands.command()
    @commands.is_owner()
    async def giveCard(self, ctx, colour, value: typing.Optional[str]):
        """Gives you a card of your choice"""
        exists = await game_exists(ctx, self.games)
        if exists is False:
            return None
        game = self.games[ctx.channel.id]

        player_id = ctx.author.id
        if self.dev_su_id is not None:
            player_id = self.dev_su_id

        player = game.players[player_id]
        if value is not None:
            player.hand.append((colour, value))
            await ctx.send(f"Gave card {colour} {value}")
        else:
            player.hand.append((colour, ))
            await ctx.send(f"Gave card {colour}")

    @commands.command()
    @commands.is_owner()
    async def removeCard(self, ctx, colour, value: typing.Optional[str]):
        """Removes a card from your hand (dev only)"""
        exists = await game_exists(ctx, self.games)
        if exists is False:
            return None
        game = self.games[ctx.channel.id]

        player_id = ctx.author.id
        if self.dev_su_id is not None:
            player_id = self.dev_su_id

        player = game.players[player_id]

        if value is None:
            player.hand.remove((colour, ))
            await ctx.send(f"Removed {colour}")
        else:
            player.hand.remove((colour, value))
            await ctx.send(f"Removed {colour} {value}")

    @commands.command()
    @commands.is_owner()
    async def removeCards(self, ctx, amount: int):
        """Removes a number of cards from your hand (dev only)"""
        exists = await game_exists(ctx, self.games)
        if exists is False:
            return None
        game = self.games[ctx.channel.id]

        player_id = ctx.author.id
        if self.dev_su_id is not None:
            player_id = self.dev_su_id

        player = game.players[player_id]

        for num in range(amount):
            player.hand.pop()

        await ctx.send(f"Removed {amount} card(s) from your hand")


def setup(bot):
    bot.add_cog(Uno(bot))
