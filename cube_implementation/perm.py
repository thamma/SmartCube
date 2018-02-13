import math
import functools

class P:
    def __init__(self, d):
        self.d = {i: d[i] for i in sorted(d)}
        self._cached_hash = hash(tuple(self.d.items()))
        self._cached_order = None

    @classmethod
    def from_cycles(cls, cycles):
        d = dict()
        for cycle in cycles:
            k = len(cycle)
            for i in range(k):
                if cycle[i] in d:
                    raise ValueError("{} is already mapped".format(cycle[i]))
                d[cycle[i]] = cycle[(i+1) % k]
        return cls({i: d[i] for i in d if d[i] != i})

    def __repr__(self):
        return "{}.from_cycles({})".format(self.__class__.__name__, self.cycles())

    def __mul__(self, other):
        return P({i: self[other[i]] for i in set(self) | set(other) if self[other[i]] != i})

    def __matmul__(self, other):
        return other * self

    def __pow__(self, other):
        if other < 0:
            return self ** ((self.order() + other) % self.order())
        else:
            res = P(dict())
            b = self
            exp = other
            while exp > 0:
                if exp % 2 == 1:
                    res *= b
                    exp -= 1
                else:
                    b *= b
                    exp /= 2
            return res

    def order(self):
        if self._cached_order is None:
            cycles = (len(cycle) for cycle in self.cycles())
            self._cached_order = functools.reduce(lambda a, b: a * b // math.gcd(a, b), cycles, 1)
        return self._cached_order

    def __getitem__(self, key):
        return self.d.get(key, key)

    def __iter__(self):
        return self.d.__iter__()

    def __contains__(self, item):
        return item in self.d

    def __eq__(self, other):
        for i in set(self) | set(other):
            if self[i] != other[i]:
                return False
        return True

    def __hash__(self):
        return self._cached_hash

    def cycles(self):
        res = []
        done = {i: False for i in self}
        for i in self:
            if done[i]:
                continue
            done[i] = True
            res.append([i])
            t = i
            while self[t] != i:
                t = self[t]
                res[-1].append(t)
                done[t] = True
        return res
