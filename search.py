"""
Search (Chapters 3-4)

The way to use this code is to subclass Problem to create a class of problems,
then create problem instances and solve them with calls to the various search
functions.
"""

import sys
import math
from collections import deque

from utils import *
from agents import *


"""
1- BFS: Breadth first search. Using tree or graph version, whichever makes more sense for the problem
2- DFS: Depth-First search. Again using tree or graph version.
3- UCS: Uniform-Cost-Search. Using the following cost function to optimise the path, from initial to current state.
4- Greedy: Uses Manhattan distance to the next closest dirty room as heuristic for greedy algorithm. To find the next closest dirty room, use Manhattan distance.
5- A*:  Using A star search.
"""
searchTypes = ['None', 'Reflex', 'BFS', 'DFS', 'UCS', 'Greedy', 'A*']
"""
Cost function used for UCS and A* search. 
-'Step' counts the numbers of steps from start
-'StepTurn' adds number of turns to Step cost
-'StayLeft' favors staying on the left side of the map
-'StayUp' favors staying on the top side of the map
"""
costFunctions = ['Step', 'StepTurn', 'StayLeft', 'StayUp']
heuristics = ['Manhattan', 'Euclid']

class Problem:
    """The abstract class for a formal problem. You should subclass
    this and implement the methods actions and result, and possibly
    __init__, goal_test, and path_cost. Then you will create instances
    of your subclass and solve them with the various search functions."""

    def __init__(self, initial, goal=None):
        """The constructor specifies the initial state, and possibly a goal
        state, if there is a unique goal. Your subclass's constructor can add
        other arguments."""
        self.initial = initial
        self.goal = goal

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a list, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        raise NotImplementedError

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        raise NotImplementedError

    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal or checks for state in self.goal if it is a
        list, as specified in the constructor. Override this method if
        checking against a single self.goal is not enough."""
        if isinstance(self.goal, list):
            return is_in(state, self.goal)
        else:
            return state == self.goal

    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2. If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""
        return c + 1

    def value(self, state):
        """For optimization problems, each state has a value. Hill Climbing
        and related algorithms try to maximize this value."""
        raise NotImplementedError


# ______________________________________________________________________________


class Node:
    """A node in a search tree. Contains a pointer to the parent (the node
    that this is a successor of) and to the actual state for this node. Note
    that if a state is arrived at by two paths, then there are two nodes with
    the same state. Also includes the action that got us to this state, and
    the total path_cost (also known as g) to reach the node. Other functions
    may add an f and h value; see best_first_graph_search and astar_search for
    an explanation of how the f and h values are handled. You will not need to
    subclass this class."""

    def __init__(self, state, parent=None, action=None, path_cost=0):
        """Create a search tree Node, derived from a parent by an action."""
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1

    def __repr__(self):
        return "<Node {}>".format(self.state)

    def __lt__(self, node):
        return self.state < node.state

    def expand(self, problem):
        """List the nodes reachable in one step from this node."""
        return [self.child_node(problem, action)
                for action in problem.actions(self.state)]

    def child_node(self, problem, action):
        """[Figure 3.10]"""
        next_state = problem.result(self.state, action)
        pathCost = problem.path_cost(self, self.state, action, next_state)
        next_node = Node(next_state, self, action, pathCost)
        return next_node

    def solution(self):
        """Return the sequence of actions to go from the root to this node."""
        return [node.action for node in self.path()[1:]]


    def path(self):
        """Return a list of nodes forming the path from the root to this node."""
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    # We want for a queue of nodes in breadth_first_graph_search or
    # astar_search to have no duplicated states, so we treat nodes
    # with the same state as equal. [Problem: this may not be what you
    # want in other contexts.]

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        # We use the hash value of the state
        # stored in the node instead of the node
        # object itself to quickly search a node
        # with the same state in a Hash Table
        return hash(self.state)



class VacuumPlanning(Problem):
    """ The problem of find the next room to clean in a grid of m x n rooms.
    A state is represented by state of the grid cells locations. Each room is specified by index set
    (i, j), i in range(m) and j in range (n). Final goal is to clean all dirty rooms. We go by performing sub-goals, each being cleaning the "next" dirty room.
    """

    def __init__(self, env, searchtype):
        """ Define goal state and initialize a problem
            initial is a pair (i, j) of where the agent is
            goal is next pair(k, l) where map[k][l] is dirty
        """
        self.solution = None
        self.env = env
        self.state = env.agent.location
        super().__init__(self.state)
        self.map = env.things
        self.searchType = searchtype
        env.agent.direction = 'UP'  # initial direction of the agent.
        self.agent = env.agent

    def generateSolution(self):
        """ generate full path and explored nodes from current node to the next goal node based on type of the search chosen"""
        if self.searchType == 'None':
            print("generateSolution: searchType not set or running not clicked!")
            return

        self.env.read_env()
        self.state = self.env.agent.location
        super().__init__(self.state)

        if self.searchType == 'BFS':
            path, explored = breadth_first_graph_search(self)
        elif self.searchType == 'DFS':
            path, explored = depth_first_graph_search(self)
        elif self.searchType == 'UCS':
            path, explored = uniform_cost_search(self)
        elif self.searchType == 'Greedy':
            path, explored = best_first_graph_search(self, None)
        elif self.searchType == 'A*':
            path, explored = astar_search(self, None)
        elif self.searchType == 'Reflex':
            path, explored = reflexAgentSearch(self)
        else:
            raise 'NameError'

        if (path != None):
            self.env.set_solution(path)
        else:
            print("There is no solution!\n")

        if (explored != None):
            self.env.display_explored(explored)
            self.env.exploredCount += len(explored)
            self.env.pathCount += len(self.env.path)
            self.env.ExploredCount_label.config(text=str(self.env.exploredCount))
            self.env.PathCount_label.config(text=str(self.env.pathCount))
        else:
            print("There is not explored list!\n")

    def generateNextSolution(self):
        self.generateSolution()

    def actions(self, state):
        """ Return the actions that can be executed in the given state.
        The result would be a list, since there are only four possible actions
        in any given state of the environment """

        possible_neighbors = self.env.things_near(state)
        possible_actions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
        for slot in possible_neighbors:
            if isinstance(slot[0], Wall):
                x, y = slot[0].location
                if x == state[0] and y == state[1] + 1:
                    possible_actions.remove('UP')
                if x == state[0] and y == state[1] - 1:
                    possible_actions.remove('DOWN')
                if x == state[0] + 1 and y == state[1]:
                    possible_actions.remove('RIGHT')
                if x == state[0] - 1 and y == state[1]:
                    possible_actions.remove('LEFT')

        return possible_actions

    def result(self, state, action):
        """ Given state and action, return a new state that is the result of the action.
        Action is assumed to be a valid action for the state """
        self.agent.direction = action
        new_state = list(state)
        if action == 'RIGHT':
            new_state[0] += 1
        elif action == 'LEFT':
            new_state[0] -= 1
        elif action == 'UP':
            new_state[1] += 1
        elif action == 'DOWN':
            new_state[1] -= 1

        return new_state

    def goal_test(self, state):
        """ Given a state, return True if state is a goal state or False, otherwise """
        return self.env.some_things_at(state, Dirt)

    def path_cost(self, curNode, state1, action, state2):
        """computes accumulated path cost so far to state2. Returns the cost of a solution path that arrives at state2 from
        state1 via action, assuming it costs c to get up to state1. For our problem state is (x, y) coordinate pair.
        Rotation of the agent costs 3 times of basic cost unit for each 90' rotation plus the basic cost. """
        # print("path_cost: to be done by students")
        cost = curNode.path_cost

        if self.env.costFunc == costFunctions[0]:  # Basic stepCount cost
            cost = cost + 1
        elif self.env.costFunc == costFunctions[1]:  # stepCount plus turn cost
            # Get current direction from parent node if exists
            cur_direction = 'UP'  # Default direction
            if curNode.parent:
                cur_direction = curNode.action
            turn_cost = self.computeTurnCost(cur_direction, action)
            cost = cost + 1 + turn_cost
        elif self.env.costFunc == costFunctions[2]:  # StayLeft
            # Higher cost for right half of grid
            midpoint = self.env.width // 2
            if state2[0] >= midpoint:
                cost = cost + 5  # Higher cost for right side
            else:
                cost = cost + 1  # Lower cost for left side
        else:  # StayUp - costFunctions[3]
            # Higher cost for bottom half of grid
            midpoint = self.env.height // 2
            if state2[1] < midpoint:
                cost = cost + 5  # Higher cost for bottom half
            else:
                cost = cost + 1  # Lower cost for top half

        return cost

    def computeTurnCost(self, action1, action):
        """computes turn cost as the number of 90' rotations away from current direction given by action1"""
        directions = ['UP', 'RIGHT', 'DOWN', 'LEFT']
        i1 = directions.index(action1)
        i2 = directions.index(action)
        turn_diff = abs(i1 - i2)
        if turn_diff == 3:  # Going from LEFT to UP or vice versa is just one turn
            turn_diff = 1
        return turn_diff * 3  # Each 90° turn costs 3

    def findMinManhattanDist(self, pos):
        """Find a dirty room among all dirty rooms which has minimum Manhattan distance to pos
        hint: use distance_manhattan() function in utils.py"""
        min_dist = float('inf')
        for x in range(self.env.width):
            for y in range(self.env.height):
                if self.env.some_things_at((x, y), Dirt):
                    dist = abs(pos[0] - x) + abs(pos[1] - y)
                    min_dist = min(min_dist, dist)
        return min_dist

    def findMinEuclidDist(self, pos):
        """Find a dirty room among all dirty rooms which has minimum Manhattan distance to pos
                hint: use distance_manhattan() function in utils.py"""
        min_dist = float('inf')
        for x in range(self.env.width):
            for y in range(self.env.height):
                if self.env.some_things_at((x, y), Dirt):
                    dist = math.sqrt((pos[0] - x)**2 + (pos[1] - y)**2)
                    min_dist = min(min_dist, dist)
        return min_dist

    def h(self, node):
        """ Return the heuristic value for a given state. For this problem use minimum Manhattan or Euclid
        distance to a dirty room, among all the dirty rooms.
        """
        if self.env.args['heuristic'] == 'Manhattan':
            heur = self.findMinManhattanDist(node.state)
        else:  ## means Euclid distance
            heur = self.findMinEuclidDist(node.state)

        return heur

