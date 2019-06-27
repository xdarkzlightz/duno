from discord.ext import commands


def game_exists(games):
    async def predicate(ctx):
        if ctx.channel.id not in games.keys():
            await ctx.send("Oops! A game doesn't exist in your channel!" +
                           " You can create one with `;create`")
            return False
        else:
            return True

    return commands.check(predicate)


async def valid_card(player_id, colour, value, game, ctx):
    """Checks if the card is valid, and if the player has the card"""
    wilds = ["wild", "wild+4"]
    colours = ["red", "green", "blue", "yellow"]
    values = ["reverse", "skip", "+2"]

    wild = colour in wilds
    not_valid_value = value not in values and ((value not in colours) and wild)

    if not_valid_value is False:
        try:
            num = int(value)
            if num not in range(0, 10):
                not_valid_value = True
        except ValueError:
            not_valid_value = False

    if colour not in colours and wild is False:
        await ctx.send(f"Invalid colour! You said {colour}")
    elif not_valid_value:
        await ctx.send(f"Invalid value! You said {value}")

    player = game.players[player_id]

    if wild and (colour, ) not in player.hand:
        await ctx.send("Sorry but you don't have that card!")
    if wild is False and (colour, value) not in player.hand:
        await ctx.send("Sorry but you don't have that card!")


async def card_matches(colour, value, card, ctx):
    wilds = ["wild", "wild+4"]
    matches = False
    if colour in wilds:
        matches = True
    elif colour == card[0] or value == card[1]:
        matches = True

    if matches is False:
        await ctx.send("Your card doesn't match!")
