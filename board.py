# -*- coding: utf-8 -*-
'''

@author: andrea
'''

from copy import copy, deepcopy

UP    = 0
DOWN  = 2
LEFT  = 1
RIGHT = 3

ENGLISH = [(2, 3), (2, 3), (0, 7), (0, 7), (0, 7), (2, 3), (2, 3)]
FRENCH  = [(2, 3), (1, 5), (0, 7), (0, 7), (0, 7), (1, 5), (2, 3)]
REVERSEPROBLEM = True


def _dir2str(direct):
    """
    Convert a direction constant to String
    """
    if direct == UP:
        return "UP"
    elif direct == DOWN:
        return "DOWN"
    elif direct == LEFT:
        return "LEFT"
    elif direct == RIGHT:
        return "RIGHT"
    else:
        return "INVALID DIRECTION"


class MoveError(Exception):
    """
    Exception raised when performing a move fails
    """
    
    def __init__(self, move = None, brd = None):
        Exception.__init__(self)
        self.board = brd
        self.move = move
        
    def __str__(self):
        return "Move"  + ((self.move == None) and " " or " " + str(self.move) + " ")\
            + "failed" + ((self.board == None) and "! " or ". " + "Board was: \n\n" \
                         + str(self.board))  
    
    
class OutOfBoardError(MoveError):
    """
    Exception raised on attempting move out of Board
    """
    
    def __init__(self, move = None, brd = None):
        MoveError.__init__(self, move, brd)
    
        
class PegError(MoveError):
    """
    Exception raised when trying to put 
    a peg when there is already one
    """
    
    def __init__(self, move = None, brd = None):
        MoveError.__init__(self, move, brd)
    
                
class MissingPegError(MoveError):
    """
    Exception raised when trying to take
    a peg where there isn't one
    """
    
    def __init__(self, move = None, brd = None):
        MoveError.__init__(self, move, brd)

        
class NotOverlappingRowsError(Exception):
    """
    Exception raised when trying to build a 
    Board rows do not overlap.
    """
    
    def __init__(self):
        Exception.__init__(self)


def reachable(position, limit, visited):
    """
    Tells if a position is reachable in
    (limit - 1)/2 moves. Buggy function,
    DON'T TRUST!!!
    """
    
    
    if __debug__:
        print " " * len(visited), "visiting", repr(position)
        print " " * len(visited), "already visited:", visited
        print " " * len(visited), str(limit - len(visited))
        print
    
    if position is None or position in visited or limit - len(visited) == 0:
        return False
    else:
        visited.append(position)
        if position.peg:
            return True
        else:
            reachable_test = reachable(position.up, limit, visited) and\
            reachable(position.uup, limit, visited) or \
            reachable(position.down, limit, visited) and\
            reachable(position.ddown, limit, visited) or \
            reachable(position.left, limit, visited) and\
            reachable(position.lleft, limit, visited) or \
            reachable(position.right,limit, visited) and\
            reachable(position.rright, limit, visited)
            if reachable_test:
                if __debug__:
                    print repr(position), "is reachable."
                    print
                return True
            else:
                visited.remove(position) # rimuove empty
                if len(visited) > 1 and visited[len(visited) - 1].peg: 
                    visited.pop() # rimuove eventuali True
                return False


