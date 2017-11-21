# This script will generate new matches for users based on graphs edges
from collection import defaultdict
from models import User
from app import MC

class Node(object):
    """
    Simple node to represent a vertex in a graph
    """

    def __init__(self, data=None):
        # Id for a vertex in a graph
        self.data = data
        # list of all adjacent vertex in a graph
        self.adjacent = list()

    def add_addjacent(self, data):
        newNode = Node(data)
        self.adjacent.append(newNode)

    def edge_weight(self, targetVertex):
        """
        Calculates edge weight between self and target vertex
        """
        pass

class WeightedGraph(object):

    def __init__(self):
        self.graph = defaultdict()
        self.vertices = 0
        self.edges = 0

    def add_connection(self, rootVertex, targetVertex):
        if rootVertex is None and targetVertex is None:
            return False

        # Get all users from the database and build a graph
        # Update connections based on users played
        # Check if memcache ranks key exists
        if MC.get("ranks") is not None:
            # Generate matches based on ranks
        else:
            # Get users from database to create ranks
            users = User.select()
        return True
