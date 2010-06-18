'''
Created on 14/giu/2010

@author: andrea
'''
import sys
sys.path.append("..")
import unittest
import board

class Test(unittest.TestCase):


    def setUp(self):
        self.B = board.Board(board.ENGLISH)
        self.C = board.Board(board.ENGLISH)
        self.C.complement()
        self.B.complement()
        self.B[0][4].put()
        self.B[1][2].put()
        self.B[1][3].put()
        self.B[2][0].put()
        self.B[2][4].put()
        self.B[2][5].put()
        self.B[4][5].put()
        self.B[4][6].put()
        self.B[6][2].put()
        self.C[0][3].put()
        self.C[1][2].put()
        self.C[1][4].put()
        self.C[2][1].put()
        self.C[2][5].put()
        self.C[3][0].put()
        self.C[3][6].put()
        self.C[4][1].put()
        self.C[4][5].put()
        self.C[5][2].put()
        self.C[5][4].put()
        self.C[6][4].put()
        print self.B
        


    def tearDown(self):
        pass


    def testReachable(self):
        assert board.reachable(self.B[3][3], 5, [], [])
        assert board.reachable(self.B[5][4], 9, [], [])
#        assert board.reachable(self.C[4][6], 5, [])
        
    
    def testReachableLimit(self):
        assert not board.reachable(self.B[3][3], 4, [], [])
        assert not board.reachable(self.B[5][4], 8, [], [])
        
        
    def testNotReachable(self):
        assert not board.reachable(self.B[5][2], 19, [], [])
        assert not board.reachable(self.B[4][3], 19, [], [])


if __name__ == "__main__":
    
    unittest.main()