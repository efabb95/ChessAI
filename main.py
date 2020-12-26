import chess
import random

def inputUCI():
    print("id name PunchingBall")
    print("id author Giovanna Brava")
    # Modify Options HERE
    print("uciok")
    board = chess.Board()
    return board


def inputIsReady():
    print("readyok")


def inputSetOptions(options):
    # Set engine options according to GUI orders
    pass


def inputUCINewGame():
    board = chess.Board()
    return board

def inputPosition(position, board):
    last_move = position.split(" ")[-1]
    board.push(chess.Move.from_uci(last_move))
    print(f'Position command received: "{position}"')


def inputGo(board):
    moves = list(board.generate_legal_moves())
    move = random.choice(moves)
    print(f"bestmove {move}")
    board.push(move)
    # Search for best move. Ideally, do it in another thread,
    # so text can be read while processing and search can be stopped


def main():
    while(True):
        nextLine = input()
        if nextLine == "uci":
            board = inputUCI()
        elif nextLine == "isready":
            inputIsReady()
        elif nextLine.startswith("go"):
            inputGo(board)
        elif nextLine == "ucinewgame":
            board = inputUCINewGame()
        elif nextLine.startswith("setoption"):
            inputSetOptions(nextLine)
        elif nextLine.startswith("position"):
            inputPosition(nextLine, board)
        else:
            print(f"Unrecognized command '{nextLine}'")


if __name__ == "__main__":
    main()
