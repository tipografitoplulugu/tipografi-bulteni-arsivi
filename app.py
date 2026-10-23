import streamlit as st
import sqlite3
import re
import os

st.set_page_config(page_title="Tipografi Bülteni Arama Motoru", page_icon="🔤", layout="wide")

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tipografi_arsivi.db")

@st.cache_resource
def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

conn = get_connection()
cur = conn.cursor()

# İstatistikler
cur.execute("SELECT COUNT(DISTINCT dosya_adi), COUNT(*) FROM haberler")
total_bulten, total_haber = cur.fetchone()

# Kenar Çubuğu
with st.sidebar:
    st.title("🔤 Tipografi Bülteni")
    st.markdown("**Arşiv Kapsamı:** 2019 – 2026")
    st.metric("Toplam Bülten", f"{total_bulten} Sayı")
    st.metric("İndekslenen Haber", f"{total_haber:,}")
    st.divider()
    st.markdown("Türkçe Tipografi Topluluğu bülten arşivinde başlık ve içerik araması yapabilirsiniz.")

# Ana Sayfa
st.title("🔍 Tipografi Bülteni Gelişmeler Veritabanı")
st.markdown("Arşivde yer alan 90+ bülten içindeki tüm gelişmeleri, terimleri ve haberleri arayın.")

col1, col2 = st.columns([4, 1])
with col1:
    sorgu = st.text_input("Arama Terimi", placeholder="örn: değişken yazıtipi, monotype, gutenberg, kaligrafi, yapay zeka...")
with col2:
    yil_secim = st.selectbox("Yıl Filtresi", ["Tümü", "2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019"])

if sorgu.strip():
    kelime = sorgu.strip()
    fts_sorgu = f'"{kelime}"'
    
    if yil_secim == "Tümü":
        cur.execute("""
            SELECT h.bulten_adi, h.yil, h.ay, h.baslik, h.icerik
            FROM haberler_fts f
            JOIN haberler h ON f.rowid = h.id
            WHERE haberler_fts MATCH ?
            ORDER BY h.yil DESC, h.id DESC
        """, (fts_sorgu,))
    else:
        cur.execute("""
            SELECT h.bulten_adi, h.yil, h.ay, h.baslik, h.icerik
            FROM haberler_fts f
            JOIN haberler h ON f.rowid = h.id
            WHERE haberler_fts MATCH ? AND h.yil = ?
            ORDER BY h.id DESC
        """, (fts_sorgu, int(yil_secim)))
        
    sonuclar = cur.fetchall()

    if sonuclar:
        kaynaklar = []
        for r in sonuclar:
            temiz = re.sub(r"^.*?:\s*", "", r[0])
            if temiz not in kaynaklar:
                kaynaklar.append(temiz)

        kaynak_str = ", ".join(kaynaklar)
        st.info(f"**Anahtar Kelime:** `{kelime}`\n\n**Kaynaklar:** {kaynak_str}\n\n**Bulunan Sonuç:** {len(sonuclar)} gelişme")
        st.markdown("---")
        
        for bulten_adi, yil, ay, baslik, icerik in sonuclar:
            temiz_bulten = re.sub(r"^.*?:\s*", "", bulten_adi)
            with st.container():
                st.markdown(f"### {baslik}")
                st.caption(f"🗓️ **Kaynak:** {temiz_bulten} ({yil})")
                st.markdown(icerik)
                st.divider()
    else:
        st.warning(f"'{kelime}' ile eşleşen bir haber bulunamadı.")
else:
    st.write("Aramak istediğiniz terimi yukarıdaki kutucuğa yazın.")
