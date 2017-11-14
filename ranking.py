"""
Get wins and draws for each player
Calculate goal difference while calculating wins
Sort users based on wins and GD
"""
from collections import OrderedDict
from models import Match

class RankUser(object):
    """
    Placeholder class to represent a user.
    """
    def __init__(self, uid, username):
        self.id = uid
        self.username = username
        self.wins = 0
        self.draws = 0
        self.GD = 0
        self.points = 0
        self.matches_played = 0

    def add_win(self):
        """
        Add win for user
        """
        self.wins += 1
        self.points += 3

    def add_draw(self):
        """
        Add draw for user
        """
        self.draws += 1
        self.points += 1

    def calculate_gd(self, goals_for, goals_against):
        """
        Calculate GD for user
        """
        self.GD += (goals_for - goals_against)

    def add_match(self):
        """
        Increment match count for user
        """
        self.matches_played += 1

    def __str__(self):
        return """id:{}, username:{}, wins:{}, draws:{}, GD:{}, points:{},
                mp:{}""".format(self.id, self.username, self.wins,
                                self.draws, self.GD, self.points,
                                self.matches_played)


def calculate_ranks():
    """
    calculates the ranks for user based on matches played, gd and points
    """
    user_map = dict()
    for match in Match.select():
        # search player 1
        try:
            player1 = user_map[match.player1.get_id()]
        except KeyError:
            player1 = RankUser(match.player1.get_id(), match.player1.username)

        # search player 2
        try:
            player2 = user_map[match.player2.get_id()]
        except KeyError:
            player2 = RankUser(match.player2.get_id(), match.player2.username)

        # calculating draws and wins
        if match.player1_goals == match.player2_goals:
            # add a point for both players
            player1.add_draw()
            player2.add_draw()
        elif match.player1_goals > match.player2_goals:
            player1.add_win()
        else:
            player2.add_win()

        # calculate GD's for both players
        player1.calculate_gd(match.player1_goals, match.player2_goals)
        player2.calculate_gd(match.player2_goals, match.player1_goals)

        # adding a match for both players
        player1.add_match()
        player2.add_match()

        # adding users back to the player user_map
        user_map[player1.id] = player1
        user_map[player2.id] = player2

    return OrderedDict(sorted(user_map.items(), key=lambda t: (t[1].points, t[1].matches_played),
                              reverse=True))
