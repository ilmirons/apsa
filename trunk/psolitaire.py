'''

@author: andrea
'''

import sys
import time
from board import Board, LEFT, RIGHT, UP, DOWN, ENGLISH, Move
from aima.search import Problem, best_first_graph_search


COSTS = {}

def print_sol(node):
    """
    Print the solution.
    """
    if node is None:
        print >> sys.stderr, "\nNO SOLUTION FOUND!!"
        return False
    else:
        solution = node.path()
        while solution:
            node = solution.pop()
            print node.action
            print node.state
            print "classes count:", \
            [
             len(pos_class) 
             for pos_class in 
             [ [c for c in cls if c.peg]
                for cls in node.state.clses
                ]
             ], "\n\n"
    return True

def fitness(node):
    """
    Evaluate how good a state is
    (the lower the function the better the state)
    Returns the sum of costs defined in COSTS for 
    each full multiplied by difference between classes.
    """
    try:
        brd = node.state
    except AttributeError:
        brd = node
    cost = 0
    for cell in [c for c in brd.full]:
        cost += COSTS[cell.coords]
    cost += class_cost(brd) * cost
    return cost

def class_cost(brd):
    """
    Return the difference 
    between equivalent group of 
    classes
    """
    return abs(len([c for c in brd.clses[0] if c.peg]) + \
               len([c for c in brd.clses[3] if c.peg]) -\
                (len([c for c in brd.clses[1] if c.peg]) + \
                 len([c for c in brd.clses[2] if c.peg])))

def init_costs(brd):
    """
    Assign a cost to each cell
    according to how many places 
    it can move to.
    """
    for cell in brd.compact:
        COSTS[cell.coords] = 1
        for cell2 in [cell.uup, cell.ddown, cell.lleft, cell.rright]:
            if cell2 is None:
                COSTS[cell.coords] += 1
    


class CentralSolitaireProblem(object, Problem):
    """
    The complement central 
    problem on an English board. 
    """
    def __init__(self):
        brd1 = Board(ENGLISH)
        brd1[3][3].pick()
        brd2 = brd1.copy()
        brd2.complement()
        init_costs(brd1)
        Problem.__init__(self, brd1, brd2)
        self.initial.set_observed_class(self.goal[3][3])
        self.initial[3][3].pvalue = \
        self.goal[3][3].pvalue = len(self.goal.clses) + 1
        self.generated = 0
        

    
    def successor(self, brd): #IGNORE:R0912
        """
        Generate the successors of state brd
        brd -- state of the problem
        """
        moves = []
        if not len([sc for sc in brd.obs if sc.peg]) == 0:
            # and reachable(brd[3][3], len(brd.full), []):
            
            empty_start = len(brd.empty) < len(brd.full)
            
            if brd.chk_vert_sym():
                if brd.chk_hor_sym():
                    search_area = brd.__iter__((0, int(round(brd.width/2))), \
                                               int(round(brd.height/2) + 1), \
                                               int(round(brd.height/2) + 1))
                else:
                    search_area = brd.__iter__((0, 0), brd.width, \
                                               int(round(brd.height/2) + 1))
            elif brd.chk_hor_sym():
                search_area = brd.__iter__((0, int(round(brd.width/2))), \
                                           int(round(brd.width/2) + 1), brd.height)
            else:
                search_area = brd.compact
                
            for n in search_area:
                if empty_start and n != None and not n.peg:
                    if (n.lleft != None) and n.left.peg and n.lleft.peg:
                        m = Move(n.lleft.coords, RIGHT)
                        moves.append((m, m(brd)))
                        self.generated += 1
                    if (n.rright is not None) and n.right.peg and n.rright.peg:
                        m = Move(n.rright.coords, LEFT)
                        moves.append((m, m(brd)))
                        self.generated += 1
                    if (n.uup is not None) and n.up.peg and n.uup.peg:
                        m = Move(n.uup.coords, DOWN)
                        moves.append((m, m(brd)))
                        self.generated += 1
                    if (n.ddown is not None) and n.down.peg and n.ddown.peg:
                        m = Move(n.ddown.coords, UP)
                        moves.append((m, m(brd)))
                        self.generated += 1
                elif not empty_start and n != None and n.peg:
                    if (n.lleft != None) and n.left.peg and not n.lleft.peg:
                        m = Move(n.coords, LEFT)
                        moves.append((m, m(brd)))
                        self.generated += 1
                    if (n.rright is not None) and n.right.peg and not n.rright.peg:
                        m = Move(n.coords, RIGHT)
                        moves.append((m, m(brd)))
                        self.generated += 1
                    if (n.uup is not None) and n.up.peg and not n.uup.peg:
                        m = Move(n.coords, UP)
                        moves.append((m, m(brd)))
                        self.generated += 1
                    if (n.ddown is not None) and n.down.peg and not n.ddown.peg:
                        m = Move(n.coords, DOWN)
                        moves.append((m, m(brd)))
                        self.generated += 1
            if moves != []:
                print str(brd)
                print "fitness:", str(fitness(brd))
        return moves

if __name__ == '__main__':
    
    P = CentralSolitaireProblem()
    T0 = time.clock()
    SOL = best_first_graph_search(P, fitness)
    T = time.clock() - T0
    print_sol(SOL)
    
    print "solution found in", str(T) + "s"
    print P.generated, "nodes generated"
    
    