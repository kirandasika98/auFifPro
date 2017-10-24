from models import *
from peewee import *

"""
Check database if user is first or second player
Check if user lost
Generate appropriate string and add it to the array
return array
"""

def match_result(g1, g2, is_player1=False, is_player2=False):
    """
    Returns True or False based on whether the player won or lost the match.
    """
    pass


def get_my_matches(user=None):
    if user is None:
        return None

    outcome_strings = []
    for match in Match.select():
        is_player1 = False
        is_player2 = False

        # Checking if user is player1 or player2
        if match.player1.get_id() == user.get_id():
            is_player1 = True
        else:
            is_player2 = True

        result = match_result(match.player1_goals, match.player2_goals,
                                is_player1=is_player1, is_player2=is_player2)

        outcome_string = None
        if result:
            if is_player1:
                outcome_string = "vs {} WON ({}-{})".format(match.player2.username,
                                                    match.player1_goals,
                                                    match.player2_goals)
            if is_player2:
                outcome_string = "vs {} WON ({}-{})".format(match.player1.username,
                                                    match.player1_goals,
                                                    match.player2_goals)
        else:
            if is_player1:
                outcome_string = "vs {} LOST ({}-{})".format(match.player2.username,
                                                    match.player1_goals,
                                                    match.player2_goals)
            if is_player2:
                outcome_string = "vs {} LOST ({}-{})".format(match.player2.username,
                                                    match.player1_goals,
                                                    match.player2_goals)

        outcome_strings.append(outcome_string)

    return outcome_strings
