from random import randint

from discord import Embed
from discord.ext import commands

from game import Game


def game_exists(games):
    async def predicate(ctx):
        if ctx.channel.id not in games.keys():
            await ctx.send("Oops! A game doesn't exist in your channel!" +
                           " You can create one with `;create`")
            return False
        else:
            return True

    return commands.check(predicate)


class Uno(commands.Cog):
    games = {}

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def reload(self, ctx):
        """Reloads uno, dev only"""
        self.bot.reload_extension("uno")
        await ctx.send("Uno has been reloaded")

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
    @game_exists(games)
    async def join(self, ctx):
        """Joins a game"""
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
    @game_exists(games)
    async def players(self, ctx):
        """Shows all the players in the game"""
        game = self.games[ctx.channel.id]

        players = []
        for player_id, player in game.players.items():
            players.append(player.player_name)

        embed = Embed(colour=0x0fb0d8)
        embed.add_field(name="Players", value="\n".join(players))
        embed.set_footer(text=f"Total: {len(players)}")

        await ctx.send(embed=embed)

    @commands.command()
    @game_exists(games)
    async def start(self, ctx):
        """Starts the game"""
        game = self.games[ctx.channel.id]
        game.start()

    @commands.command()
    @game_exists(games)
    async def addPlayer(self, ctx):
        """Adds a new player to the game (dev only)"""
        game = self.games[ctx.channel.id]
        name = f"Test Player {len(game.players) + 1}"
        player_id = randint(1000, 9999)
        game.add_player(player_id=player_id, player_name=name)

        await ctx.send(f"Test player added with the id of {player_id}")

    @commands.command()
    @game_exists(games)
    async def su(self, ctx, player_id):
        """Lets you execute commands as other players (dev only)"""


def setup(bot):
    bot.add_cog(Uno(bot))
