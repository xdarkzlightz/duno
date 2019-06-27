from discord import Embed

hex_colours = {
    "red": 0xe80909,
    "green": 0x54e50b,
    "blue": 0x020dea,
    "yellow": 0xe2ea02
}


def embed_turn(action, game):
    """Embed helper for the turn event"""

    players = []
    for player_id, player in game.players.items():
        players.append(player.player_name)

    current_player = game.players[game.turn_order[game.turn]]

    embed = Embed(colour=hex_colours[game.current_card[0]], title=action)

    embed.add_field(name="Players", value="\n".join(players))
    embed.add_field(name="Current Card",
                    value=f"{game.current_card[0]} {game.current_card[1]}")
    embed.set_footer(text=f"It's {current_player.player_name}'s turn |" +
                     f" Drawpile: {len(game.deck)}")
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

    embed = Embed(colour=hex_colours[game.current_card[0]], title=action)
    embed.add_field(name="Cards", value=", ".join(hand))
    embed.set_footer(text=f"Total cards: {len(hand)}")
    return embed