class Board:
    """
    Representation of a Board.
    """
    
    def __init__(self, rows_definition):
        self.rows_definition = rows_definition
        self.rows    = []
        i = 0
        j = 0
        width = max([(rdef[0] + rdef[1]) for rdef in rows_definition ])
        for rdef in rows_definition:
            self.rows.append([])
            while j < width:
                if j < rdef[0] or j >= rdef[0] + rdef[1]:
                    self.rows[i].append(None)
                else:
                    cell = Board.Node(self, i, j)
                    self.rows[i].append(cell)
                j += 1
            j =  0
            i += 1
        self._memoized_compact = None
        self.clses = []
        self.clses.extend(self._init_pagoda_clses())
        self._memoized_length = None
        self.obs = None
        
            
    def _init_pagoda_clses(self):
        """
        Init a simple pagoda function
        and "closed move classes".
        Note that some board configurations 
        may have empty classes.
        """
        a = []; b = [] #IGNORE:C0321
        c = []; d = [] #IGNORE:C0321
        row_selector = ((a, b), (c, d))
        for cell in self.compact:
            row_selector[cell.y % 2][cell.x % 2].append(cell)
            cell.pvalue = cell.y % 2 + 1 + cell.x % 2 
        return a, b, c, d
    
    
    def set_observed_class(self, cell):
        """
        Set the class that contains cell
        with coords as a special observed class.
        """
        try:
            if cell.coords in [c.coords for c in self.clses[0]]:
                self.obs = self.clses[0]
            elif cell.coords in [c.coords for c in self.clses[1]]:
                self.obs = self.clses[1]
            elif cell.coords in [c.coords for c in self.clses[2]]:
                self.obs = self.clses[2]
            elif cell.coords in [c.coords for c in self.clses[3]]:
                self.obs = self.clses[3]
            else:
                print self.clses 
                raise OutOfBoardError()
        except IndexError:
            print self.clses 
            raise OutOfBoardError()
       
    
    def __eq__(self, other):
        if other == None:
            return False
        elif self.rows_definition != other.rows_definition:
            return False
        else:
            it1 = self.__iter__()
            it2 = other.__iter__()
            try:
                while it1.next() == it2.next(): #IGNORE:E1101
                    continue
                return False
            except StopIteration:
                return True

        
    def __getitem__(self, index):
        return self.rows[index]
    
    
    def __hash__(self):
        i = 0
        ret = 0
        for cell in self.compact:
            if cell.peg:
                ret += 2 ** i 
                i += 1
        return ret
    
    
    def __iter__(self, start = (0, 0), width = 0, height = 0):
        """
        Iterate (sub)Board cells line by line starting from start
        and stopping at (width, height). If width or height are
        non-positive it iterates over entire length of row/column
        start -- the top left coordinates of the sub board
        width -- number of columns in the sub board
        height -- number of columns in in the sub board 
        """
        
        if width <= 0:
            width = self.width
        elif width > self.width:
            raise OutOfBoardError, "End width of iteration out of (extended) border"
        if height <= 0:
            height = self.height
        elif height > self.height:
            raise OutOfBoardError, \
                "End height of iteration out of (extended) border"
        if start[0] < 0:
            raise OutOfBoardError, \
                "Start width of iteration out of (extended) border."
        if start[1] < 0:
            raise OutOfBoardError, \
                "Start height of iteration out of (extended) border."
        for row in (self.rows[start[0]:(start[0] + height)]):
            for cell in row[start[1]:start[1] + width]:
                yield cell
                
    
    def __len__(self):
        if self._memoized_length == None:
            self._memoized_length = len(self.compact) 
        return self._memoized_length
                
    def __repr__(self):
        ret = "\n"
        for row in self.rows:
            for cell in row:
                ret += (cell == None and "//////////" or repr(cell))
            ret += "\n"
        return ret + "\n"
    
    
    def __str__(self):
        ret = "\n"
        for row in self.rows:
            for cell in row:
                ret += (cell == None and "  " or str(cell))
            ret += "\n"
        return ret + "\n"
    
    
    def _get(self, (y, x)):
        """
        Get a cell from a tuple of coords.
        """
        return self[y][x]
    
    
    @property
    def compact(self):
        """
        Return a list of non-None
        cells of the board. Useful for iterations.
        """
        if self._memoized_compact == None:
            self._memoized_compact = [cell for cell in self if cell != None]
        return self._memoized_compact
    
    
    def chk_hor_sym(self):
        """
        Check whether this board is symmetric w.r.t.
        a VERTICAL axis.
        """
        for row in self.rows:
            rrow = copy(row)
            rrow.reverse()
            for i in xrange(int(round(len(row)/2))):
                if row[i] == rrow[i]:
                    continue
                else:
                    return False
        return True 
    
    
    def chk_vert_sym(self):
        """
        Check whether this board is symmetric w.r.t.
        an HORIZONTAL axis.
        """
        for j in xrange(self.width):
            for i in xrange(int(round(self.height/2))):
                if self.rows[i][j] == self.rows[self.height - (i + 1)][j]:
                    continue
                else:
                    return False
        return True
                    
        
    def copy(self):
        """
        Return a deep copy of the Board.
        """
        cpy = deepcopy(self)
        # usually we use copy to perform transformations on the board
        # so it's good to reset memoized values
        cpy._memoized_compact = None 
        return cpy
    
    
    def complement(self):
        """
        Invert empty and full cells
        """
        for cell in self.compact:
            cell.set(not cell.peg)
            
    @property
    def empty(self):
        """
        List of empty cells.
        """
        return [cell for cell in self.compact if not cell.peg]
    
    
    @property
    def full(self):
        """
        List of full cells.
        """
        return [cell for cell in self.compact if cell.peg]
    
    
    @property
    def height(self):
        """
        Number of rows in this board
        """
        return len(self.rows)
    
    @property
    def pagoda(self):
        """
        Pagoda function value for this board.
        """
        return sum([c.pvalue for c in self.compact if c.peg])
    
    
    @property
    def width(self):
        """
        Number of columns in this board
        """
        return len(self.rows[0])
    
    
    class Node:
        """
        A cell on the Board. Note this is created just inside board.
        brd -- the board this cell belongs to.
        y -- the row this node belongs to.
        x -- the column this node belongs to. 
        """
    
    
        def __init__(self, brd, y, x): #IGNORE:C0103
            self._val = True
            self.pvalue = 0
            self.x = x #IGNORE:C0103
            self.y = y #IGNORE:C0103
            self.brd = brd

        
        @property
        def up(self): #IGNORE:C0103
            if self.y - 1 < 0:
                return None
            return self.brd[self.y - 1][self.x]
    
        @property
        def down(self): #IGNORE:C0111
            try:
                return self.brd[self.y + 1][self.x]
            except IndexError:
                return None
    
        @property
        def left(self): #IGNORE:C0111
            if self.x - 1 < 0:
                return None
            return self.brd[self.y][self.x - 1]
    
        @property
        def right(self): #IGNORE:C0111
            try:
                return self.brd[self.y][self.x + 1]
            except IndexError:
                return None
            
        @property
        def coords(self): #IGNORE:C0111
            return (self.y, self.x)
        
        @property
        def lleft(self): #IGNORE:C0111
            if self.left is None:
                return None
            else:
                return self.left.left
        
        @property
        def uup(self): #IGNORE:C0111
            if self.up is None:
                return None
            else:
                return self.up.up
    
        @property
        def ddown(self): #IGNORE:C0111
            if self.down is None:
                return None
            else:
                return self.down.down
    
        @property
        def rright(self): #IGNORE:C0111
            if self.right is None:
                return None
            else:
                return self.right.right
    
        @property
        def peg(self):
            """
            True if there is a peg in this cell.
            """
            return self._val
        

        def pick(self):
            """
            Pick the peg from the current cell
            Makes no check.
            """
            self._val = False
        
        def put(self):
            """
            Put a peg in current cell
            Makes no check.
            """
            self._val = True
        
        
        def makemove(self, direction):
            """
            Perform a move on the Board.
            Raise appropriate Exception on Error.
            (e.g. moving a peg in a full cell)
            Return this board after applying the move.
            (changes are local, no copy produced)
            """
            self.pick()
            try:
                if direction == LEFT:
                    midpeg = self.left
                    endpeg = self.lleft
                elif direction == RIGHT:
                    midpeg = self.right
                    endpeg = self.rright
                elif direction == UP:
                    midpeg = self.up
                    endpeg = self.uup
                elif direction == DOWN:
                    midpeg = self.down
                    endpeg = self.ddown
                else:
                    raise MoveError((self.coords, _dir2str(direction)), self.brd)
                if midpeg.peg:
                    midpeg.pick()
                else:
                    raise MissingPegError((self.coords, _dir2str(direction)), \
                                          self.brd)
                if endpeg.empty:
                    endpeg.put()
                else: raise PegError((self.coords, _dir2str(direction)), self.brd)
            except AttributeError:
                raise OutOfBoardError((self.coords, _dir2str(direction)), self.brd)
            return self.brd
    

        def set(self, boolean):
            """
            Set the status of this cell (empty/full)
            """
            self._val = boolean
    
    
        def empty(self): #IGNORE:C0111
            return self._val == False
    
    
        def __eq__(self, other):
            if other is None:
                return False
            return other.peg == self.peg and\
            other.coords == self.coords
    
    
        def __str__(self):
            if self._val:
                return "* "
            else:
                return ". "
    
        
        def __repr__(self):
            return (str(self) + "@" + str(self.coords) + \
                    ":" + str(self.pvalue)).rjust(12)
    
    
        def __hash__(self):
            return hash((self.coords, self._val))

    