# ______________________________________________________________________________


# ______________________________________________________________________________
# Uninformed Search algorithms

def breadth_first_graph_search(problem):
    """[Figure 3.11]
    Note that this function can be implemented in a
    single line as below:
    return graph_search(problem, FIFOQueue())
    """
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return node, [node.state]

    frontier = deque([node])
    explored = set()
    explored_states = [list(node.state)]  # For visualization

    while frontier:
        node = frontier.popleft()
        state_tuple = tuple(node.state)
        explored.add(state_tuple)

        for child in node.expand(problem):
            child_tuple = tuple(child.state)
            if child_tuple not in explored and not any(tuple(n.state) == child_tuple for n in frontier):
                explored_states.append(list(child.state))
                if problem.goal_test(child.state):
                    return child, explored_states
                frontier.append(child)

    # If no solution is found
    return None, explored_states


def depth_first_graph_search(problem):
    """
    [Figure 3.7]
    Search the deepest nodes in the search tree first.
    Search through the successors of a problem to find a goal.
    The argument frontier should be an empty queue.
    Does not get trapped by loops.
    If two paths reach a state, only use the first one.
    """
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return node, [node.state]

    frontier = [node]
    explored = set()
    explored_states = [list(node.state)]  # For visualization

    while frontier:
        node = frontier.pop()
        state_tuple = tuple(node.state)

        if state_tuple not in explored:
            explored.add(state_tuple)
            explored_states.append(list(node.state))

            if problem.goal_test(node.state):
                return node, explored_states

            successors = node.expand(problem)
            for child in reversed(successors):  # Reverse to maintain correct DFS order
                child_tuple = tuple(child.state)
                if child_tuple not in explored and not any(tuple(n.state) == child_tuple for n in frontier):
                    frontier.append(child)

    # If no solution is found
    return None, explored_states

