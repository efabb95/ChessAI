import chess
import chess.polyglot
import random
import time
import math
import positionTables
import hashExtension
import typing
import transpositionTables as tt
from pathlib import Path
from random import randrange



# TODO: Move search into separate thread
# TODO: study code efficiency
# TODO: Add quiescence search at the last ply of negamax, to correct point evaluation
# TODO: Add minor heuristics to order non-capture moves
# TODO: Find out what is a useful hash size

""" PRINCIPLES (from protocol docs http://wbec-ridderkerk.nl/html/UCIProtocol.html )

- Communication between GUI and engine happens via standard input/iutput with text commands
- The engine boot should be as fast as possible, wait for either 'isready' or 'setoption' to set internal parameters
- Engine must always be able to process input on stdin, even while pondering
- All command strings exchanged end with '\n'
- Engine is always in 'forced' mode, i.e. it should never start calculating or pondering without receiving a "go" command first.
- Before the engine is asked to search on a position, there will always be a position command to tell the engine about the current position.
- By default, opening books are dealt with by the GUI, unless the 'OwnBook' option is used
- If the engine or GUI receives an unknown command it should just ignore it and parse the rest of the string
- If the engine receives commands at the wrong moment (e.g. 'stop' while it is not calculating) it should just ignore them
- move format is in long agebraic notation, examples:
    e2e4
    e1g1    (white short castling)
    a7a8q   (promotion)

"""

