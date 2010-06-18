'''
Created on 15/giu/2010

@author: andrea
'''

from board import Board
from copy import copy, deepcopy

class Tile(Board):
    
    def __init__(self, rows_definition, catalyst = []):
        """
        rows_definition -- a list of tuples in the form (offset, number of cells)
        catalyst -- a list of two coords tuples that are "catalyst" for the tile:
        in base configuration the second is forced to be empty. The peg in the catalizer 
        position is the only survivor after the tile has been applied
        emptyStart -- a boolean stating whether this tile has to be bound to the empty or 
        catalyst cell or not.   
        """
        Board.__init__(self, rows_definition)
        self[catalyst[1][0]][catalyst[1][1]].pick()
        self.catalyst = catalyst
        self.start = None
        
        
    def getGoal(self):
        """
        The local goal for this Tile.
        (all empty but one)
        """
        ret = self.copy()
        for cell in ret:
            if cell is not None and cell.peg \
            and cell.coords not in self.catalyst:
                cell.pick()
        return ret
    
    def setParams(self, start, emptyStart = True, reverse = False):
        """
        Set parameters for __call__ function 
        start -- the board cell coordinates corresponding to a catalyst
        reverse -- if True apply the Tile in reverse mode: searches for 
        complement of Tile and fill it.
        """
        
        self.boardStart = start
        
        if emptyStart:
            self.start = self._get(self.catalyst[1]).peg == False and \
            self.catalyst[1] or \
            self.catalyst[0]
        else:
            self.start = self._get(self.catalyst[0]).peg == False and \
            self.catalyst[1] or \
            self.catalyst[0]
        
        self.reverse = reverse
        
        
    def __call__(self, board):
        """
        Call apply function with parameters set 
        via setParams function
        """
        try:
            return self.apply(self.boardStart, board, True, False)
        except UnboundLocalError:
            raise
        
        
    def apply(self, start, board, emptyStart = True, reverse = False):
        """
        Return an updated copy of board
        if it is applied in a fitting position 
        else return False
        start -- the board cell coordinates corresponding to a catalyst
        board -- the board this tile is applied to
        reverse -- if True apply the Tile in reverse mode: searches for 
        complement of Tile and fill it.
        """
        
        if not hasattr(self, 'boardStart'):
            self.setParams(start, emptyStart, reverse) 
        
        if self.boardStart[0] - self.start[0] >= 0 and self.boardStart[1] - self.start[1] >= 0 and\
        (self.boardStart[0] + self.height - self.start[0] <= board.height) and \
        (self.boardStart[1] + self.width - self.start[1] <= board.width):
            
            brd2 = board.copy()
            
            for (t, b) in zip(self.__iter__(), \
                              brd2.__iter__((self.boardStart[0] - self.start[0], \
                                             self.boardStart[1] - self.start[1]), \
                                             self.width, self.height)):
                if t == None:
                    continue
                elif b == None or \
                    self.start[0] - t.coords[0] != self.boardStart[0] - b.coords[0] or\
                    self.start[1] - t.coords[1] != self.boardStart[1] - b.coords[1]:
                    return False
                else:
                    
                    if not self.reverse:
                        
                        if t.peg != b.peg:
                            return False
                        elif t.peg == b.peg:
                            if t.coords not in self.catalyst:  
                                brd2[b.coords[0]][b.coords[1]].pick()
                            continue
                        
                    else: # handle reverse operations
                            
                        if t.peg and b.peg and t.coords not in self.catalyst\
                        or not t.peg and b.peg:
                            return False
                        elif t.peg and not b.peg:
                            brd2[b.coords[0]][b.coords[1]].put()
                            continue
            
            return brd2
        else: # Matches Board "border condition"
            return False
            
    


BASETILES = []

# / + /
# / + /
# + + *
T1 = Tile([(1, 1), (1, 1), (0, 3)], [(2, 0), (2, 2)])


# + * * /
# / + + +
# / + + +
T2 = Tile([(0, 3), (1, 3), (1, 3)], [(0, 0), (0, 2)])
T2[0][1].pick()
BASETILES.append(T2)
BASETILES.append(T1)
# / +
# + + *
# / +
# / + + +
T3 = Tile([(1, 1), (0, 3), (1, 1), (1, 3)], [(1, 0), (1, 2)])
BASETILES.append(T3)

# +
# +
# *
# +
#T4 = Tile([(0, 1), (0, 1), (0, 1), (0, 1)], [(1, 0), (2, 0)])
#BASETILES.append(T4)
TILES   = []


def rec_helper(node, transformations = None, ttiles = []):
    
    if transformations is None:
        transformations = [mkHorizontalSym, mkVerticalSym, mkSwapCatal, mkRotation]
    elif transformations == []:
        return ttiles
    t = transformations[0]
    if node is not None and node not in ttiles:
        ttiles.append(node)
    otran = []
    for tile in ttiles:
        tran = t(tile)
        while tran not in otran:
            if tran not in ttiles:
                ttiles.append(tran)
            otran.append(tran)
            tran = t(tran)
    rec_helper(None, transformations[1:], ttiles)
    return ttiles


