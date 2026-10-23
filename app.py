import streamlit as st
import sqlite3
import re
import os
import pandas as pd

st.set_page_config(
    page_title="Tipografi Bülteni Arama Motoru",
    page_icon="T",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tipografik Stil ve Arayüz İyileştirmeleri
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Alegreya:ital,wght@0,400..900;1,400..900&display=swap');
/* 1. Başlıklar: Substack editoryal tarzı Alegreya Serif */
h1, h2, h3, h4, h5, h6,
h1 *, h2 *, h3 *, h4 *, h5 *, h6 *,
.stTitle, .stTitle *,
.stHeader, .stHeader *,
.stSubheader, .stSubheader *,
[data-testid="stHeadingWithActionElements"],
[data-testid="stHeadingWithActionElements"] *,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h1 *,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h2 *,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h3 * {
    font-family: 'Alegreya', Georgia, serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.015em !important;
}

/* 2. Gövde Metinleri ve Arayüz: Apple SF Pro */
html, body, .stApp, [data-testid="stAppViewContainer"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
}

p, li, .stMarkdown p, [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    font-size: 1.02rem !important;
    line-height: 1.65 !important;
}

/* 3. Streamlit İkonlarını Koru (Font çakışmasını ve '_arr...' bozulmalarını önler) */
[data-testid="stIconMaterial"], 
[data-testid="stExpanderToggleIcon"],
[data-testid="stExpanderToggleIcon"] *,
.material-symbols-rounded, 
.material-icons,
[class*="StyledIcon"],
[class*="Icon"] {
    font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
}

/* 4. Bağlantı Linkleri: Mavi ve Altı Çizgili */
a, [data-testid="stMarkdownContainer"] a, .stMarkdown a {
    color: #38bdf8 !important;
    text-decoration: underline !important;
    text-underline-offset: 3px !important;
    text-decoration-thickness: 1.2px !important;
    font-weight: 500 !important;
    background: transparent !important;
    transition: color 0.15s ease;
}
a:hover, [data-testid="stMarkdownContainer"] a:hover, .stMarkdown a:hover {
    color: #7dd3fc !important;
}

/* 5. Zarif Arama Vurgusu (Sarı Blok Yerine İnce Altın Kehribar Vurgu) */
mark {
    background-color: rgba(245, 158, 11, 0.22) !important;
    color: inherit !important;
    border-bottom: 2px solid rgba(245, 158, 11, 0.85) !important;
    padding: 0.05em 0.25em !important;
    border-radius: 3px !important;
    font-weight: 600 !important;
}

/* 6. Popüler Konu Butonları (Arama Alanının Altında Düşük Opaklıklı Haplar) */
.tag-section-title {
    font-size: 0.78rem !important;
    opacity: 0.5 !important;
    margin-top: 0.2rem !important;
    margin-bottom: 0.35rem !important;
    font-weight: 500 !important;
}

div[data-testid="stHorizontalBlock"] button {
    opacity: 0.5 !important;
    font-size: 0.72rem !important;
    padding: 0.2rem 0.5rem !important;
    min-height: 28px !important;
    height: 28px !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    background: rgba(255, 255, 255, 0.04) !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stHorizontalBlock"] button:hover {
    opacity: 1 !important;
    border-color: #38bdf8 !important;
    background: rgba(56, 189, 248, 0.12) !important;
}

/* 7. Açılır Kutular (Expander / Alıntı Formatı) */
[data-testid="stExpander"] {
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 8px !important;
    background: rgba(255, 255, 255, 0.02) !important;
    margin-top: 0.5rem !important;
    margin-bottom: 0.5rem !important;
}

[data-testid="stExpander"] summary {
    font-size: 0.88rem !important;
    opacity: 0.85 !important;
    padding-top: 0.35rem !important;
    padding-bottom: 0.35rem !important;
}

[data-testid="stExpander"] summary:hover {
    opacity: 1 !important;
    color: #38bdf8 !important;
}

/* Kart Ayracı */
hr {
    margin-top: 1.5rem !important;
    margin-bottom: 1.5rem !important;
    border-color: rgba(255, 255, 255, 0.1) !important;
}

/* 8. Zemin Rengi */
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
[data-testid="stSidebar"], [data-testid="stSidebar"] > div,
[data-testid="stSidebarContent"], section[data-testid="stSidebar"] {
    background-color: #121212 !important;
}

/* 9. Sidebar – Body Ayırıcı Dikey Çizgi */
section[data-testid="stSidebar"] {
    border-right: 1px solid rgba(255, 255, 255, 0.25) !important;
}
</style>
""", unsafe_allow_html=True)

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tipografi_arsivi.db")

# 93 bültenin orijinal Medium ve Substack bağlantıları
BULTEN_URLS = {
    "Ocak 2019": "https://medium.com/tipografi/tipografi-haberleri-ocak-2019-604f7ccb2b07",
    "Şubat 2019": "https://medium.com/tipografi/tipografi-haberleri-şubat-2019-20a4558cf898",
    "Mart 2019": "https://medium.com/tipografi/tipografi-haberleri-mart-2019-27f1060df7bc",
    "Nisan 2019": "https://medium.com/tipografi/tipografi-haberleri-nisan-2019-ad2ff81a02a7",
    "Mayıs 2019": "https://medium.com/tipografi/tipografi-haberleri-mayıs-2019-b0fe22fb7228",
    "Haziran 2019": "https://medium.com/tipografi/tipografi-haberleri-haziran-2019-cdcb17025b40",
    "Temmuz 2019": "https://medium.com/tipografi/tipografi-haberleri-temmuz-2019-153421028174",
    "Ağustos 2019": "https://medium.com/tipografi/tipografi-haberleri-ağustos-2019-f19b996e323f",
    "Eylül 2019": "https://medium.com/tipografi/tipografi-haberleri-eylül-2019-6c85e8d07d41",
    "Ekim 2019": "https://medium.com/tipografi/tipografi-haberleri-ekim-2019-9d95ca9dc851",
    "Kasım 2019": "https://medium.com/tipografi/tipografi-haberleri-kasım-2019-1068f7aba186",
    "Aralık 2019": "https://medium.com/tipografi/tipografi-haberleri-aralık-2019-b655b51e2939",
    "Ocak 2020": "https://medium.com/tipografi/tipografi-haberleri-ocak-2020-5cd73e88420c",
    "Şubat 2020": "https://medium.com/tipografi/tipografi-haberleri-şubat-2020-4942a3299f3e",
    "Mart 2020": "https://medium.com/tipografi/tipografi-haberleri-mart-2020-d4b96a791d32",
    "Nisan 2020": "https://medium.com/tipografi/tipografi-haberleri-nisan-2020-c3da4f9a1e28",
    "Mayıs 2020": "https://medium.com/tipografi/tipografi-haberleri-mayıs-2020-15f2875c5a19",
    "Haziran 2020": "https://medium.com/tipografi/tipografi-haberleri-haziran-2020-ba2a3e54fb51",
    "Temmuz 2020": "https://medium.com/tipografi/tipografi-haberleri-temmuz-2020-f398d60949d7",
    "Ağustos 2020": "https://medium.com/tipografi/tipografi-haberleri-ağustos-2020-6cd4fcbd9a3b",
    "Eylül 2020": "https://medium.com/tipografi/tipografi-haberleri-eylül-2020-7cb342277bd3",
    "Ekim 2020": "https://medium.com/tipografi/tipografi-haberleri-ekim-2020-a04d29bed91b",
    "Kasım 2020": "https://medium.com/tipografi/tipografi-haberleri-kasım-2020-e0d7c2fc6b9f",
    "Aralık 2020": "https://medium.com/tipografi/tipografi-haberleri-aralık-2020-d881afb1a230",
    "Ocak 2021": "https://medium.com/tipografi/tipografi-haberleri-ocak-2021-3429aabca4ed",
    "Şubat 2021": "https://medium.com/tipografi/tipografi-haberleri-şubat-2021-6b4d000da517",
    "Mart 2021": "https://medium.com/tipografi/tipografi-haberleri-mart-2021-2b733a4da85d",
    "Nisan 2021": "https://medium.com/tipografi/tipografi-haberleri-nisan-2021-fd6cdff4e9c4",
    "Mayıs 2021": "https://medium.com/tipografi/tipografi-haberleri-mayıs-2021-d8cf2966d3ea",
    "Haziran 2021": "https://medium.com/tipografi/tipografi-haberleri-haziran-2021-623c191197a7",
    "Temmuz 2021": "https://medium.com/tipografi/tipografi-haberleri-temmuz-2021-83e6b71d3f15",
    "Ağustos 2021": "https://medium.com/tipografi/tipografi-haberleri-ağustos-2021-b87f55e89171",
    "Eylül 2021": "https://medium.com/tipografi/tipografi-haberleri-eylül-2021-9ac0312435e3",
    "Ekim 2021": "https://medium.com/tipografi/tipografi-haberleri-ekim-2021-cfac56c9bf63",
    "Kasım 2021": "https://medium.com/tipografi/tipografi-haberleri-kasım-2021-315e190a2dca",
    "Aralık 2021": "https://medium.com/tipografi/tipografi-haberleri-aralık-2021-28519238bd95",
    "Ocak 2022": "https://medium.com/tipografi/tipografi-haberleri-ocak-2022-c3389a6d20f7",
    "Şubat 2022": "https://medium.com/tipografi/tipografi-haberleri-şubat-2022-9d9bcbc58c9c",
    "Mart 2022": "https://medium.com/tipografi/tipografi-haberleri-mart-2022-8b40ca83e307",
    "Nisan 2022": "https://medium.com/tipografi/tipografi-haberleri-nisan-2022-23a68f22d53",
    "Mayıs 2022": "https://medium.com/tipografi/tipografi-haberleri-mayıs-2022-c258249bd466",
    "Haziran 2022": "https://medium.com/tipografi/tipografi-haberleri-haziran-2022-55f6efe264b",
    "Temmuz 2022": "https://medium.com/tipografi/tipografi-haberleri-temmuz-2022-5bef2d0161ed",
    "Ağustos 2022": "https://medium.com/tipografi/tipografi-haberleri-ağustos-2022-16cd48b4cf42",
    "Eylül 2022": "https://medium.com/tipografi/tipografi-haberleri-eylül-2022-971dc3981ffd",
    "Ekim 2022": "https://medium.com/tipografi/tipografi-haberleri-ekim-2022-a5a2414d62b8",
    "Kasım 2022": "https://medium.com/tipografi/tipografi-haberleri-kasım-2022-4f991e4c973b",
    "Aralık 2022": "https://medium.com/tipografi/tipografi-haberleri-aralık-2022-812bc46e6f13",
    "Ocak 2023": "https://medium.com/tipografi/tipografi-bülteni-ocak-2023-9dfac3c77718",
    "Şubat 2023": "https://medium.com/tipografi/tipografi-bülteni-şubat-2023-61bc8fd552ce",
    "Mart 2023": "https://medium.com/tipografi/tipografi-bülteni-mart-2023-3a93154ac01b",
    "Nisan 2023": "https://medium.com/tipografi/tipografi-bülteni-nisan-2023-a14f05be724a",
    "Mayıs 2023": "https://medium.com/tipografi/tipografi-bülteni-mayıs-2023-805c3ba8bd36",
    "Haziran 2023": "https://medium.com/tipografi/tipografi-bülteni-haziran-2023-66206d1949ee",
    "Temmuz 2023": "https://medium.com/tipografi/tipografi-bülteni-temmuz-2023-677cf7be9318",
    "Ağustos 2023": "https://medium.com/tipografi/tipografi-bülteni-ağustos-2023-5ee8b04702ec",
    "Eylül 2023": "https://medium.com/tipografi/tipografi-bülteni-eylül-2023-92014965a49a",
    "Ekim 2023": "https://medium.com/tipografi/tipografi-bülteni-ekim-2023-8dfb252f2a1b",
    "Kasım 2023": "https://medium.com/tipografi/tipografi-bülteni-kasım-2023-2ba98f905d1f",
    "Aralık 2023": "https://medium.com/tipografi/tipografi-bülteni-aralık-2023-dc3a5cc03c6a",
    "Ocak 2024": "https://medium.com/tipografi/tipografi-bülteni-ocak-2024-92f521042bae",
    "Şubat 2024": "https://medium.com/tipografi/tipografi-bülteni-şubat-2024-c2e94d6a58ae",
    "Mart 2024": "https://medium.com/tipografi/tipografi-bülteni-mart-2024-7dbe9c27c694",
    "Nisan 2024": "https://medium.com/tipografi/tipografi-bülteni-nisan-2024-df8f79c906db",
    "Mayıs 2024": "https://medium.com/tipografi/tipografi-bülteni-mayıs-2024-b4a80020ec7f",
    "Haziran 2024": "https://medium.com/tipografi/tipografi-bülteni-haziran-2024-2db3b5b4b237",
    "Temmuz 2024": "https://medium.com/tipografi/tipografi-bülteni-temmuz-2024-1e68e9d4a48c",
    "Ağustos 2024": "https://medium.com/tipografi/tipografi-bülteni-ağustos-2024-d8271c2ec119",
    "Eylül 2024": "https://medium.com/tipografi/tipografi-bülteni-eylül-2024-03f75b4d6162",
    "Ekim 2024": "https://medium.com/tipografi/tipografi-bülteni-ekim-2024-6f8a5ee599fc",
    "Kasım 2024": "https://medium.com/tipografi/tipografi-bülteni-kasım-2024-7ac6873bb581",
    "Aralık 2024": "https://medium.com/tipografi/tipografi-bülteni-aralık-2024-b5fc8e46b4ce",
    "Ocak 2025": "https://medium.com/tipografi/tipografi-bülteni-ocak-2025-4f4f7ad5aca1",
    "Şubat 2025": "https://medium.com/tipografi/tipografi-bülteni-şubat-2025-d8c2206c0274",
    "Mart 2025": "https://medium.com/tipografi/tipografi-bülteni-mart-2025-09e6ff1f9a12",
    "Nisan 2025": "https://medium.com/tipografi/tipografi-bülteni-nisan-2025-9ca46327e554",
    "Mayıs 2025": "https://medium.com/tipografi/tipografi-bülteni-mayıs-2025-81cc9ee02d83",
    "Haziran 2025": "https://medium.com/tipografi/tipografi-bülteni-haziran-2025-057366758db6",
    "Temmuz 2025": "https://medium.com/tipografi/tipografi-bülteni-temmuz-2025-f69f62427adc",
    "Ağustos 2025": "https://medium.com/tipografi/tipografi-bülteni-ağustos-2025-410f52e44a70",
    "Eylül 2025": "https://medium.com/tipografi/tipografi-bülteni-eylül-2025-fa7a0941bd68",
    "Ekim 2025": "https://medium.com/tipografi/tipografi-bülteni-ekim-2025-803661d110ac",
    "Kasım 2025": "https://medium.com/tipografi/tipografi-bülteni-kasım-2025-6a52698d71d0",
    "Aralık 2025": "https://medium.com/tipografi/tipografi-bülteni-aralık-2025-119b6d532a2b",
    "Ocak 2026": "https://tipografi.substack.com/p/tipografi-bulteni-ocak-2026",
    "Şubat 2026": "https://tipografi.substack.com/p/tipografi-bulteni-subat-2026",
    "Mart 2026": "https://tipografi.substack.com/p/tipografi-bulteni-mart-2026",
    "Nisan 2026": "https://tipografi.substack.com/p/tipografi-bulteni-nisan-2026",
    "Mayıs 2026": "https://tipografi.substack.com/p/tipografi-bulteni-mays-2026",
    "Haziran 2026": "https://tipografi.substack.com/p/tipografi-bulteni-haziran-2026",
    "Temmuz 2026": "https://tipografi.substack.com/p/tipografi-bulteni-temmuz-2026",
    "Ağustos 2026": "https://tipografi.substack.com/p/tipografi-bulteni-agustos-2026",
    "Eylül 2026": "https://tipografi.substack.com/p/tipografi-bulteni-eylul-2026"
}

POPULER_ETIKETLER = [
    "Değişken Yazıtipi", "Monotype", "Gutenberg", "Yapay Zekâ",
    "Lisanslama", "Kaligrafi", "TDC", "Google Fonts", "Arial"
]

def get_bulten_url(temiz_bulten, yil):
    if temiz_bulten in BULTEN_URLS:
        return BULTEN_URLS[temiz_bulten]
    
    # Gelecek bültenler için otomatik Substack bağlantısı
    tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    slug = temiz_bulten.lower().translate(tr_map).replace(" ", "-")
    return f"https://tipografi.substack.com/p/{slug}"

def highlight_keyword(text, keyword):
    if not keyword or not keyword.strip():
        return text
    def repl(m):
        full = m.group(0)
        if full.startswith("[") and "](" in full and full.endswith(")"):
            anchor, url = full[1:-1].split("](", 1)
            highlighted_anchor = re.sub(re.escape(keyword), r"<mark>\g<0></mark>", anchor, flags=re.IGNORECASE)
            return f"[{highlighted_anchor}]({url})"
        else:
            return f"<mark>{full}</mark>"

    pattern = re.compile(rf"(\[[^\]]+\]\([^\)]+\)|{re.escape(keyword)})", flags=re.IGNORECASE)
    return pattern.sub(repl, text)

def gorsel_satirlarini_temizle(metin):
    satirlar = metin.split("\n")
    temiz = [s for s in satirlar if not re.match(r"^\s*(\*|_)?\s*Görsel(\/Video)?\s*:\s*", s, re.IGNORECASE)]
    return "\n".join(temiz).strip()

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
    st.image("logo.png", width=120)
    st.title("Tipografi Bülteni")
    st.markdown("**Arşiv Kapsamı:** 2019 – 2026")
    st.markdown(f"**Toplam Bülten:** {total_bulten} Sayı")
    st.markdown(f"**İndekslenen Gelişme:** {total_haber:,}")
    st.divider()
    st.markdown("Türkçe Tipografi Topluluğu bülten arşivinde başlık ve içerik araması yapabilirsiniz.")
    st.markdown("🌐 [Substack](https://tipografi.substack.com/) | [Medium](https://medium.com/tipografi)")

# Ana Sayfa Başlığı
st.title("🔍 Tipografi Bülteni Gelişmeler Veritabanı")
st.markdown("Arşivde yer alan **90+ bülten** içindeki tüm gelişmeleri, terimleri ve haberleri arayın.")

if "secili_etiket" not in st.session_state:
    st.session_state["secili_etiket"] = ""

# 1. Arama Alanı ve Yıl Filtresi
col_search, col_filter = st.columns([4, 1])
with col_search:
    sorgu_input = st.text_input(
        "Arama Terimi",
        value=st.session_state.get("secili_etiket", ""),
        placeholder="örn: değişken yazıtipi, monotype, gutenberg, kaligrafi, yapay zeka...",
        label_visibility="collapsed"
    )
with col_filter:
    yil_secim = st.selectbox(
        "Yıl Filtresi",
        ["Tümü", "2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019"],
        label_visibility="collapsed"
    )

# 2. Arama Alanının Altında Zarif, Düşük Opaklıklı Popüler Konu Butonları
st.markdown('<div class="tag-section-title">Popüler Konular:</div>', unsafe_allow_html=True)
tag_cols = st.columns(len(POPULER_ETIKETLER))
for i, tag in enumerate(POPULER_ETIKETLER):
    if tag_cols[i].button(tag, key=f"btn_tag_{i}", use_container_width=True):
        st.session_state["secili_etiket"] = tag
        st.rerun()

kelime = sorgu_input.strip()

if kelime:
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
        # Kaynakları topla ve tıklanabilir link yap
        kaynak_linkleri = []
        gorulen_kaynaklar = set()
        yil_dagilimi = {y: 0 for y in range(2019, 2027)}
        
        for r in sonuclar:
            temiz = re.sub(r"^.*?:\s*", "", r[0])
            r_yil = r[1]
            if r_yil in yil_dagilimi:
                yil_dagilimi[r_yil] += 1
            if temiz not in gorulen_kaynaklar:
                gorulen_kaynaklar.add(temiz)
                url = get_bulten_url(temiz, r_yil)
                kaynak_linkleri.append(f"[**{temiz}**]({url})")

        kaynak_str = " • ".join(kaynak_linkleri)
        st.info(f"**Anahtar Kelime:** `{kelime}`\n\n**Kaynak Bültenler:** {kaynak_str}\n\n**Bulunan Sonuç:** {len(sonuclar)} gelişme")

        # Zaman Çizelgesi Dağılım Grafiği
        df_trend = pd.DataFrame(
            [{"Yıl": str(y), "Gelişme Sayısı": count} for y, count in yil_dagilimi.items()]
        ).set_index("Yıl")

        with st.expander("📊 Yıllara Göre Dağılım Grafiği (Zaman Çizelgesi)", expanded=False):
            st.bar_chart(df_trend, height=200)

        st.markdown("---")
        
        # Sonuç Kartları
        for bulten_adi, yil, ay, baslik, icerik in sonuclar:
            temiz_bulten = re.sub(r"^.*?:\s*", "", bulten_adi)
            bulten_url = get_bulten_url(temiz_bulten, yil)
            temiz_icerik = gorsel_satirlarini_temizle(icerik)
            
            with st.container():
                # Başlığı Alegreya serif ile göster ve aranan kelimeyi zarifçe vurgula
                vurgulu_baslik = highlight_keyword(baslik, kelime)
                st.markdown(f"### {vurgulu_baslik}", unsafe_allow_html=True)
                
                # Tıklanabilir Kaynak ve Tarih
                st.caption(f"🗓️ **Kaynak:** [{temiz_bulten} ({yil})]({bulten_url}) ↗")
                
                # "Küçük Puntolar" bölümünde sadece aranan kelimenin geçtiği maddeyi göster
                if "küçük puntolar" in baslik.lower():
                    satirlar = [s.strip() for s in temiz_icerik.split("\n") if s.strip()]
                    eslesenler = [s for s in satirlar if kelime.lower() in s.lower()]
                    
                    if eslesenler:
                        for madde in eslesenler:
                            vurgulu_madde = highlight_keyword(madde, kelime)
                            st.markdown(vurgulu_madde, unsafe_allow_html=True)
                        
                        with st.expander("📌 Bu sayının tüm Küçük Puntolar maddelerini göster"):
                            vurgulu_tamami = highlight_keyword(temiz_icerik, kelime)
                            st.markdown(vurgulu_tamami, unsafe_allow_html=True)
                    else:
                        vurgulu_icerik = highlight_keyword(temiz_icerik, kelime)
                        st.markdown(vurgulu_icerik, unsafe_allow_html=True)
                else:
                    vurgulu_icerik = highlight_keyword(temiz_icerik, kelime)
                    st.markdown(vurgulu_icerik, unsafe_allow_html=True)
                
                # Alıntıla (Cite) Kutusu — APA 7
                temiz_baslik_duz = re.sub(r"[*_`#]", "", baslik).strip()
                # APA 7: Yazar. (Yıl, Ay). Başlık. *Süreli Yayın Adı*. URL
                alinti_metni = f'Türkçe Tipografi Topluluğu. ({yil}, {ay}). {temiz_baslik_duz}. Tipografi Bülteni. {bulten_url}'
                
                with st.expander("📖 Alıntıla (APA 7)", expanded=False):
                    st.code(alinti_metni, language="text")
                    st.caption("APA 7 alıntı formatı. Kullanırken *Tipografi Bülteni* italik yazılmalıdır. Sağ üstteki simgeden tek tıkla kopyalayabilirsiniz.")
                        
                st.divider()
    else:
        st.warning(f"'{kelime}' ile eşleşen bir haber bulunamadı.")
else:
    st.write("Aramak istediğiniz terimi yukarıdaki kutucuğa yazın veya popüler konulardan birine tıklayın.")