class Engine:
    
    def __init__(self):
        self.engineName = 'PunchingBall'
        self.author = 'Michele'
        self.debug = False
        self.maxEval = 100000
        self.root = None
        self.materialScores ={
            chess.PAWN : 100,
            chess.KNIGHT : 320,
            chess.BISHOP : 325,
            chess.ROOK : 500,
            chess.QUEEN : 975,
            chess.KING : 32767
            }
        self.positionTables = positionTables.tables
        self.useOpeningBook = True
        self.bookReader = chess.polyglot.open_reader(Path(__file__).parent / "books/performance.bin")
        self.pLine = []
        self.hashSize = 100000000
        self.tt = [None]*self.hashSize
        self.boardHash = None
        self.errors = 0
        self.tableHits = 0
        self.victimScores = [0, 100, 200, 300, 400, 500, 600]



    def inputUCI(self):
        print(f'id name {self.engineName}')
        print(f'id author {self.author}')
        # TODO: send back 'option' command to tell the GUI which options the engine supports
        print('uciok')
    

    def inputDebug(self, line):
        state = line[6:]  # erase the 'debug ' part of the command
        if state.startswith('on'):
            self.debug = True
        elif state.startswith('off'):
            self.debug = False
        else:
            print(f'info string Received invalid debug command "{line}"')


    def inputIsReady(self):
        # This is called once before the GUI asks to calculate a move the first time.
        # It is also called if the engine is taking time when it is expected to answer, e.g. after setting path to tablebases or other commands that take time
        # It is called to check if the engine is still alive
        print('readyok')
    

    def inputSetOption(self, line):
        # This is called to set the internal options of the engine.
        # It is called once per option with the syntax:
        # "setoption name Style value Risky\n"
        # TODO: implement option setting
        print('info string setoption command is not supported yet')


    def inputRegister(self):
        # This is called to try and register the engine or communicate that registration will be done later (WTF is registration??)
        # TODO: Implement Registration
        print('info string register command is not supported yet')


    def inputUCINewGame(self):
        # This is called if the next search will be from a different game. Next search will be communicated with 'position' and 'go' commands
        # As the engine's reaction to "ucinewgame" can take some time the GUI should always send "isready"
        # after "ucinewgame" to wait for the engine to finish its operation.
        self.board = chess.Board() # board represents the present state of the game
        self.color = chess.WHITE
        self.useOpeningBook = True


    def inputPosition(self, line):
        # The command contains the position the GUI wants to communicate to the engine,
        # in FEN string notation https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation  
        cmd = line[9:]  # Eliminate 'position '
        if cmd.startswith('startpos'):
            self.board = chess.Board()
        elif cmd.startswith('fen'):
            idx = cmd.find('moves')
            self.board = chess.Board(cmd[4:idx-2])
        
        idx = cmd.find('moves')
        if idx >= 0:
            cmd = cmd[idx+6:] # strip 'moves ' from command
            moves = cmd.split(' ')
            for move in moves:
                self.board.push(chess.Move.from_uci(move))

        self.boardHash = chess.polyglot.zobrist_hash(self.board)


    def inputGo(self, command):
        # start calculating on the current position set up with the "position" command. Ideally, do it in another thread,
        # so text can be read while processing and search can be stopped
        # Many options can follow (see docs)
        # TODO: Do it in another thread
        plyDepth = 5
        score, self.bestMove = self.searchPosition(plyDepth)
        print(f'bestmove {self.bestMove}')
        self.pushMove(self.bestMove)
    
    def searchPosition(self, depth):
        if self.useOpeningBook:
            self.useOpeningBook=False
            for entry in self.bookReader.find_all(self.board):
                self.useOpeningBook = True
                break
        for d in range(depth):
            start = time.perf_counter()
            searchInfo = {"Nodes":0}
            score, bestMove = self.negaMaxAlphaBeta(-math.inf, math.inf, d+1, self.useOpeningBook, searchInfo)
            end = time.perf_counter()
            # Send the GUI some info
            if self.board.turn == chess.BLACK:
                score = -score
            print(f'info score cp {score} depth {d+1} time {int((end-start)*1000)} pv {self.getCurrentPVString()} nodes {searchInfo["Nodes"]}, nps {int(searchInfo["Nodes"]/(end-start))}')
        return score, bestMove
        

    def negaMaxAlphaBeta(self, alpha, beta, depth, useOpening, searchInfo):
        # If using opening book
        if useOpening:
            openingMoves = list()
            sumWeight = 0
            for entry in self.bookReader.find_all(self.board):
                openingMoves.append((sumWeight,entry.move))
                sumWeight += entry.weight
            chosenMove = randrange(0, sumWeight)
            i = 1
            openingMovesLen = len(openingMoves)
            while i < openingMovesLen:
                if chosenMove <= openingMoves[i][0]:
                    return [chosenMove, openingMoves[i-1][1]]
            return [chosenMove, openingMoves[openingMovesLen-1][1]]
        # If NOT using opening book
        else:
            bestScore = -math.inf
            bestMove = chess.Move.null()
            if depth == 0 or self.board.is_game_over():
                    score = self.evalBoard()
                    searchInfo["Nodes"] += 1
                    return [score, bestMove]
            searchInfo["Nodes"] += 1
            # Check for draw by repetition here
            oldAlpha = alpha
            legalMoves = list(self.board.legal_moves)
            scores = self.scoreMoves(legalMoves)
            for m in range(len(legalMoves)):
                move = self.pickMove(legalMoves, scores, m)
                self.pushMove(move)
                [score, tempMove] = self.negaMaxAlphaBeta(-beta, -alpha, depth-1, useOpening, searchInfo)
                score = -score
                self.popMove(move)
                if score > bestScore:
                    bestScore = score
                    bestMove = move
                    if score > alpha:
                        if score >= beta:
                            self.tt[self.boardHash%self.hashSize] = tt.Hashentry(self.boardHash, depth, tt.HASH_BETA, score, False, move)
                            return [beta, move]
                        alpha = score
                        bestMove = move
            if alpha != oldAlpha:
                self.tt[self.boardHash%self.hashSize] = tt.Hashentry(self.boardHash, depth, tt.HASH_EXACT, alpha, False, bestMove)
            else:
                self.tt[self.boardHash%self.hashSize] = tt.Hashentry(self.boardHash, depth, tt.HASH_ALPHA, alpha, False, bestMove)
            return [alpha, bestMove]
    
    def scoreMoves(self, moves):
        scores = []
        for move in moves:
            pvLine = self.getCurrentPVLine()
            if pvLine and move == pvLine[0]:
                score = 200000
            elif self.board.is_en_passant(move):
                score = self.victimScores[chess.PAWN] + 6 - (self.victimScores[chess.PAWN]/100)
            elif self.board.is_capture(move):
                score = self.victimScores[self.board.piece_at(move.to_square).piece_type] + 6 - (self.victimScores[self.board.piece_at(move.from_square).piece_type]/100)
            else:
                score = 0                
            scores.append(score)
        return scores

    def pickMove(self, moves, scores, i):
        bestScore = -math.inf
        bestMove = moves[i]
        bestIdx = 0
        for m in range(i, len(moves)):
            if scores[m] > bestScore:
                bestScore = scores[m]
                bestIdx = m
                bestMove = moves[m]
        moves[i], moves[bestIdx] = moves[bestIdx], moves[i]
        scores[i], scores[bestIdx] = scores[bestIdx], scores[i]
        return bestMove

    def getCurrentPVString(self):
        # Returns a string describing the PV Line frome the current state of self.board
        pvLine = self.getCurrentPVLine()
        pvMoves = ''
        if pvLine:
            for m in pvLine:
                pvMoves += ' ' + m.uci()
        return pvMoves

    
    def getCurrentPVLine(self):
        # Returns a list describing the PV Line frome the current state of self.board
        pvLine = []
        revLine = []
        while self.tt[self.boardHash%self.hashSize] and self.tt[self.boardHash%self.hashSize].bestMove != chess.Move.null():
            if self.tt[self.boardHash%self.hashSize].zobrist != self.boardHash:
                print("info string WARNING hash index collision, PVLine lost")
                break
            move = self.tt[self.boardHash%self.hashSize].bestMove
            pvLine.append(move)
            revLine.append(move)
            self.pushMove(move)
        if revLine:
            revLine.reverse()
            for move in revLine:
                self.popMove(move)
        return pvLine
         

    def orderMoves(self, depth, initialDepth):
        pass

    # Evaluate own board, relative to the player to move (Positive is good for evaluating color)
    def evalBoard(self):
        # "State" component
        # if self.board.can_claim_draw():
        #     return 0
        evaluation = 0
        pieces = self.board.piece_map()
        for pSquare in pieces:
            # Material Evaluation
            if pieces[pSquare].color == chess.WHITE:
                evaluation += self.materialScores[pieces[pSquare].piece_type]
            else:
                evaluation -= self.materialScores[pieces[pSquare].piece_type]
            # Position Evaluation
            if pieces[pSquare].piece_type != chess.ROOK and pieces[pSquare].piece_type != chess.QUEEN:
                if pieces[pSquare].color == chess.WHITE:
                    evaluation += self.positionTables[pieces[pSquare].piece_type][pSquare]
                else:
                    evaluation -= self.positionTables[pieces[pSquare].piece_type][pSquare]
        if self.board.is_checkmate():
            if len(self.board.attackers(chess.WHITE, self.board.king(chess.BLACK))) > 0:
                evaluation = evaluation+self.maxEval
            else:
                evaluation = evaluation-self.maxEval
        if self.board.turn == chess.BLACK:
            return -evaluation
        return evaluation

    def pushMove(self, move: chess.Move):
        # pushes move on the self.board AND updates self.boardHash
        self.updateHash(move)
        self.board.push(move)

    def popMove(self, move: chess.Move):
        # pops move from self.board AND updates self.boardHash
        self.board.pop()
        self.updateHash(move)
        

    # Updated the hash zobristKey of the board self.board to reflect the move, without re-hashing the whole board
    def updateHash(self, move: chess.Move):
        # Hash move
        piece_index = (typing.cast(chess.PieceType, self.board.piece_type_at(move.from_square)) - 1) * 2
        if self.board.turn == chess.WHITE:
            piece_index += 1
        self.boardHash ^= hashExtension.POLYGLOT_RANDOM_ARRAY[64*piece_index + move.from_square]
        self.boardHash ^= hashExtension.POLYGLOT_RANDOM_ARRAY[64*piece_index + move.to_square]
        # If king moves by more than 1 square, it's castling -> also hash Rook move
        if (piece_index == 10 or piece_index == 11) and chess.square_distance(move.from_square, move.to_square) > 1:
            if move.to_square == chess.C1: # If Kc1 -> white O-O-O
                piece_index = (chess.ROOK - 1) * 2 + 1
                origin = chess.A1
                destination = chess.D1
            elif move.to_square == chess.G1:   # Kg1
                piece_index = (chess.ROOK - 1) * 2 + 1
                origin = chess.H1
                destination = chess.F1
            elif move.to_square == chess.C8:   # Kc8 -> black O-O-O
                piece_index = (chess.ROOK - 1) * 2
                origin = chess.A8
                destination = chess.D8
            elif move.to_square == chess.G8:    # Kg8
                piece_index = (chess.ROOK - 1) * 2
                origin = chess.H8
                destination = chess.F8
            self.boardHash ^= hashExtension.POLYGLOT_RANDOM_ARRAY[64*piece_index + origin]
            self.boardHash ^= hashExtension.POLYGLOT_RANDOM_ARRAY[64*piece_index + destination]
        # Address promotions
        elif (piece_index == 0 and move.to_square <= chess.H1) or (piece_index == 1 and move.to_square >= chess.A8):
            new_piece_index = (typing.cast(chess.PieceType, move.promotion) - 1) * 2
            if self.board.turn == chess.WHITE:
                new_piece_index += 1
            self.boardHash ^= hashExtension.POLYGLOT_RANDOM_ARRAY[64*piece_index + move.to_square] # Remove Pawn from promotion square
            self.boardHash ^= hashExtension.POLYGLOT_RANDOM_ARRAY[64*new_piece_index + move.to_square] # Add correct piece

        # Compare all changes and store values in a list, so that we can push the move only once
        preCastle = [self.board.has_kingside_castling_rights(chess.WHITE), self.board.has_queenside_castling_rights(chess.WHITE),
        self.board.has_kingside_castling_rights(chess.BLACK), self.board.has_queenside_castling_rights(chess.BLACK)]
        preEp = self.board.ep_square
        self.board.push(move)

        postCastle = [self.board.has_kingside_castling_rights(chess.WHITE), self.board.has_queenside_castling_rights(chess.WHITE),
        self.board.has_kingside_castling_rights(chess.BLACK), self.board.has_queenside_castling_rights(chess.BLACK)]
        postEp = self.board.ep_square
        self.board.pop()

        # Hash en passant square
        if preEp:
            if self.board.turn == chess.WHITE:
                ep_mask = chess.shift_down(chess.BB_SQUARES[self.board.ep_square])
            else:
                ep_mask = chess.shift_up(chess.BB_SQUARES[self.board.ep_square])
            ep_mask = chess.shift_left(ep_mask) | chess.shift_right(ep_mask)

            if ep_mask & self.board.pawns & self.board.occupied_co[self.board.turn]:
               self.boardHash ^= hashExtension.POLYGLOT_RANDOM_ARRAY[772 + chess.square_file(self.board.ep_square)]
        if postEp:
            self.board.push(move)
            if self.board.turn == chess.WHITE:
                ep_mask = chess.shift_down(chess.BB_SQUARES[self.board.ep_square])
            else:
                ep_mask = chess.shift_up(chess.BB_SQUARES[self.board.ep_square])
            ep_mask = chess.shift_left(ep_mask) | chess.shift_right(ep_mask)

            if ep_mask & self.board.pawns & self.board.occupied_co[self.board.turn]:
               self.boardHash ^= hashExtension.POLYGLOT_RANDOM_ARRAY[772 + chess.square_file(self.board.ep_square)]
            self.board.pop()
        # Hash castling
        for i in range(len(preCastle)):
            if preCastle[i] != postCastle[i]:
                self.boardHash ^= hashExtension.POLYGLOT_RANDOM_ARRAY[768+i]
        # Hash captures
        if (self.board.piece_type_at(move.to_square)):
            piece_index = (typing.cast(chess.PieceType, self.board.piece_type_at(move.to_square)) - 1) * 2
            if self.board.turn == chess.BLACK:
                piece_index += 1
            self.boardHash ^= hashExtension.POLYGLOT_RANDOM_ARRAY[64*piece_index + move.to_square]
        # Hash turn
        self.boardHash ^= hashExtension.POLYGLOT_RANDOM_ARRAY[780]
        
        # finally pop the move to go back to normal state
        


    # Starts the UCI protocol loop to communicate with a chess GUI
    def protocolLoop(self):
        # This method gets called when the message 'uci' is received
        while(True):
            nextLine = input()
            if nextLine == 'uci':
                self.inputUCI()
            elif nextLine.startswith("debug"):
                self.inputDebug(nextLine)
            elif nextLine == 'isready':
                self.inputIsReady()
            elif nextLine.startswith('setoption'):
                self.inputSetOption(nextLine)
            elif nextLine.startswith('register'):
                self.inputRegister()
            elif nextLine == "ucinewgame":
                self.inputUCINewGame()
            elif nextLine.startswith("position"):
                self.inputPosition(nextLine)
            elif nextLine.startswith("go"):
                self.inputGo(nextLine)
            else:
                print(f"Unrecognized command '{nextLine}'")


def main():
    engine = Engine()
    engine.protocolLoop()


if __name__ == "__main__":
    main()
