"""
This script returns all the matches played by a user in a display format
"""
from models import Match

def get_my_matches(user=None):
    """
    Get's a users matches
    """
    if user is None:
        return None

    # Querying for all matches that the user has played
    user_matches = Match.select().where(
        (Match.player1_id == user.get_id()) |
        (Match.player2_id == user.get_id())
    )
    # Return is a list of strings
    outcomes = []
    # Iterating over all the matches where the user played
    for match in user_matches:
        outcomes.append(
            "{} vs {} ({}-{})".format(match.player1.username, match.player2.username,
                                      match.player1_goals, match.player2_goals)
        )

    return outcomes
