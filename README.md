# 2D RL Car Area

Python ve Pygame kullanılarak geliştirilen 2D bir otonom araç öğrenme projesi.

Araç, Q-Learning algoritması ile pist üzerinde hareket etmeyi, duvarlardan kaçınmayı ve checkpoint'leri doğru sırada geçerek tur tamamlamayı öğrenir.

---

## Özellikler

### Araç Sistemi

- 2D araç fizik sistemi
- İleri ve geri hareket
- Direksiyon kontrolü
- Hız ve açı yönetimi

### Sensör Sistemi

Araç çevresini 3 adet mesafe sensörü ile algılar:

- Sol sensör
- Ön sensör
- Sağ sensör

Sensörler duvara olan mesafeyi ölçer ve bu bilgiler RL ajanının state bilgisi olarak kullanılır.

---

## Reinforcement Learning Sistemi

### Algoritma

- Q-Learning

### State Bilgisi

Ajan aşağıdaki bilgileri kullanarak karar verir:

- Sol sensör mesafesi
- Ön sensör mesafesi
- Sağ sensör mesafesi
- Araç hızı

State alanı küçültmek için değerler kategorilere ayrılır:

- 0 → Çok yakın
- 1 → Yakın
- 2 → Uzak

---

## Aksiyonlar

Ajan toplam 6 farklı aksiyon seçebilir:

| Aksiyon | Açıklama |
|---|---|
| 0 | İleri |
| 1 | Geri |
| 2 | Sola dön |
| 3 | Sağa dön |
| 4 | İleri + sola dön |
| 5 | İleri + sağa dön |

---

## Q-Learning Parametreleri

| Parametre | Değer |
|---|---|
| Learning Rate | 0.1 |
| Discount Factor (Gamma) | 0.95 |
| Epsilon | 0.2 |
| Minimum Epsilon | 0.01 |
| Epsilon Decay | 0.999 |

---

## Reward Sistemi

| Durum | Ödül |
|---|---|
| Pist üzerinde kalmak | +0.1 |
| Checkpoint'e yaklaşmak | Mesafeye göre pozitif/negatif |
| Checkpoint geçmek | +100 |
| Tur tamamlamak | +1000 |
| Hareketsiz kalmak | -1 |
| Pist dışına çıkmak | -150 |

---

## Pist Sistemi

Pist:

- Dış sınır
- İç boşluk
- Checkpoint çizgilerinden oluşur

Checkpoint sistemi:

- Checkpoint'ler sıralı takip edilir
- Bir checkpoint geçildiğinde bir sonraki checkpoint hedef olur
- Tur tamamlandığında sayaç artar

---

## Episode Sistemi

Her eğitim denemesi bir episode olarak değerlendirilir.

Özellikler:

- Maksimum 3000 step sınırı
- Timeout durumunda otomatik reset
- Çarpışma sonrası otomatik reset
- Episode sonunda epsilon azaltma
- Episode skor takibi

---

## Eğitim ve Debug Bilgileri

Ekranda aşağıdaki bilgiler gösterilir:

- Sensör değerleri
- Mevcut skor
- En iyi skor
- Öğrenilen state sayısı
- Son seçilen aksiyon
- Hedef checkpoint
- Geçilen checkpoint sayısı
- Tamamlanan tur sayısı
- Epsilon değeri
- Geçen süre
- Episode step sayısı
- Anlık reward değeri

---

## Kayıt Sistemi

Program kapanırken otomatik olarak:

- Q-Table kaydedilir
- En iyi skor kaydedilir
- Epsilon değeri kaydedilir

Program tekrar açıldığında:

- Önceki öğrenme yüklenir
- Eğitim kaldığı yerden devam eder

---

## Tamamlanan Geliştirmeler

- [x] Araç hareket sistemi
- [x] Sensör sistemi
- [x] Pist ve çarpışma sistemi
- [x] Q-Learning altyapısı
- [x] State discretization
- [x] 6 aksiyon sistemi
- [x] Q-Table kayıt/yükleme
- [x] Checkpoint sistemi
- [x] Tur sistemi
- [x] Progress reward
- [x] Episode timeout sistemi
- [x] Reward tuning
- [x] Eğitim debug ekranı

---

## Yapılacak Geliştirmeler

- [ ] Daha iyi epsilon stratejisi
- [ ] Daha karmaşık pist
- [ ] Birden fazla başlangıç pozisyonu
- [ ] Geri gitme cezası
- [ ] Hız ödülü
- [ ] DQN geçişi
- [ ] PyTorch entegrasyonu
- [ ] Model checkpoint sistemi
- [ ] Eğitim istatistikleri grafikleri
- [ ] Farklı pistlerde test

---

## Teknolojiler

- Python 3
- Pygame
- Q-Learning
- Pickle

---

## Çalıştırma

```bash
pip install pygame

python main.py
```

---

## Amaç

Bu proje, basit bir Q-Learning ajanının 2D bir ortamda kendi kendine araç sürmeyi öğrenmesini amaçlamaktadır.