# -*- coding: utf-8 -*-
'''

@author: andrea
'''

import sys
import time
from board import Board, LEFT, RIGHT, UP, DOWN, ENGLISH, REVERSEPROBLEM, Move
from aima.search import Node, Problem, depth_first_tree_search
from aima.utils import FIFOQueue
from tile import TILES


original_hashed_fringe = {}
reverse_hashed_fringe = {}


def print_sol(node, out = sys.stdout):
    if node is None:
        print >> sys.stderr, "\nNO SOLUTION FOUND!!"
        return False
    elif not isinstance(node, list):
        solution = node.path()
    else:
        solution = node
    cnt = 0
    for node in solution:
        cnt += 1
        print >> out, node.state
    print "Solution was achieved in " + str(cnt) + " step"
    return True
    

class BoardProblem(object, Problem):
    """
    Solve a board by tiling.
    """     
    
    def __init__(self, initial, goal):
        Problem.__init__(self, initial, goal)
        self.generated = 0
        
        
    def successor(self, brd):
        emptyStart = len(brd.empty) < len(brd.full)
        
        if brd.chk_vert_sym():
            if brd.chk_hor_sym():
                searchArea = brd.__iter__((0, int(round(brd.width/2))),\
                                           int(round(brd.height/2) + 1), int(round(brd.height/2) + 1))
            else:
                searchArea = brd.__iter__((0, 0), brd.width, int(round(brd.height/2) + 1))
        elif brd.chk_hor_sym():
            searchArea = brd.__iter__((0, int(round(brd.width/2))),\
                                       int(round(brd.width/2) + 1), brd.height)
        else:
            searchArea = brd.__iter__()
        
        if emptyStart:
            candidates = [cell for cell in searchArea if cell is not None and not cell.peg]
        else: 
            candidates = [cell for cell in searchArea if cell is not None and cell.peg]
        
        def _check_board_consistency(brd2):
            for b, g in zip(brd2.compact, self.goal.compact):
                if (not b.peg) and g.peg:
                    return False
            return True 
        
        ret = []
        if _check_board_consistency(brd):
            for tile in TILES:
                if len(tile.full) - 1 < len(brd.full):
                    for cell in candidates:
                        tmptile = tile.copy()
                        newBoard = tmptile.apply(cell.coords, brd, emptyStart)
                        if newBoard != False:
                            if __debug__:
                                print "applied \n" + str(tmptile) + "on\n" + str(brd)\
                                + "with " + str(tmptile.boardStart) + " <t=b> " + str(cell.coords)
                                print newBoard
                            ret.append((tmptile, newBoard))
                            self.generated += 1
        return ret
        
class ReverseBoardProblem(Problem):
    
    def __init__(self, initial, goal):
        Problem.__init__(self, initial, goal)
        self.generated = 0
        
        
        
    def successor(self, brd):
        emptyStart = len(brd.empty) < len(brd.full)
        
        #TODO capire inversione searcharea su reverse problem
        
        if brd.chk_vert_sym():
            if brd.chk_hor_sym():
                searchArea = brd.__iter__((0, int(round(brd.width/2))), int(round(brd.height/2) + 1), int(round(brd.height/2) + 1))
            else:
                searchArea = brd.__iter__((0, 0), brd.width, int(round(brd.height/2) + 1))
        elif brd.chk_hor_sym():
            searchArea = brd.__iter__((0, int(round(brd.width/2))), int(round(brd.width/2) + 1), brd.height)
        else:
            searchArea = brd.__iter__()
        
        if emptyStart:
            candidates = [cell for cell in searchArea if cell is not None and not cell.peg]
        else: 
            candidates = [cell for cell in searchArea if cell is not None and cell.peg]
        
        def _check_board_consistency(brd2):
            for b, g in zip(brd2.compact, self.goal.compact):
                if b.peg and not g.peg:
                    return False
            return True 
        
        ret = []
        if _check_board_consistency(brd):
            for tile in TILES:
                if len(tile.full) - 1 < len(brd.empty):
                    for cell in candidates:
                        tmptile = tile.copy()
                        newBoard = tmptile.apply(cell.coords, brd, emptyStart, REVERSEPROBLEM)
                        if newBoard != False:
                            if __debug__:
                                print "applied \n" + str(tmptile) + "(reversed) on\n" + str(brd)\
                                + "with " + str(tmptile.boardStart) + " <t=b> " + str(cell.coords)
                                print newBoard
                            ret.append((tmptile, newBoard))
                            self.generated += 1
                        
        return ret


class TileProblem(object, Problem):
    """
    Solve a board move by move
    """
    def __init__(self, initial, goal):
        Problem.__init__(self, initial, goal)
    
    def successor(self, brd):
        moves = []
        for n in brd.compact:
            if not n.peg:
                if (n.lleft != None) and n.left.peg and n.lleft.peg:
                    m = Move(n.lleft.coords, RIGHT)
                    moves.append((m, m(brd)))
                if (n.rright is not None) and n.right.peg and n.rright.peg:
                    m = Move(n.rright.coords, LEFT)
                    moves.append((m, m(brd)))
                if (n.uup is not None) and n.up.peg and n.uup.peg:
                    m = Move(n.uup.coords, DOWN)
                    moves.append((m, m(brd)))
                if (n.ddown is not None) and n.down.peg and n.ddown.peg:
                    m = Move(n.ddown.coords, UP)
                    moves.append((m, m(brd)))
        return moves
    
        
