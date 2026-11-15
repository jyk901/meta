# data.json 생성 스크립트 (재현용)
import json, random
from main import make_cross, make_x

random.seed(3)
def noisy(m, k):
    n = len(m); m = [r[:] for r in m]
    for _ in range(k):
        i, j = random.randrange(n), random.randrange(n)
        m[i][j] = 1 - m[i][j]
    return m

data = {"filters": {}, "patterns": {}}
labels = [("+", make_cross), ("x", make_x)]
for n in (5, 13, 25):
    data["filters"]["size_%d" % n] = {"cross": make_cross(n), "x": make_x(n)}
    idx = 1
    for lab, mk in labels:
        for noise in (0, 1 if n == 5 else 2):
            data["patterns"]["size_%d_%d" % (n, idx)] = {
                "input": noisy(mk(n), noise), "expected": lab if idx % 2 else ("Cross" if lab == "+" else "x")}
            idx += 1
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f)
