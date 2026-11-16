import numpy as np
from numba import njit
from multiprocessing import Pool
from collections import Counter
import math

KOD_UZUNLUGU = 5
MAKS_SAYI = 10

# --------------------------------------------------
# KOD HAVUZU
# --------------------------------------------------

def tum_kodlar():

    grids = np.indices(
        [MAKS_SAYI]*KOD_UZUNLUGU,
        dtype=np.uint8
    )

    return grids.reshape(
        KOD_UZUNLUGU,
        -1
    ).T


# --------------------------------------------------
# FEEDBACK
# --------------------------------------------------

@njit(cache=True)
def feedback(tahmin, gizli):

    siyah = 0

    tc = np.zeros(
        MAKS_SAYI,
        dtype=np.uint8
    )

    gc = np.zeros(
        MAKS_SAYI,
        dtype=np.uint8
    )

    for i in range(KOD_UZUNLUGU):

        a = tahmin[i]
        b = gizli[i]

        if a == b:
            siyah += 1

        tc[a] += 1
        gc[b] += 1

    ortak = 0

    for i in range(MAKS_SAYI):

        ortak += min(
            tc[i],
            gc[i]
        )

    return siyah, ortak - siyah


# --------------------------------------------------
# FILTER
# --------------------------------------------------

@njit(cache=True)
def filtre(adaylar, tahmin, siyah, beyaz):

    out = []

    for i in range(len(adaylar)):

        s, b = feedback(
            tahmin,
            adaylar[i]
        )

        if s == siyah and b == beyaz:
            out.append(i)

    return np.array(
        out,
        dtype=np.int32
    )


# --------------------------------------------------
# ENTROPY
# --------------------------------------------------

def entropy_score(args):

    guess, adaylar = args

    counts = {}

    for g in adaylar:

        r = feedback(
            guess,
            g
        )

        counts[r] = counts.get(
            r,
            0
        ) + 1

    total = len(adaylar)

    e = 0

    for c in counts.values():

        p = c / total

        e -= p * math.log2(p)

    return e


# --------------------------------------------------
# EN IYI TAHMIN
# --------------------------------------------------

def en_iyi_tahmin(adaylar):

    sample = adaylar

    if len(sample) > 5000:

        idx = np.random.choice(
            len(sample),
            5000,
            replace=False
        )

        sample = sample[idx]

    with Pool() as p:

        scores = p.map(
            entropy_score,
            [
                (g, adaylar)
                for g in sample
            ]
        )

    return sample[
        np.argmax(scores)
    ]


# --------------------------------------------------
# SOLVER
# --------------------------------------------------

def coz(gizli):

    havuz = tum_kodlar()

    adaylar = havuz

    tahmin = np.array(
        [1,1,2,2,3],
        dtype=np.uint8
    )

    deneme = 0

    while True:

        deneme += 1

        siyah, beyaz = feedback(
            tahmin,
            gizli
        )

        print(
            f"{deneme}:",
            tahmin,
            "→",
            siyah,
            beyaz
        )

        if siyah == KOD_UZUNLUGU:

            print(
                "\nBulundu",
                deneme
            )

            return deneme

        idx = filtre(
            adaylar,
            tahmin,
            siyah,
            beyaz
        )

        adaylar = adaylar[
            idx
        ]

        tahmin = en_iyi_tahmin(
            adaylar
        )


# --------------------------------------------------

if __name__ == "__main__":

    gizli = np.array(
        [7,3,9,2,5],
        dtype=np.uint8
    )

    coz(gizli)