import numpy as np
from numba import njit

L = 5
D = 10

def codes():
    g = np.indices(
        (D,) * L,
        dtype=np.uint8
    )
    return g.reshape(L, -1).T

ALL = codes()

# ----------------

@njit(cache=True)
def fb(g, s):
    b = 0
    gc = np.zeros(D, np.uint8)
    sc = np.zeros(D, np.uint8)

    for i in range(L):
        a = g[i]
        c = s[i]

        if a == c:
            b += 1

        gc[a] += 1
        sc[c] += 1

    com = 0
    for i in range(D):
        com += min(gc[i], sc[i])

    return b * 10 + (com - b)

"""
if sc[i] > gc[i] and gc[i] != 0:
    com += sc[i]
else:
    com += min(gc[i], sc[i])
"""
# ----------------

@njit(cache=True)
def score_guess(guess, candidates, bound):
    groups = np.zeros(60, np.int32)
    worst = 0

    for i in range(len(candidates)):
        f = fb(guess, candidates[i])
        groups[f] += 1

        if groups[f] > worst:
            worst = groups[f]
            
            # Budama (Pruning) işlemi orijinalindeki gibi
            if worst >= bound:
                return 999999

    return worst

# ----------------

@njit(cache=True)
def minimax_numba(search, candidates):
    best = 10**9
    best_idx = 0

    for i in range(len(search)):
        # score_guess çağrısı artık doğrudan C seviyesinde çalışıyor
        s = score_guess(search[i], candidates, best)

        if s < best:
            best = s
            best_idx = i

    return search[best_idx]

def minimax(candidates):
    if len(candidates) > 3000:
        idx = np.random.choice(
            len(ALL),
            3000,
            replace=False
        )
        search = ALL[idx]
    else:
        search = ALL

    # Ağır yük Numba fonksiyonuna devredildi
    return minimax_numba(search, candidates)

# ----------------

@njit(cache=True)
def reduce(cand, guess, result):
    # Liste yerine maksimum uzunlukta dizi ayırarak belleği optimize ediyoruz
    keep = np.empty(len(cand), np.int32)
    count = 0

    for i in range(len(cand)):
        if fb(guess, cand[i]) == result:
            keep[count] = i
            count += 1

    # Sadece dolu olan kısmı geri döndürüyoruz
    return keep[:count]

# ----------------

def solve(secret):
    cand = ALL

    guess = np.array([0, 1, 2, 3, 4], np.uint8)

    t = 0

    while True:
        t += 1

        result = fb(guess, secret)
        b = result // 10
        w = result % 10

        # once filtrele, kalan aday sayisini al
        idx = reduce(cand, guess, result)
        cand = cand[idx]

        # oynanan tahmin + onun skoru + bu hamleden sonra kalan aday
        print(f"Adim: {t} | Tahmin: {guess} | siyah,beyaz: {b},{w} | Kalan Aday: {len(cand)}")

        if result == 50:
            return t

        if len(cand) == 1:
            guess = cand[0]
        else:
            guess = minimax(cand)
        
# test

if __name__ == "__main__":

    import time

    for i in range(100):
        print(f"\nTest {i+1}/100")
        secret = np.random.choice(D, L, replace=True).astype(np.uint8)
        print(f"Adim: 0 | Gizli : {secret}                    | kalan aday: 100000")
        start = time.time(); print(f"\nToplam Deneme: {solve(secret)} | Süre: {time.time()-start:.4f}s")
        print()

