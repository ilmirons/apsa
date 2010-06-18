'''
Created on 06/giu/2010

@author: andrea
'''
import unittest
import pegsolitaire


class Test(unittest.TestCase):


    def testDirectionProperties(self):
        B = pegsolitaire.Board(pegsolitaire.ENGLISH)
        assert B[2][2].lleft != None
        assert B[2][2].rright != None
        assert B[2][2].uup != None
        assert B[2][2].ddown != None
        t = pegsolitaire.TILES[8]
        print t
        print t[1][2].brd
        assert t[1][2].brd == t 

    def testSolveTileProblem(self):
        for t in pegsolitaire.TILES:
            print "\nsolving", t
            p = pegsolitaire.TileProblem(t, t.getGoal())
            sol = pegsolitaire.depth_first_tree_search(p)
            pegsolitaire.print_sol(sol)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()