class Move: #IGNORE:R0903
    """
    An object representing a move on the board.
    """
    
    # Note this object has no object references
    # apart from __call__() method. This property
    # should be kept true since we use copy()
    # instead of deep copy
    
    def __init__(self, coords, direction):
        """
        Init the parameters of the move.
        coords -- coordinates of starting cell
        direction -- integer, direction of the move
        """
        self.y, self.x = coords
        self.direction = direction
        
        
    def __call__(self, brd):
        """
        Perform a move on a copy of 
        brd, according to parameters
        set via __init__()
        brd -- starting position
        """
        brdcpy = brd.copy() 
        return brdcpy[self.y][self.x].makemove(self.direction)
    
    
    def displace(self, (y_offset, x_offset)):
        """
        Return a copy of the move shifted
        """
        ret = copy(self)
        ret.y += y_offset
        ret.x += x_offset
        return ret
    
    
    def __str__(self):
        return str((self.y, self.x)) + ":" + _dir2str(self.direction) 
        



if __name__ == "__main__":
    
    # A simple test for pagoda function
    
    B = Board(ENGLISH)
    
    for cel in B.compact:
        if cel.uup != None:
            assert cel.pvalue + cel.up.pvalue >= cel.uup.pvalue
        if cel.ddown != None:
            assert cel.pvalue + cel.down.pvalue >= cel.ddown.pvalue
        if cel.lleft != None:
            assert cel.pvalue + cel.left.pvalue >= cel.lleft.pvalue
        if cel.rright != None:
            assert cel.pvalue + cel.right.pvalue >= cel.rright.pvalue

        
    

    