def tum_kodlari_uret():
    """
    1-6 arası rakamlardan oluşan tüm 4 haneli kodları üretir.
    Kütüphane kullanmadan iç içe döngüyle yapılır.
    Döndürür: list of tuple, örn. [(1,1,1,1), (1,1,1,2), ..., (6,6,6,6)]
    """
    kodlar = []
    for a in range(1, 7):
        for b in range(1, 7):
            for c in range(1, 7):
                for d in range(1, 7):
                    kodlar.append((a, b, c, d))
    return kodlar


# Tüm 1296 kodu global olarak bir kez üretiyoruz.
TUM_KODLAR = tum_kodlari_uret()


# -----------------------------------------------------------------------------
# ADIM 2: Skor hesaplama
# -----------------------------------------------------------------------------
# Bir tahmin yapıldığında gizli kodla karşılaştırılır.
# Hesaplama iki aşamada yapılmak zorundadır:
#   1) Önce siyahlar bulunur (doğru yer, doğru rakam).
#      Bulunan pozisyonlar işaretlenerek beyaz hesabına dahil edilmez.
#   2) Sonra beyazlar: kalan rakamlarda her haneden kaç tane eşleşiyor?
#
# Neden min() kullanıyoruz?
#   Gizli: (1,1,3,4), Tahmin: (1,1,1,5)
#   Pozisyon 0 ve 1'de siyah var, pozisyon 2'deki "1" için:
#     gizli'de kalan 1 sayısı: 0 (hepsi siyah olarak işaretlendi)
#     tahminde kalan 1 sayısı: 1
#     min(0, 1) = 0 → beyaz yok. Doğru.

def skor_hesapla(gizli, tahmin):
    """
    Gizli kodu tahminle karşılaştırır, (siyah, beyaz) döndürür.

    Parametreler:
        gizli  : tuple, örn. (4, 3, 5, 3)
        tahmin : tuple, örn. (1, 1, 2, 2)

    Döndürür:
        (siyah, beyaz) tuple
            siyah: doğru rakam, doğru pozisyon sayısı
            beyaz: doğru rakam, yanlış pozisyon sayısı
    """
    siyah = 0
    # Siyah hesabı için kopyalar üzerinde çalışıyoruz ki orijinaller bozulmasın
    gizli_kalan = list(gizli)
    tahmin_kalan = list(tahmin)

    # Aşama 1: Siyahları bul, işaretlenmiş pozisyonları -1 yap
    for i in range(4):
        if gizli_kalan[i] == tahmin_kalan[i]:
            siyah += 1
            gizli_kalan[i] = -1   # Bu pozisyon artık beyaz hesabına girmeyecek
            tahmin_kalan[i] = -1

    # Aşama 2: Beyazları bul
    # Her rakam için: gizli'de kaç tane kaldı vs. tahminde kaç tane kaldı → min al
    beyaz = 0
    for rakam in range(1, 7):
        beyaz += min(gizli_kalan.count(rakam), tahmin_kalan.count(rakam))

    return (siyah, beyaz)


# -----------------------------------------------------------------------------
# ADIM 3: Aday filtreleme
# -----------------------------------------------------------------------------
# Bir tahmin yapıp skorunu aldıktan sonra, o skorla tutarsız olan tüm adayları
# havuzdan çıkarırız.
#
# Mantık: Eğer gizli kod X olsaydı ve biz Y tahminini yapsaydık,
# aldığımız skor Z olurdu. Gerçekte aldığımız skor Z' ise ve Z ≠ Z' ise,
# X gizli kod olamaz → X'i listeden çıkar.

def adaylari_filtrele(adaylar, tahmin, alinan_skor):
    """
    Tahmin ve alınan skorla tutarsız adayları listeden çıkarır.

    Parametreler:
        adaylar    : list of tuple, mevcut aday listesi
        tahmin     : tuple, yapılan tahmin
        alinan_skor: (siyah, beyaz) tuple, gerçekte alınan skor

    Döndürür:
        Tutarlı adayların yeni listesi
    """
    yeni_adaylar = []
    for aday in adaylar:
        # Bu aday gizli kod olsaydı, tahminimize ne skor verirdi?
        simule_skor = skor_hesapla(aday, tahmin)
        # Sadece gerçek skorla eşleşenleri tut
        if simule_skor == alinan_skor:
            yeni_adaylar.append(aday)
    return yeni_adaylar


