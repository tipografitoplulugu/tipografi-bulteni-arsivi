# 🔤 Tipografi Bülteni — Arşiv ve Arama Motoru

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://tipografi-bulteni-arsivi.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

[Türkçe Tipografi Topluluğu](https://medium.com/tipografi) tarafından 2019 yılından bu yana düzenli olarak hazırlanan aylık bültenlerin tam metin aranabilir dijital arşivi ve bilgi tabanı.

👉 **Canlı Arama Motoru:** [tipografi-bulteni-arsivi.streamlit.app](https://tipografi-bulteni-arsivi.streamlit.app/)

---

## 📌 Proje Hakkında

Bu proje; tipografi, yazı tasarımı, görsel kimlik, açık kaynaklı fontlar, lisanslama tartışmaları, kaligrafi ve baskı tarihi üzerine dünyadan ve Türkiye’den derlenen aylık gelişmelerin toplandığı kapsamlı bir arama platformudur.

Arşivde yer alan **93 bülten**, bağımsız haber bloklarına ayrılarak tam metin arama (Full-Text Search) motoruyla indekslenmiştir.

### 📊 Arşiv İstatistikleri
* **Kapsanan Dönem:** 2019 – 2026
* **Toplam Bülten:** 93 Sayı
* **İndekslenen Haber / Gelişme:** 1.620+ kayıt
* **Veritabanı Motoru:** SQLite (FTS5)

---

## ✨ Özellikler

* **Hızlı Tam Metin Arama (FTS5):** Aradığınız terimi (*örn: değişken yazıtipi, Monotype, Gutenberg, kaligrafi, yapay zekâ*) başlık ve paragraflar içinde milisaniyeler içinde bulur.
* **Akıllı Sonuç Kartları:** Aranan anahtar kelimenin hangi aylarda ve hangi bültenlerde yer aldığını özet kaynak bilgisiyle gösterir.
* **Yıl Bazlı Filtreleme:** 2019–2026 arasındaki belirli bir yıla odaklanarak arama yapabilme imkânı.
* **Sıfır Dış Bağımlılık:** Harici bir veritabanı veya sunucu maliyeti gerektirmeyen hafif, taşınabilir SQLite mimarisi.

---

## 🚀 Yerel Kurulum (Local Setup)

Projeyi kendi bilgisayarınızda çalıştırmak için:

1. **Depoyu klonlayın:**
   ```bash
   git clone https://github.com/tipografitoplulugu/tipografi-bulteni-arsivi.git
   cd tipografi-bulteni-arsivi
