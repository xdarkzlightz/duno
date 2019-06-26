"""
    Author: xdarkzlightz#4975
    Version: v0.0.0

    TODO: Setup initial game

    Commands:
        dev commands:
            reload - reloads bots uno cog
            sudo - Lets you play as other players
            addUser - Lets you add players in the game

        normal commands:
            play - plays a card
            join - joins a game
            create - creates a game
            draw - draw a card
            kick - kick a player from the game
            quit - quits the game
"""

import os
from os.path import join

from discord.ext import commands
from dotenv import load_dotenv

dotenv_path = join(os.getcwd(), ".env")
load_dotenv(dotenv_path)

bot = commands.Bot(command_prefix=";")


@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")


token = os.getenv("TOKEN")
bot.run(token)
