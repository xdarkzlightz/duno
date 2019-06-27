class Player:
    """Represents a player"""

    def __init__(self, player_id, player_name):
        self.player_id = player_id
        self.player_name = player_name
        self.hand = []
        self.uno = False
