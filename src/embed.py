from discord import Embed

from cards import blue, green, red, wild, wild_plus_four, yellow

hex_colours = {
    "red": 0xe80909,
    "green": 0x54e50b,
    "blue": 0x020dea,
    "yellow": 0xe2ea02
}


def get_assets(game):
    """Gets the embed colour and thumbnail"""
    colour = None
    thumbnail = None
    wilds = ["wild", "wild+4"]
    if game.current_card[0] in wilds:
        colour = hex_colours[game.current_card[1]]
        thumbnail = wild if game.current_card[0] == "wild" else wild_plus_four
    else:
        colour = hex_colours[game.current_card[0]]
        if game.current_card[0] == "red":
            thumbnail = red[game.current_card[1]]
        elif game.current_card[0] == "green":
            thumbnail = green[game.current_card[1]]
        elif game.current_card[0] == "blue":
            thumbnail = blue[game.current_card[1]]
        elif game.current_card[0] == "yellow":
            thumbnail = yellow[game.current_card[1]]

    return {"colour": colour, "thumbnail": thumbnail}


def embed_turn(action, game):
    """Embed helper for the turn event"""
    assets = get_assets(game)

    players = []
    for player_id in game.turn_order:
        player = game.players[player_id]
        playing = ""
        if player_id == game.turn_order[game.turn]:
            playing = "👑"

        players.append(f"{player.player_name} ({len(player.hand)}) {playing}")

    current_player = game.players[game.turn_order[game.turn]]

    embed = Embed(colour=assets["colour"], title=action)

    embed.add_field(name="Players", value="\n".join(players))
    embed.add_field(name="Current Card",
                    value=f"{game.current_card[0]} {game.current_card[1]}")
    embed.set_footer(text=f"It's {current_player.player_name}'s turn")
    embed.set_thumbnail(url=assets["thumbnail"])

    return embed


def embed_hand(action, player_id, game):
    """Embed helper for embedding a players hand"""
    player = game.players[int(player_id)]
    hand = []

    for card in player.hand:
        val = ""
        if len(card) == 2:
            val = card[1]
        hand.append(f"{card[0]} {val}")
    hand.sort()

    assets = get_assets(game)

    embed = Embed(colour=assets["colour"], title=action)
    embed.add_field(name="Cards", value=", ".join(hand))
    embed.set_footer(
        text=f"Total cards: {len(hand)} | " +
        f"Current card is a {game.current_card[0]} {game.current_card[1]}")

    embed.set_thumbnail(url=assets["thumbnail"])
    return embed
