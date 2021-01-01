import chess
import chess.engine, chess.polyglot
import positionTables
import typing
import hashExtension

b = chess.Board('rnb2bnr/p1q1k1pp/1ppp1p2/4p3/4P3/BPN2NPB/P1PPQP1P/R3K2R w KQ - 1 8')
hash1 = chess.polyglot.zobrist_hash(b)
move = chess.Move.from_uci('e1g1')


print(b.piece_map())
pieces = b.piece_map()

for s in pieces:
    print(f'piece {pieces[s].piece_type} at square {s}')
"""
piece_index = [0:11]. Odd -> white, even -> black
6 rook
2 knight
4 bishop
10 king
8 queen
0 pawn
"""