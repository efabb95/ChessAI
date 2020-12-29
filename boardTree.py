import chess
import math

class Node:
    """ Each BoardNode has the following attributes:
    - A board representing the position
    - The absolute move depth
    - A list of legal moves for the player whose turn it represents
    - A list of the children Nodes
    - Minmaxed utility value of the current position for the player to move
    - Related best move in variable bestMove
    """
    def __init__(self, board, absoluteMoveDepth):
        self.board = board
        self.absoluteDepth = absoluteMoveDepth
        self.legalMoves = list(self.board.generate_legal_moves())
        self.children = []
        self.utility = None
        self.maxEval = 10000
    

    def __repr__(self):
        if self.board.turn == chess.WHITE:
            color = 'White'
        else:   
            color = 'Black'
        return str(self.board) + f'\nMove {self.absoluteDepth}, {color} to move. This node currently has {len(self.children)} children plies.'
    
    def minChildrenUtility(self):
        minUtility = math.inf
        bestMove = None
        for i in range(len(self.children)):
            if self.children[i].utility < minUtility:
                minUtility = self.children[i].utility
                bestMove = self.legalMoves[i]
        return minUtility, bestMove


    def maxChildrenUtility(self):
        maxUtility = -math.inf
        bestMove = None
        for i in range(len(self.children)):
            if self.children[i].utility > maxUtility:
                maxUtility = self.children[i].utility
                bestMove = self.legalMoves[i]
        return maxUtility, bestMove


    # Recursively expand tree up to the specified relative depth in plies
    def expand(self, plies):
        # If the board is in an end position, return
        if not self.legalMoves:
            return
        # if the node has never been expanded, create children for the next ply
        elif not self.children:
            newDepth = self.absoluteDepth
            if self.board.turn == chess.BLACK:
                newDepth = newDepth+1
            for move in self.legalMoves:
                newBoard = self.board.copy()
                newBoard.push(move)
                self.children.append(Node(newBoard, newDepth))
        # If the ply level is not the last, expand again
        if plies > 1:
            for c in self.children:
                c.expand(plies-1)
    
    def updateUtility(self, plies, color):
        if plies == 0 or self.board.is_game_over():
            self.evalBoard()
            return
        else:
            for c in self.children:
                c.updateUtility(plies-1, not color)
        if color: # Plies even = caller root node color player to move = utility of this board is max utility of children
            self.utility, self.bestMove = self.maxChildrenUtility()
        else:
            self.utility, self.bestMove = self.minChildrenUtility()


    def evalBoard(self): # Evaluate own board
        # Control for checkmates
        if self.board.is_checkmate():
            if len(self.board.attackers(chess.WHITE, self.board.king(chess.BLACK))) > 0:
                evaluation = self.maxEval
            else:
                evaluation = -self.maxEval
        # Calculate value function
        evaluation = 0
        pieces = self.board.piece_map()
        for p in pieces.values():
            if p.color == chess.BLACK:
                sign = -1
            else:
                sign = 1
            if p.piece_type == chess.PAWN:
                value = 1
            elif p.piece_type == chess.KNIGHT or p.piece_type == chess.BISHOP:
                value = 3
            elif p.piece_type == chess.ROOK:
                value = 5
            elif p.piece_type == chess.QUEEN:
                value = 9
            elif p.piece_type == chess.KING:
                value = 200
            evaluation = evaluation + sign*value
        # Update own utility value
        self.utility = evaluation

    def expandAndSearch(self, plies):
        print(f"info string ExpandAndSearch reached with {plies} plies")
        self.expand(plies)
        print('info string node expanded')
        self.updateUtility(plies, self.board.turn)
        print('info string utility updated')