def translate2moves(tile_solution):
    """
    This function takes a tile solution
    and convert it in single moves.
    """
    memoized = {}
    moves = []
    for node in tile_solution[1:]:
        if not node.action in memoized:
            p = TileProblem(node.action, node.action.getGoal())
            end_node = depth_first_tree_search(p)
            assert end_node != None
            reloc_moves = end_node.path()
            reloc_moves.reverse()
            memoized[node.action] = reloc_moves
        displacement = (node.action.boardStart[0] - node.action.start[0],
                        node.action.boardStart[1] - node.action.start[1])
        moves.extend([mv.action.displace(displacement) for mv in memoized[node.action][1:]])
    return moves
    

def go(problem, reverseproblem, fringe, rfringe):
    """
    Returns True when the original problem is
    to be expanded, False when the reverse has 
    to, raise StopIteration when both fringe are 
    empty. Make the problem with the smallest 
    fringe proceed.
    """
    if problem.generated < reverseproblem.generated and fringe:
        return True
    elif rfringe:
        return False
#    if (len(fringe) <= len(rfringe)) and fringe:
#        return True
#    elif rfringe:
#        return False
    else:
        raise StopIteration()
    

def bidirectional_search(original_problem, reverse_problem, go, \
                         original_fringe = FIFOQueue(), reverse_fringe = FIFOQueue()\
                         ):
    
    def _put(node, frin):
        k = len(node.state.empty)
        if k in frin:
            frin[k][node.state] = node
        else:
            frin[k] = {node.state : node}
    
    def _fringe_intersect(state, fringe):
        k = len(state.empty)
        if k in fringe:
            return state in fringe[k]
        else:
            return False
        
    original_problem.goal_test = _fringe_intersect
    reverse_problem.goal_test  = _fringe_intersect
    
    reverse_closed  = {}
    original_closed = {}
    reverse_root = Node(reverse_problem.initial)
    original_root = Node(original_problem.initial)
    _put(reverse_root, reverse_hashed_fringe)
    reverse_fringe.append(reverse_root)
    _put(original_root, original_hashed_fringe)
    original_fringe.append(original_root)
    
    while original_fringe or reverse_fringe:
        try:
            while not go(original_problem, reverse_problem, original_fringe, reverse_fringe):
                node = reverse_fringe.pop() # this while deals with reverse problem
                k = len(node.state.empty)
                if reverse_problem.goal_test(node.state, original_hashed_fringe):
                    print "found by reverse_problem"
                    sol_node = original_hashed_fringe[k][node.state]
                    to_solution = node.path()
                    for i in range(len(to_solution) - 1, 0, -1):
                        to_solution[i].action = to_solution[i - 1].action
                    solution = sol_node.path()
                    solution.reverse()
                    to_solution[0].action = solution.pop().action
                    solution.extend(to_solution)
                    return solution
                if node.state not in reverse_closed:
                    reverse_closed[node.state] = True
                    for new_node in node.expand(reverse_problem):
                        reverse_fringe.append(new_node)
                        _put(new_node, reverse_hashed_fringe)
            
            
            while go(original_problem, reverse_problem, original_fringe, reverse_fringe):
                node = original_fringe.pop() # this while deals with original_problem
                k = len(node.state.empty)
                if original_problem.goal_test(node.state, reverse_hashed_fringe):
                    print "found by original_problem"
                    sol_node = reverse_hashed_fringe[k][node.state]
                    to_solution = sol_node.path() # from matching state to solution
                    for i in range(len(to_solution) - 1, 0, -1):
                        to_solution[i].action = to_solution[i - 1].action
                    solution = node.path()
                    solution.reverse()
                    to_solution[0].action = solution.pop().action
                    solution.extend(to_solution)
                    return solution 
                if node.state not in original_closed:
                    original_closed[node.state] = True
                    for new_node in node.expand(original_problem):
                        original_fringe.append(new_node)
                        _put(new_node, original_hashed_fringe)
        except StopIteration:
            print "Both fringe exhausted!"
            break
        
    return None


if __name__ == '__main__':
    
    B = Board(ENGLISH)
    
    GOAL = B.copy()
    GOAL.complement()
    GOAL[4][3].put()
    GOAL[5][3].put()
    
    B[3][3].pick()
    
    P = BoardProblem(B, GOAL)
    IP  = ReverseBoardProblem(GOAL, B)
    T0 = time.clock()
    sol = bidirectional_search(P, IP, go, FIFOQueue(), FIFOQueue())
    moves = translate2moves(sol)
    T = time.clock() - T0
    
    print B
    for move in moves:
        B = move(B)
        print move
        print B
    print "Solution found in", str(T) + "s"
        
    