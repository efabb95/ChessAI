moves = ["e7e5", "d7d6", "g8f6", "b8c6"]


def inputUCI():
    print("id name PunchingBall")
    print("id author Giovanna Brava")
    # Modify Options HERE
    print("uciok")


def inputIsReady():
    print("readyok")


def inputSetOptions(options):
    # Set engine options according to GUI orders
    pass


def inputUCINewGame():
    # If needed, refresh engine before new game
    pass


def inputPosition(position):
    position = position[9:]
    print(f'Position command received: "{position}"')


def inputGo(m):
    print(f"bestmove {moves[m]}")
    # Search for best move. Ideally, do it in another thread,
    # so text can be read while processing and search can be stopped


def main():
    m = 0
    while(True):
        nextLine = input()
        if nextLine == "uci":
            inputUCI()
        elif nextLine == "isready":
            inputIsReady()
        elif nextLine.startswith("go"):
            inputGo(m)
            m = m+1
        elif nextLine == "ucinewgame":
            inputUCINewGame()
        elif nextLine.startswith("setoption"):
            inputSetOptions(nextLine)
        elif nextLine.startswith("position"):
            inputPosition(nextLine)
        else:
            print(f"Unrecognized command '{nextLine}'")


if __name__ == "__main__":
    main()
