import chess
import random
import time

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
        self.engineName = 'Random Mover'
        self.author = 'Giovanna Brava'
        self.debug = False

    def eval(self):
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
        if self.color == chess.BLACK:
            return -evaluation
        return evaluation


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


    def inputPosition(self, line):
        # The command contains the position the GUI wants to communicate to the engine,
        # in FEN string notation https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation
        
        cmd = line[9:]  # Eliminate 'position '
        if cmd.startswith('startpos'):
            self.board = chess.Board()
        else:
            # TODO: read FEN and set up board
            print('info string Starting from non-standard starting position is not supported yet')
        
        idx = cmd.find('moves')
        if idx >= 0:
            cmd = cmd[idx+6:] # strip 'moves ' from command
            moves = cmd.split(' ')
            if len(moves)%2 == 0:
                self.color = chess.WHITE
            else:
                self.color = chess.BLACK
            for move in moves:
                self.board.push(chess.Move.from_uci(move))


    def inputGo(self, line):
        # start calculating on the current position set up with the "position" command. Ideally, do it in another thread,
        # so text can be read while processing and search can be stopped
        # Many options can follow (see docs)
        # TODO: Do it in another thread
        # TODO: Implement real calculation
        legalMoves = list(self.board.generate_legal_moves())
        if len(legalMoves) == 0:
            print('info string No legal moves found. Quitting')
            quit()
        bestMove = random.choice(legalMoves)
        time.sleep(0.5)
        print(f'bestmove {bestMove}')
        self.board.push(bestMove)


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
