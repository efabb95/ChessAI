import chess
import chess.engine

board = chess.Board()

mvs = board.generate_legal_moves()
for i in mvs:
    print(i)