def best_first_graph_search(problem, f=None):
    """Search the nodes with the lowest f scores first.
    You specify the function f(node) that you want to minimize; for example,
    if f is a heuristic estimate to the goal, then we have greedy best
    first search; if f is node's depth then we have breadth-first search.
    There is a subtlety: the line "f = memoize(f, 'f')" means that the f
    values will be cached on the nodes as they are computed. So after doing
    a best first search you can examine the f values of the path returned.
    For f=None, the problem's h function (default heuristic function) is used"""
    f = memoize(f or problem.h, 'f')
    node = Node(problem.initial)

    if problem.goal_test(node.state):
        return node, [node.state]

    frontier = PriorityQueue('min', f)
    frontier_nodes = {tuple(node.state): node}  # Keep track of nodes in frontier
    frontier.append(node)
    explored = set()
    explored_states = [list(node.state)]

    while frontier:
        node = frontier.pop()
        state_tuple = tuple(node.state)
        frontier_nodes.pop(state_tuple, None)  # Remove from tracking

        if problem.goal_test(node.state):
            return node, explored_states

        if state_tuple not in explored:
            explored.add(state_tuple)
            explored_states.append(list(node.state))

            for child in node.expand(problem):
                child_tuple = tuple(child.state)
                if child_tuple not in explored and child_tuple not in frontier_nodes:
                    frontier.append(child)
                    frontier_nodes[child_tuple] = child
                elif child_tuple in frontier_nodes:
                    existing_node = frontier_nodes[child_tuple]
                    if f(child) < f(existing_node):
                        # Replace the existing node
                        del frontier_nodes[child_tuple]
                        frontier.append(child)
                        frontier_nodes[child_tuple] = child

    # If no solution is found
    return None, explored_states


def reflexAgentSearch(problem):
    """returns a path to next cell neighboring current location based on a typical reflex agent.
    A reflex agent senses the immediate neighboring cells and it finds a dirty one, move there, otherwise
    move randomly to one of the available left, right, and forward cells."""
    node = Node(problem.state)
    neighbors = node.expand(problem)
    for neigh in neighbors:
        if(problem.goal_test(neigh.state)):
            return neigh, None
    randPic = random.choice(neighbors)
    return randPic, None


def uniform_cost_search(problem):
    """[Figure 3.14]"""
    return best_first_graph_search(problem, lambda node: node.path_cost)


# ______________________________________________________________________________
# Informed (Heuristic) Search


greedy_best_first_graph_search = best_first_graph_search


# Greedy best-first search is accomplished by specifying f(n) = h(n).


def astar_search(problem, h=None):
    """A* search is best-first graph search with f(n) = g(n)+h(n).
    You need to specify the h function when you call astar_search, or
    else in your Problem subclass."""
    h = memoize(h or problem.h, 'h')
    return best_first_graph_search(problem, lambda n: n.path_cost + h(n))

# ______________________________________________________________________________
# ______________________________________________________________________________

