HASH_EXACT = 1
HASH_BETA = 2
HASH_ALPHA = 3

class Hashentry:
    def __init__(self, zobrist, depth, flag, score, ancient, bestMove):
        self.zobrist = zobrist
        self.depth = depth
        self.flag = flag
        self.score = score
        self.ancient = ancient
        self.bestMove = bestMove