# -----------------------------------------------------------------------------
# ADIM 4: Minimax ile en iyi tahmini seç
# -----------------------------------------------------------------------------
# Knuth'un algoritmasının kalbi burasıdır.
#
# Fikir: Bir sonraki tahmini öyle seç ki, hangi skoru alırsak alalım,
# aday listesi mümkün olduğunca küçük kalsın.
#
# Formülasyon:
#   Her aday tahmin G için:
#     Her olası skor S için:
#       S skorunu veren aday sayısını say → bu "kova" büyüklüğüdür
#     En büyük kovayı bul → bu G'nin "en kötü durumu"dur (worst case)
#   En küçük "en kötü durumu" olan G'yi seç → minimax
#
# Neden tüm 1296 kodu tarıyoruz, sadece adayları değil?
#   Bazen aday olmayan bir kod, adayları daha iyi parçalayan bir tahmin olabilir.
#   Örn. aday listesi {1234, 1243, 1324} iken "5566" tahmini bunları farklı
#   kovaları düşürebilir.
#
# Beraberlik çözümü: Eğer iki tahmin aynı minimax değerini veriyorsa,
# aday listesinde olan tercih edilir (hem tahmin hem cevap olabilir).

def en_iyi_tahmini_sec(adaylar):
    """
    Minimax stratejisiyle en iyi sonraki tahmini döndürür.

    Parametreler:
        adaylar: list of tuple, kalan aday listesi

    Döndürür:
        En iyi tahmin tuple
    """
    # Özel durumlar: 1 veya 2 aday varsa doğrudan adayı tahmin et
    if len(adaylar) == 1:
        return adaylar[0]
    if len(adaylar) == 2:
        return adaylar[0]  # İkisi de eşit değerde, birini seç

    en_iyi_tahmin = None
    en_iyi_en_kotu = float('inf')  # Minimize etmek istediğimiz değer
    en_iyi_aday_mi = False          # Beraberlik çözümü için

    # Tüm 1296 kodu potansiyel tahmin olarak dene
    for tahmin_adayi in TUM_KODLAR:

        # Bu tahmin için: her skor kaç adayı kapsar?
        kovalar = {}
        for gercek_aday in adaylar:
            s = skor_hesapla(gercek_aday, tahmin_adayi)
            kovalar[s] = kovalar.get(s, 0) + 1

        # Bu tahminin en kötü durumu = en büyük kova
        en_kotu = max(kovalar.values())

        # Bu tahmin aday listesinde mi?
        aday_mi = tahmin_adayi in adaylar

        # Minimax güncelleme:
        # Daha iyi bir en_kötü bulduk → güncelle
        # Eşit en_kötü ama bu sefer aday listesinden → güncelle (beraberlik çözümü)
        if (en_kotu < en_iyi_en_kotu or
                (en_kotu == en_iyi_en_kotu and aday_mi and not en_iyi_aday_mi)):
            en_iyi_en_kotu = en_kotu
            en_iyi_tahmin = tahmin_adayi
            en_iyi_aday_mi = aday_mi

    return en_iyi_tahmin


# -----------------------------------------------------------------------------
# ADIM 5: Oyunu oyna
# -----------------------------------------------------------------------------
# Algoritmayı baştan sona çalıştıran ana fonksiyon.
# İlk tahmin her zaman (1,1,2,2)'dir — Knuth'un analizi bu başlangıcın
# optimal olduğunu göstermiştir.

