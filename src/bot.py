"""
    Author: xdarkzlightz#4975
    Version: v1.0.0
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


bot.load_extension("uno")

token = os.getenv("TOKEN")
bot.run(token)
