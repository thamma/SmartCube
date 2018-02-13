from collections import deque

class PinTracker:
    def __init__(self, turn, turn_inv, max_val=1023, bounce_threshold=100):
        self.turn = turn
        self.turn_inv = turn_inv
        self.previous_values  = deque([0 for _ in range(10)])
        self.previous_indices = deque([0 for _ in range(10)])
        self.last_state = 0
        self.max_val = max_val
        self.bounce_threshold = bounce_threshold
        self.states = [0.25 * i * self.max_val for i in [1, 2, 3, 4]]

    def update(self, value):
        self.previous_values.appendleft(value)
        self.previous_values.pop()

        max_diff = max(self.previous_values) - min(self.previous_values)
        if max_diff > self.bounce_threshold:
            value = self.max_val

        current_index = 0
        while value > self.states[current_index]:
            current_index += 1

        self.previous_indices.appendleft(current_index)
        self.previous_indices.pop()

        result = None

        if len(set(self.previous_indices)) == 1:
            d = (current_index - self.last_state) % 4
            if d != 0:
                result = {1: self.turn, 2: None, 3: self.turn_inv}[d]
                self.last_state = current_index

        return result

#trackers = [PinTracker(s) for s in "udlrfb"]
trackers = [
    PinTracker("F'", "F" ), # f'
    PinTracker("D",  "D'"),
    PinTracker("L'", "L" ),
    PinTracker("U'", "U" ), # u'
    PinTracker("B'", "B" ), # b'
    PinTracker("R'", "R" ), # r'
]

while True:
    s = input()
    if "0x000e" not in s:
        continue
    bytevals = s.split("0x000e value: ")[1].split()
    vals = [int(bytevals[(2*i)+1] + bytevals[2*i], 16) for i in range(6)]
    # print(vals)
    for i in range(6):
        turn = trackers[i].update(vals[i])
        if turn:
            print(turn)

