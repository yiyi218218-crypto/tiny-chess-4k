import json, os, random, sys, time, urllib.request as U

ENV = os.environ["MAKEFUN_ENV_URL"]
G0 = time.time()
TL = 1.2
OFF = 1
V = [0, 0, 100, 320, 330, 500, 900, 0]
ORTH = (-10, -1, 1, 10)
DIAG = (-11, -9, 9, 11)
KN = (-21, -19, -12, -8, 8, 12, 19, 21)
D = [(), (), (), KN, DIAG, ORTH, ORTH + DIAG, ORTH + DIAG]

# piece-square tables, built once: index by piece type, white point of view
A = [0, 0, 0, 36, 28, 12, 12, 0]
B = [0, 0, 0, 4, 2, 1, 2, 0]
P = [None] * 8
for _t in range(2, 8):
    _a = [0] * 120
    for _f in range(21, 99):
        if _f % 10 in (0, 9):
            continue
        _r = _f // 10 - 2
        _c = _f % 10 - 1
        _d = abs(2 * _r - 7) + abs(2 * _c - 7)
        if _t == 2:
            _a[_f] = (7 - _r) * 10 + (12 if _c in (3, 4) else 0) - 8
        elif _t == 7:
            _a[_f] = (_d - 7) * 6
        else:
            _a[_f] = (A[_t] - B[_t] * _d) // 2
    P[_t] = _a

_r = random.Random(20261118)
Z = [[_r.getrandbits(64) for _ in range(120)] for _ in range(16)]
KS = _r.getrandbits(64)

M = {"p": 10, "n": 11, "b": 12, "r": 13, "q": 14, "k": 15,
     "P": 2, "N": 3, "B": 4, "R": 5, "Q": 6, "K": 7}
S = 0
H = 0
K = [0, 0]
CR = 0
NODES = 0
T0 = 0.0
TT = {}
HS = {}
KL = [[0, 0] for _ in range(128)]


