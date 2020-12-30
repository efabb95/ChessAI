import chess
import chess.engine
import positionTables

def modList(l1, l2):
    l1 = [1,2,3]
    l2[:] = [1,2,4]

l1 = [4,5,6]
l2 = [4,5,6]
modList(l1, l2)
print(l1)
print(l2)