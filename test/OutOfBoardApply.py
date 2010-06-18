'''
Created on 02/giu/2010

@author: andrea
'''
import unittest
from board import *
from sys import stderr



class OutOfBoardTest(unittest.TestCase):


    def setUp(self):
        self.b = Board(ENGLISH)
        self.b[1][2].pick() #up
        self.b[4][1].pick() #left
        self.b[5][4].pick() #down
        self.b[2][5].pick() #right
        print "Set up!", self.b


    def tearDown(self):
        pass


    def testRightOutOfBoard(self):
        """
        This test check if applying a tile
        that exceeds right border 
        return False 
        """
        print "Applying ", TILES[22], "on", self.b, \
        "with boar start", (2, 5)
        res = TILES[22].apply((2, 5), self.b)
        try:
            assert res == False
        except AssertionError:
            print >> stderr, res
            raise
    
    
    def testDownOutOfBoard(self):
        """
        This test check if applying a tile
        that exceeds down border 
        return False 
        """
        print "Applying ", TILES[18], "on", self.b, \
        "with boar start", (5, 4)
        res = TILES[18].apply((5, 4), self.b)
        try:
            assert res == False
        except AssertionError:
            print >> stderr, res
            raise
        
        
    def testLeftOutOfBoard(self):
        """
        This test check if applying a tile
        that exceeds down border 
        return False 
        """
        print "Applying ", TILES[23], "on", self.b, \
        "with boar start", (4, 1)
        res = TILES[23].apply((4, 1),self.b)
        try:
            assert res == False
        except AssertionError:
            print >> stderr, res
            raise


    def testUpOutOfBoard(self):
        """
        This test check if applying a tile
        that exceeds down border 
        return False 
        """
        print "Applying ", TILES[17], "on", self.b, \
        "with boar start", (1, 2)
        res = TILES[17].apply((1, 2),self.b)
        try:
            assert res == False
        except AssertionError:
            print >> stderr, res
            raise


    def testRightInBoard(self):
        """
        This test check if applying a tile
        that exceeds right border 
        return False 
        """
        self.b[2][4].pick() #right
        print "Applying ", TILES[22], "on", self.b, \
        "with boar start", (2, 4)
        res = TILES[22].apply((2, 4), self.b)
        try:
            assert res != False
            print res
        except AssertionError:
            print >> stderr, res
            raise
    
    
    def testDownInBoard(self):
        """
        This test check if applying a tile
        that exceeds down border 
        return False 
        """
        self.b[4][4].pick() #down
        print "Applying ", TILES[18], "on", self.b, \
        "with boar start", (4, 4)
        res = TILES[18].apply((4, 4), self.b)
        try:
            assert res != False
            print res
        except AssertionError:
            print >> stderr, res
            raise
        
        
    def testLeftInBoard(self):
        """
        This test check if applying a tile
        that exceeds down border 
        return False 
        """
        self.b[4][2].pick() #left
        print "Applying ", TILES[23], "on", self.b, \
        "with board start", (4, 2)
        res = TILES[23].apply((4, 2), self.b)
        try:
            assert res != False
            print res
        except AssertionError:
            print >> stderr, res
            raise


    def testUpInBoard(self):
        """
        This test check if applying a tile
        that exceeds down border 
        return False 
        """
        self.b[2][2].pick() #up
        print "Applying ", TILES[17], "on", self.b, \
        "with boar start", (2, 2)
        res = TILES[17].apply((2, 2), self.b)
        try:
            assert res != False
            print res
        except AssertionError:
            print >> stderr, res
            raise


if __name__ == "__main__":
    unittest.main()
    