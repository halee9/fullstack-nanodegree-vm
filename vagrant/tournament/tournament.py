#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM matches")
    conn.commit()
    conn.close()

def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM players")
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT count(*) FROM players")
    row = c.fetchone()
    conn.close()
    return row[0]

def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO players (name) VALUES (%s);", (name,))
    conn.commit()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id, name, wins, matches FROM records ORDER BY wins DESC, id ASC")
    standings = [(row[0], row[1], row[2],row[3])
             for row in c.fetchall()]
    conn.close()
    return standings


def reportMatch(winner, loser, draw):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
      draw: boolean true if the match was tied, false if not defined
    """
    conn = connect()
    c = conn.cursor()
    # insert a match row into matches table
    c.execute("INSERT INTO matches (winner, loser, draw) VALUES (%s, %s, %s)", (winner, loser, draw))
    conn.commit()
    conn.close()

def isValidMatch(firstPlayer, secondPlayer):
    """ Check if two players matched before
    Arg:
        firstPlayer: the id number of the firstPlayer
        secondPlayer: the id number od the secondPlayer
    Return:
        True or False
    """
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id FROM matches WHERE (winner = %s AND loser = %s) OR (loser = %s AND winner = %s)",
              (firstPlayer, secondPlayer, firstPlayer, secondPlayer))
    rows = c.fetchall()
    if len(rows) > 0:
        return False
    else:
        return True

def findOpponent(standings, opponentIndex):
    """ Find opponent player with recursive
    Arg:
        standings: the list of the possible candidates
        opponentIndex: index of list for opponent player
    Return:
        index of opponent
    """
    # if there is no possible candidate, return original player index
    if opponentIndex >= len(standings):
        return 1
    # if valid match, return the index
    elif isValidMatch(standings[0][0], standings[opponentIndex][0]):
        return opponentIndex
    # if not valid match, add 1 to opponent index and recursion
    else:
        return findOpponent(standings, opponentIndex+1)

def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings()
    #validatePrePairs(standings)

    # if ranking number is even, make a pair tuple
    pairs = []

    # create valid pairs with pops until list 'standing' will be empty
    while len(standings) > 1:
        # get opponent index
        opponent = findOpponent(standings, 1)
        # pop and remove first element from list 'standings'
        firstPlayer = standings.pop(0)
        # pop and remove opponent index element from list 'standings'
        secondPlayer = standings.pop(opponent-1)
        # create pair
        pairs.append((firstPlayer[0], firstPlayer[1], secondPlayer[0], secondPlayer[1]))

    return pairs

