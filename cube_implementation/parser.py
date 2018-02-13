from . import cube
import operator
import functools

def parse_sequence(s):
    s = s.upper()
    o = []
    while len(s) > 0:
        if s[0].isspace():
            continue
        elif s[0] in "UDLRFBMESXYZ":
            o.append(getattr(cube, s[0]))
        elif s[0] == "'":
            o[-1] **= -1
        else:
            raise ValueError("Invalid input {}".format(s[0]))
        s = s[1:]
    return o

def parse_alg(s):
    o = parse_sequence(s)
    return functools.reduce(operator.matmul, o)
