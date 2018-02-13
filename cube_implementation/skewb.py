from .perm import P

R = P.from_cycles([
    [10, 15, 25],
    [12, 19, 29],
    [13, 16, 26],
    [14, 18, 27],
    [ 2, 23,  9]
])

U = P.from_cycles([
    [ 0, 20, 15],
    [ 1, 21, 17],
    [ 2, 22, 19],
    [ 3, 23, 16],
    [ 6, 26, 12]
])

L = P.from_cycles([
    [ 5, 25, 20],
    [ 6, 29, 23],
    [ 8, 28, 24],
    [ 9, 26, 22],
    [ 3, 13, 19]
])

B = P.from_cycles([
    [15, 20, 25],
    [17, 24, 27],
    [18, 21, 28],
    [19, 23, 26],
    [ 1,  8, 14]
])

def bfs():
    i = 0
    Turns = [R, U, L, B, R ** -1, U ** -1, L ** -1, B ** -1]
    visited = set()
    from queue import Queue
    q = Queue()
    q.put(P(dict()))
    while not q.empty():
        state = q.get()
        if state in visited:
            continue
        visited.add(state)
        i += 1
        if i % 10000 == 0:
            print("{:.2%}".format(len(visited)/2457600))
        for t in Turns:
            q.put(state @ t)
