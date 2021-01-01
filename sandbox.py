import chess
import chess.engine, chess.polyglot
import positionTables
import typing
import hashExtension

b = chess.Board('rnb2bnr/p1q1k1pp/1ppp1p2/4p3/4P3/BPN2NPB/P1PPQP1P/R3K2R w KQ - 1 8')
hash1 = chess.polyglot.zobrist_hash(b)
move = chess.Move.from_uci('e1g1')


piece_index = (typing.cast(chess.PieceType, b.piece_type_at(move.from_square)) - 1) * 2
if b.turn == chess.WHITE:
    piece_index += 1
myhash = hash1 ^ hashExtension.POLYGLOT_RANDOM_ARRAY[64*piece_index + move.from_square]
myhash ^= hashExtension.POLYGLOT_RANDOM_ARRAY[64*piece_index + move.to_square]

move = chess.Move.from_uci('h1f1')
piece_index = (typing.cast(chess.PieceType, b.piece_type_at(move.from_square)) - 1) * 2
if b.turn == chess.WHITE:
    piece_index += 1
myhash = hash1 ^ hashExtension.POLYGLOT_RANDOM_ARRAY[64*piece_index + move.from_square]
myhash ^= hashExtension.POLYGLOT_RANDOM_ARRAY[64*piece_index + move.to_square]

myhash ^= hashExtension.POLYGLOT_RANDOM_ARRAY[780]
myhash ^= hashExtension.POLYGLOT_RANDOM_ARRAY[768]


b.push(move)
realHash = chess.polyglot.zobrist_hash(b)

print(f'pre\t{hash1}\nReal\t{realHash}\nmine\t{myhash}')

"""
piece_index = [0:11]. Odd -> white, even -> black
6 rook
2 knight
4 bishop
10 king
8 queen
0 pawn
"""