def pv(p, i):
    q = p % 8
    if p < 8:
        return V[q] + P[q][i]
    return -V[q] - P[q][(11 - i // 10) * 10 + i % 10]


def bd(fen):
    global S, H, K, CR
    b = [OFF] * 120
    for i in range(21, 99):
        if i % 10 not in (0, 9):
            b[i] = 0
    for r, row in enumerate(fen.split()[0].split("/")):
        f = 0
        for ch in row:
            if ch.isdigit():
                f += int(ch)
            else:
                b[21 + r * 10 + f] = M[ch]
                f += 1
    fl = fen.split()
    CR = 0
    if len(fl) > 2:
        for i, c in enumerate("KQkq"):
            if c in fl[2]:
                CR |= 1 << i
    S = H = 0
    K = [0, 0]
    for i in range(21, 99):
        p = b[i]
        if p > 1:
            S += pv(p, i)
            H ^= Z[p][i]
            if p % 8 == 7:
                K[p > 8] = i
    return b


def gen(b, side):
    out = []
    w = bool(side)
    for f in range(21, 99):
        p = b[f]
        if p < 2 or (p < 8) != w:
            continue
        t = p % 8
        if t == 2:
            d = -10 if w else 10
            o = f + d
            v = b[o]
            if v == 0:
                if o < 31 or o > 88:
                    out.append((f, o, 6 if w else 14))
                else:
                    out.append((f, o, 0))
                    o2 = o + d
                    if (f > 80 if w else f < 39) and b[o2] == 0:
                        out.append((f, o2, 0))
            for c in (d - 1, d + 1):
                q = f + c
                v = b[q]
                if v > 1 and (v < 8) != w:
                    if q < 31 or q > 88:
                        out.append((f, q, 6 if w else 14))
                    else:
                        out.append((f, q, 0))
        else:
            for d in D[t]:
                q = f + d
                while True:
                    v = b[q]
                    if v == OFF:
                        break
                    if v == 0:
                        out.append((f, q, 0))
                    else:
                        if (v < 8) != w:
                            out.append((f, q, 0))
                        break
                    if t in (3, 7):
                        break
                    q += d
    if w:
        if CR & 1 and b[95] == 7 and b[98] == 5 and not b[96] and not b[97] and not hit(b, 95, 0) and not hit(b, 96, 0):
            out.append((95, 97, 1))
        if CR & 2 and b[95] == 7 and b[91] == 5 and not b[94] and not b[93] and not b[92] and not hit(b, 95, 0) and not hit(b, 94, 0):
            out.append((95, 93, 2))
    else:
        if CR & 4 and b[25] == 15 and b[28] == 13 and not b[26] and not b[27] and not hit(b, 25, 1) and not hit(b, 26, 1):
            out.append((25, 27, 1))
        if CR & 8 and b[25] == 15 and b[21] == 13 and not b[24] and not b[23] and not b[22] and not hit(b, 25, 1) and not hit(b, 24, 1):
            out.append((25, 23, 2))
    return out


def hit(b, s, w):
    for c in ((9, 11) if w else (-9, -11)):
        v = b[s + c]
        if v > 1 and v % 8 == 2 and (v < 8) == w:
            return 1
    for c in KN:
        v = b[s + c]
        if v > 1 and v % 8 == 3 and (v < 8) == w:
            return 1
    for c in ORTH + DIAG:
        v = b[s + c]
        if v > 1 and v % 8 == 7 and (v < 8) == w:
            return 1
    for c in ORTH + DIAG:
        q = s + c
        while True:
            v = b[q]
            if v == OFF:
                break
            if v:
                if (v < 8) == w:
                    t = v % 8
                    if t == 6 or (t == 5 and c in ORTH) or (t == 4 and c in DIAG):
                        return 1
                break
            q += c
    return 0


def mk(b, mv):
    global S, H
    f, t, pr = mv
    p = b[f]
    cap = b[t]
    so = S
    ho = H
    S -= pv(p, f)
    H ^= Z[p][f]
    if cap:
        S -= pv(cap, t)
        H ^= Z[cap][t]
    if pr < 3:
        if pr:
            if pr == 1:
                rk = t + 1
                rd = t - 1
            else:
                rk = t - 2
                rd = t + 1
            r = b[rk]
            S += pv(r, rd) - pv(r, rk)
            H ^= Z[r][rk] ^ Z[r][rd]
            b[rd] = r
            b[rk] = 0
        b[t] = p
    else:
        b[t] = pr
    S += pv(b[t], t)
    H ^= Z[b[t]][t] ^ KS
    b[f] = 0
    if p % 8 == 7:
        K[p > 8] = t
    return (cap, p, so, ho)


def um(b, mv, u):
    global S, H
    f, t, pr = mv
    p = u[1]
    b[f] = p
    b[t] = u[0]
    if 0 < pr < 3:
        if pr == 1:
            b[t + 1] = b[t - 1]
            b[t - 1] = 0
        else:
            b[t - 2] = b[t + 1]
            b[t + 1] = 0
    S = u[2]
    H = u[3]
    if p % 8 == 7:
        K[p > 8] = f


def ok(m, b, bm, ply):
    if m == bm:
        return 1 << 30
    if m[2] > 2:
        return 1 << 29
    v = b[m[1]]
    if v:
        return (1 << 28) + V[v % 8] * 8 - V[b[m[0]] % 8]
    if m in KL[ply]:
        return 1 << 27
    return HS.get(m, 0)


def qs(b, side, a, be, d=5):
    global NODES
    NODES += 1
    if not NODES & 1023 and time.time() - T0 > TL:
        raise TimeoutError
    chk = hit(b, K[not side], not side)
    if not chk:
        st = S if side else -S
        if st >= be:
            return be
        if st > a:
            a = st
        if d <= 0:
            return a
    ms = gen(b, side)
    ms.sort(key=lambda m: ok(m, b, 0, 0), reverse=True)
    best = -30000
    n = 0
    for mv in ms:
        if not chk and not b[mv[1]] and mv[2] < 3:
            continue
        u = mk(b, mv)
        if hit(b, K[not side], not side):
            um(b, mv, u)
            continue
        n += 1
        s = -qs(b, 1 - side, -be, -a, d - 1)
        um(b, mv, u)
        if s > best:
            best = s
        if s > a:
            a = s
        if a >= be:
            return be
    if chk:
        return best if n else -29000
    return a


def sr(b, side, d, a, be, h, ply):
    global NODES
    NODES += 1
    if not NODES & 1023 and time.time() - T0 > TL:
        raise TimeoutError
    if d <= 0:
        return qs(b, side, a, be)
    e = TT.get(h)
    bm = 0
    if e:
        bm = e[3]
        if e[0] >= d:
            if e[2] == 0:
                return e[1]
            if e[2] == 1:
                if e[1] <= a:
                    return a
            elif e[1] >= be:
                return be
    a0 = a
    ms = gen(b, side)
    ms.sort(key=lambda m: ok(m, b, bm, ply), reverse=True)
    best = -30000
    bmov = 0
    for mv in ms:
        u = mk(b, mv)
        if hit(b, K[not side], not side):
            um(b, mv, u)
            continue
        if bmov:
            s = -sr(b, 1 - side, d - 1, -a - 1, -a, H, ply + 1)
            if a < s < be:
                s = -sr(b, 1 - side, d - 1, -be, -a, H, ply + 1)
        else:
            s = -sr(b, 1 - side, d - 1, -be, -a, H, ply + 1)
        um(b, mv, u)
        if s > best:
            best = s
            bmov = mv
        if s > a:
            a = s
        if a >= be:
            if not b[mv[1]] and mv[2] < 3:
                KL[ply][1] = KL[ply][0]
                KL[ply][0] = mv
                HS[mv] = HS.get(mv, 0) + d * d
            break
    if not bmov:
        return -29000 + ply
    if best >= be:
        TT[h] = (d, best, 2, bmov)
    elif best > a0:
        TT[h] = (d, best, 0, bmov)
    else:
        TT[h] = (d, best, 1, bmov)
    return best


def pick(b, side):
    global T0
    T0 = time.time()
    if len(TT) > 300000:
        TT.clear()
    ms = gen(b, side)
    best = 0
    d = 0
    try:
        while d < 64:
            d += 1
            a = -30000
            cur = 0
            for mv in ms:
                u = mk(b, mv)
                if hit(b, K[not side], not side):
                    um(b, mv, u)
                    continue
                s = -sr(b, 1 - side, d - 1, -30000, -a, H, 1)
                um(b, mv, u)
                if s > a:
                    a = s
                    cur = mv
            if not cur:
                break
            best = cur
            ms.remove(cur)
            ms.insert(0, cur)
            if a > 28000 or time.time() - T0 > TL * 0.4:
                break
    except TimeoutError:
        pass
    return best or ms[0]


def uci(mv):
    f, t, pr = mv
    return (chr(96 + f % 10) + str(10 - f // 10) + chr(96 + t % 10) + str(10 - t // 10)
            + ("q" if pr > 2 else ""))


def post(path, body):
    r = U.Request(ENV + path, json.dumps(body).encode(), {"content-type": "application/json"})
    return json.load(U.urlopen(r))


def run():
    g = post("/game", {})
    while g.get("status") != "done":
        if g.get("status") == "your_move":
            b = bd(g["fen"])
            side = 1 if g["colour"] == "white" else 0
            lg = g["legal_moves"]
            s = uci(pick(b, side))
            if s not in lg:
                sys.stderr.write("ILLEGAL %s\n" % s)
                s = lg[0]
            g = post("/move", {"game": g["game"], "move": s})
        else:
            g = post("/game", {})


if __name__ == "__main__":
    run()
