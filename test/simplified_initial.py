'''
Created on 02/giu/2010

@author: andrea
'''
import unittest
import board
import pegsolitaire


class Test(unittest.TestCase):


    def setUp(self):
        self.B = board.Board(board.ENGLISH)
        self.easy = self.B.copy()
        self.easy.complement()
        self.easy[2][0].put()
        self.easy[2][1].put()
        self.easy[3][0].put()
        self.easy[3][1].put()
        self.easy[3][2].put()
        self.easy[4][0].put()
        self.easy[4][1].put()
        self.easy[4][2].put()
        self.easy[4][3].put()
        self.easy[5][2].put()
        self.easy[5][3].put()
        self.easy[6][2].put()
        self.easy[6][3].put()
        self.easy[6][4].put()
        
        GOAL = self.B.copy()
        GOAL.complement()
        GOAL[4][3].put()
        GOAL[5][3].put()
        self.P  = pegsolitaire.BoardProblem(self.easy, GOAL)
        self.IP = pegsolitaire.ReverseBoardProblem(GOAL, self.easy)


    def tearDown(self):
        pass
    
    
    def testApplyBigL(self):        
        b = board.TILES[12].apply((3, 2), self.easy, False)
        print b
        assert board.TILES[28].apply((4, 3), b, False) != False


    def testBidirectionalSearch(self):
        sol = pegsolitaire.bidirectional_search(self.P, self.IP, pegsolitaire.go,
                                                 pegsolitaire.FIFOQueue(), pegsolitaire.FIFOQueue())
        assert pegsolitaire.print_sol(sol)


if __name__ == "__main__":
#    import sys; sys.argv = ['', 'Test.testApplyBigL']
    unittest.main()