def knuth_mastermind(gizli_kod, verbose=True):
    """
    Knuth algoritmasıyla verilen gizli kodu çözer.

    Parametreler:
        gizli_kod: tuple, örn. (4, 3, 5, 3)
        verbose  : bool, adım adım çıktı verilsin mi

    Döndürür:
        Kaç tahmin yapıldığı (int)
    """
    adaylar = list(TUM_KODLAR)  # Başlangıçta tüm 1296 kod adaydır
    tur = 0

    if verbose:
        print(f"Gizli kod: {gizli_kod}")
        print(f"Toplam aday: {len(adaylar)}")
        print("-" * 50)

    while True:
        tur += 1

        # İlk tahmini sabit seç, sonraki turlar için minimax kullan
        if tur == 1:
            tahmin = (1, 1, 2, 2)
        else:
            tahmin = en_iyi_tahmini_sec(adaylar)

        # Skoru hesapla (gerçek oyunda bu bilgi dışarıdan gelir)
        siyah, beyaz = skor_hesapla(gizli_kod, tahmin)

        if verbose:
            print(f"Tur {tur}: Tahmin={tahmin}  →  {siyah} siyah, {beyaz} beyaz  "
                  f"(aday havuzu: {len(adaylar)})")

        # 4 siyah = kodu bulduk
        if siyah == 4:
            if verbose:
                print(f"\nBulundu! {tur} tahminde çözüldü.")
            return tur

        # Alınan skorla tutarsız adayları eliyoruz
        adaylar = adaylari_filtrele(adaylar, tahmin, (siyah, beyaz))

        if verbose:
            if len(adaylar) <= 8:
                print(f"         Kalan adaylar ({len(adaylar)}): {adaylar}")
            else:
                print(f"         Kalan aday sayısı: {len(adaylar)}")


# -----------------------------------------------------------------------------
# ADIM 6: Garantiyi doğrula
# -----------------------------------------------------------------------------
# Knuth, algoritmasının 1296 kodun HEPSİNİ en fazla 5 tahminde çözdüğünü
# kanıtlar. Bunu tüm kodlar üzerinde çalıştırarak doğrulayabiliriz.

def garantiyi_dogrula():
    """
    Algoritmayı tüm 1296 gizli kod için çalıştırır, istatistik verir.
    """
    print("Tüm 1296 kod test ediliyor...\n")

    dagılım = {}  # kaç tahmin → kaç kod

    for i, gizli in enumerate(TUM_KODLAR):
        tahmin_sayisi = knuth_mastermind(gizli, verbose=False)
        dagılım[tahmin_sayisi] = dagılım.get(tahmin_sayisi, 0) + 1

        # İlerleme göster
        if (i + 1) % 200 == 0:
            print(f"  {i+1}/1296 tamamlandı...")

    print("\n--- Sonuç ---")
    toplam = 0
    for tur in sorted(dagılım):
        sayi = dagılım[tur]
        toplam += tur * sayi
        print(f"  {tur} tahminde çözülen: {sayi:4d} kod")

    maks = max(dagılım.keys())
    ortalama = toplam / 1296
    print(f"\n  Maksimum tahmin sayısı : {maks}")
    print(f"  Ortalama tahmin sayısı : {ortalama:.4f}")
    print(f"  Knuth garantisi (≤5)   : {'GEÇTI' if maks <= 5 else 'BAŞARISIZ'}")


# -----------------------------------------------------------------------------
# Ana program
# -----------------------------------------------------------------------------

if __name__ == "__main__":

    # Örnek 1: Ekran görüntüsündeki oyun (gizli kod: 4 3 5 3)
    print("=" * 50)
    print("Örnek oyun: gizli kod (4, 3, 5, 3)")
    print("=" * 50)
    knuth_mastermind((4, 3, 5, 3), verbose=True)

    print()

    # Örnek 2: Zor bir kod
    print("=" * 50)
    print("Örnek oyun: gizli kod (6, 6, 6, 6)")
    print("=" * 50)
    knuth_mastermind((6, 6, 6, 6), verbose=True)

    print()

    # Örnek 3: Tüm 1296 kodu test et ve garantiyi doğrula
    print("=" * 50)
    print("Knuth garantisi doğrulaması (tüm 1296 kod)")
    print("=" * 50)
    garantiyi_dogrula()