# RL 2D Car

Basit bir 2D yarış pistinde Q-Learning kullanan otonom araç projesi.

## Proje Amacı

Bu projenin amacı, bir aracın sensör verilerini kullanarak pist üzerinde kendi kendine sürüş öğrenmesini sağlamaktır.

Ajan başlangıçta tamamen rastgele hareket eder. Zamanla checkpoint ödülleri ve Q-Learning sayesinde pist üzerinde ilerlemeyi öğrenir.

---

## Özellikler

### Araç Sistemi

* 2D araç fiziği
* Hızlanma
* Direksiyon kontrolü
* Sürtünme (friction)
* Çarpışma algılama

### Sensör Sistemi

Araç çevresini algılamak için 7 adet mesafe sensörü kullanır.

Sensör açıları:

* -90°
* -60°
* -30°
* 0°
* +30°
* +60°
* +90°

Her sensör pist dışına olan mesafeyi ölçer.

---

## Reinforcement Learning

Algoritma:

* Q-Learning

Durum (State):

* 7 sensör mesafesi
* araç hızı

Aksiyonlar:

| ID | Aksiyon   |
| -- | --------- |
| 0  | Bekle     |
| 1  | Gaz       |
| 2  | Sola dön  |
| 3  | Sağa dön  |
| 4  | Gaz + Sol |
| 5  | Gaz + Sağ |

Toplam aksiyon sayısı:

```text
6
```

---

## Reward Sistemi

### Pozitif Ödüller

Pist üzerinde kalmak:

```text
+0.1
```

Checkpoint geçmek:

```text
+500
```

Tur tamamlamak:

```text
+1000
```

Checkpoint'e yaklaşmak:

```text
progress * 0.1
```

### Negatif Ödüller

Hareketsiz kalmak:

```text
-2
```

Pist dışına çıkmak:

```text
-100
```

---

## Checkpoint Sistemi

Araç checkpointleri sırayla geçmelidir.

Mevcut checkpoint sayısı:

```text
6
```

Her checkpoint geçildiğinde:

* ödül kazanılır
* sonraki checkpoint hedef olur

Son checkpoint tamamlanınca:

* tur sayısı artar
* başlangıç checkpointine dönülür

---

## Öğrenme Parametreleri

Learning Rate:

```text
0.1
```

Discount Factor:

```text
0.95
```

Başlangıç Epsilon:

```text
0.2
```

Minimum Epsilon:

```text
0.01
```

Epsilon Decay:

```text
0.999
```

---

## Kaydedilen Veriler

Program kapanırken otomatik kaydedilir:

* Q Table
* Best Score
* Epsilon

Dosya:

```text
q_table.pkl
```

---

## Tamamlanan Geliştirmeler

* [x] Araç hareket sistemi
* [x] Sensör sistemi
* [x] Çarpışma algılama
* [x] Q-Learning
* [x] Checkpoint sistemi
* [x] Tur sistemi
* [x] Progress reward
* [x] Q-table kaydetme/yükleme
* [x] 6 aksiyon sistemi
* [x] State discretization

---

## Yapılacaklar

### Kısa Vadeli

* [ ] Episode timeout
* [ ] Checkpoint sırası doğrulama
* [ ] Reward tuning
* [ ] Daha iyi epsilon stratejisi

### Orta Vadeli

* [ ] Daha karmaşık pist
* [ ] Birden fazla başlangıç pozisyonu
* [ ] Geri gitme cezası
* [ ] Hız ödülü

### Uzun Vadeli

* [ ] Deep Q Network (DQN)
* [ ] PyTorch entegrasyonu
* [ ] Model checkpoint sistemi
* [ ] Eğitim istatistikleri grafikleri
* [ ] Farklı pistlerde test

---

## Son Durum

Proje şu anda çalışan bir Q-Learning ajanına sahiptir.

Ajan:

* checkpoint geçebilmektedir
* tur tamamlayabilmektedir
* geçmiş öğrenmesini saklayabilmektedir

Bir sonraki büyük hedef:

```text
Q-Learning → DQN geçişi
```