def __init__():
    
    for t in BASETILES:
        res = rec_helper(t, None, [])
        for tile in res:
            TILES.append(tile)

    
def mkHorizontalSym(self):
    """
    Build a symmetrical copy of this board
    swapping left/right cell values. In other 
    words the copy returned is symmetrical
    w.r.t. the VERTICAL symmetry axis of this
    board. If such an axis doesn't exist raise 
    an error. 
    """
    ret = self.copy()
    new_catalyzer = []
    for row in ret.rows:
        rrow = copy(row)
        rrow.reverse()
        i = 0
        for left, right in zip(row, rrow):
            if i >= round(len(row) / 2):
                break
            elif isinstance(left, Board.Node) and \
            right is None:
                if left.coords in self.catalyst:
                    new_catalyzer.append((left.y, ret.width - (i + 1)))
                row[i].x = ret.width - (i + 1)
                row[ret.width - (i + 1)] = row[i]
                row[i] = None
            elif left is None and \
            isinstance(right, Board.Node):
                if right.coords in self.catalyst:
                    new_catalyzer.append((right.y, i))
                row[ret.width - (i + 1)].x = i
                row[i] = row[ret.width - (i + 1)]
                row[ret.width - (i + 1)] = None
            elif isinstance(left, Board.Node) and \
            isinstance(right, Board.Node):
                if left.coords in self.catalyst:
                    new_catalyzer.append((left.y, ret.width - (i + 1)))
                if right.coords in self.catalyst:
                    new_catalyzer.append((right.y, i))
                rpeg = right.peg
                right.set(left.peg)
                left.set(rpeg)
            elif left.__class__ == None and \
            right.__class__ == None:
                pass
            i += 1
    ret.catalyst = new_catalyzer
    return ret
    
    
def mkVerticalSym(self):
    """
    Build a symmetrical copy of this board
    swapping up/down cell values. In other 
    words the copy returned is symmetrical
    w.r.t. the HORIZONTAL symmetry axis of this
    board. If such an axis doesn't exist raise 
    an error.
    """
    ret = self.copy()
    rrows = copy(ret.rows)
    rrows.reverse()
    i = 0
    new_catalyzer = []
    for up, down in zip(ret.rows, rrows):
        if i >= round(ret.height / 2):
            break
        else:
            for cellup, celldown in zip(up, down):
                if cellup is not None:
                    if cellup.coords in self.catalyst:
                        new_catalyzer.append((ret.height - (cellup.y + 1), cellup.x))
                    ret.rows[i][cellup.x].y = ret.height - (cellup.y + 1)
                if celldown is not None:
                    if celldown.coords in self.catalyst:
                        new_catalyzer.append((ret.height - (celldown.y + 1), celldown.x))
                    ret.rows[ret.height - (i + 1)][celldown.x].y = ret.height - (celldown.y + 1)
                    
            tmp = ret.rows[i]
            ret.rows[i] = ret.rows[ret.height - (i + 1)]
            ret.rows[ret.height - (i + 1)] = tmp
        i += 1
    ret.catalyst = new_catalyzer
    return ret


    
    
def mkRotation(self):
    """
    Rotate the board 90 
    degrees clockwise
    """
    ret = self.copy()
    rrows = deepcopy(ret.rows)
    rrows.reverse()
    i = 0
    rdiff = ret.height - ret.width
    new_catalyst = []
    for row in rrows:
        for j in xrange(len(row)):
            if row[j] is not None:
                if row[j].coords in ret.catalyst:
                    new_catalyst.append((j, i))
                row[j].x = i
                row[j].y = j
            try:
                ret.rows[j][i] = row[j]
            except IndexError: # Got error on index i: column missing
                try:
                    ret.rows[j].append(row[j])
                except IndexError:
                    ret.rows.append([row[j]])            
        i += 1
    if rdiff > 0:
        ret.rows = ret.rows[0:len(ret.rows) - rdiff]
    elif rdiff < 0:
        for i in xrange(self.height):
            if len(ret.rows[i]) + rdiff > 0:
                ret.rows[i] = ret.rows[i][0:len(ret.rows[i]) + rdiff]
    else:
        pass
    ret.catalyst = new_catalyst
    for node in ret:
        if node != None:
            node.brd = ret
    return ret
    
def mkSwapCatal(self):
    """
    Return a copy with 
    swapped empty and full
    catalyst cells.
    """
    ret = self.copy()
    tmpValue = ret[ret.catalyst[0][0]][ret.catalyst[0][1]].peg
    ret[ret.catalyst[0][0]][ret.catalyst[0][1]].set(ret[ret.catalyst[1][0]][ret.catalyst[1][1]].peg)
    ret[ret.catalyst[1][0]][ret.catalyst[1][1]].set(tmpValue)
    return ret
                
        
    
__init__()

if __name__ == '__main__':
    
    i = 0
    for t in TILES:
        print i
        print t
        print str(t.catalyst)
        i += 1 