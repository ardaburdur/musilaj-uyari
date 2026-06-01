import streamlit as st
import numpy as np
import cv2
import rasterio
from rasterio.io import MemoryFile
import matplotlib.pyplot as plt

# =====================================================================
# 🎨 WEB SİTESİ ARAYÜZÜ AYARLARI
# =====================================================================
st.set_page_config(page_title="Deniz Kirliliği Tespit Sistemi", layout="wide", page_icon="🌊")

st.title("🛰️ Uydu Verili Deniz Kirliliği Tespit Sistemi")
st.markdown("**Geliştirici:** Elektrik-Elektronik Mühendisliği Bitirme Projesi")
st.markdown("Bu sistem, SAR (Radar) ve Optik uydu görüntülerini kullanarak makine öğrenmesi ve ileri sinyal işleme algoritmalarıyla deniz kirliliğini (Petrol ve Müsilaj) otonom olarak tespit eder.")

# =====================================================================
# ⚙️ TESPİT ALGORİTMALARI (Buraya kendi nihai fonksiyonlarını koyabilirsin)
# =====================================================================
def petrol_tespit_et(sar_bandi):
    # Uzay boşluğunu temizle
    gecerli_maske = (sar_bandi != 0) & (~np.isnan(sar_bandi)) & (sar_bandi > -50.0)
    
    # Normalizasyon
    p1, p99 = np.percentile(sar_bandi[gecerli_maske], (1, 99))
    sar_kisilmis = np.clip(sar_bandi, p1, p99)
    sar_8bit = np.zeros_like(sar_bandi, dtype=np.uint8)
    sar_8bit[gecerli_maske] = cv2.normalize(sar_kisilmis[gecerli_maske], None, 0, 255, cv2.NORM_MINMAX).flatten()

    # Kıyı Zırhı
    th, _ = cv2.threshold(sar_8bit[gecerli_maske], 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kara_maskesi = (sar_8bit > th).astype(np.uint8)
    kara_zirhi = cv2.dilate(kara_maskesi, np.ones((5, 5), np.uint8), iterations=1)
    deniz_maskesi = gecerli_maske & (kara_zirhi == 0)

    # Sızıntıyı Bul (En karanlık %8)
    deniz_pikselleri = sar_8bit[deniz_maskesi]
    if len(deniz_pikselleri) > 0:
        karanlik_esik = np.percentile(deniz_pikselleri, 8)
        petrol_ham = ((sar_8bit <= karanlik_esik) & deniz_maskesi).astype(np.uint8)
    else:
        petrol_ham = np.zeros_like(sar_8bit)

    # Kırmızı Katman (RGBA)
    h, w = sar_8bit.shape
    kirmizi_katman = np.zeros((h, w, 4), dtype=np.float32)
    kirmizi_katman[petrol_ham == 1] = [1.0, 0.0, 0.0, 0.8] 

    return sar_8bit, kirmizi_katman

def musilaj_tespit_et(optik_band):
    # Buraya daha önce yazdığımız müsilaj tespit kodunu (U-Net veya NDVI benzeri indeksli kodu) entegre edebilirsin.
    # Şimdilik örnek bir filtreleme koyuyorum.
    sar_8bit = cv2.normalize(optik_band, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    _, th = cv2.threshold(sar_8bit, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    h, w = sar_8bit.shape
    yesil_katman = np.zeros((h, w, 4), dtype=np.float32)
    yesil_katman[(sar_8bit > th)] = [0.0, 1.0, 0.0, 0.7] # Müsilajı yeşil göster
    
    return sar_8bit, yesil_katman

# =====================================================================
# 🖱️ KULLANICI KONTROL PANELİ (Sol Menü)
# =====================================================================
st.sidebar.header("Ayarlar ve Yükleme")
mod = st.sidebar.radio("Çalışma Modunu Seçin:", ["Petrol Sızıntısı (SAR)", "Müsilaj Tespiti (Optik)"])

yuklenen_dosya = st.sidebar.file_uploader("Uydu Görüntüsü Yükle (.tif)", type=["tif", "tiff"])

if st.sidebar.button("Analizi Başlat", type="primary"):
    if yuklenen_dosya is not None:
        with st.spinner('Yapay Zeka ve Sinyal İşleme Motoru Çalışıyor...'):
            # Kullanıcının yüklediği dosyayı bellekte okuma
            with MemoryFile(yuklenen_dosya) as memfile:
                with memfile.open() as src:
                    band_verisi = src.read(1).astype(np.float32)

            # Seçilen moda göre işleme yap
            if mod == "Petrol Sızıntısı (SAR)":
                arkaplan, maske = petrol_tespit_et(band_verisi)
                hedef_isim = "Petrol Sızıntısı"
            else:
                arkaplan, maske = musilaj_tespit_et(band_verisi)
                hedef_isim = "Müsilaj Yayılımı"

            st.success("Analiz Tamamlandı!")

            # =====================================================================
            # 🖼️ SONUÇLARIN EKRANA BASILMASI
            # =====================================================================
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Orijinal Uydu Görüntüsü")
                fig1, ax1 = plt.subplots()
                ax1.imshow(arkaplan, cmap='gray')
                ax1.axis('off')
                st.pyplot(fig1)
                
            with col2:
                st.subheader(f"Yapay Zeka Destekli {hedef_isim} Tespiti")
                fig2, ax2 = plt.subplots()
                ax2.imshow(arkaplan, cmap='gray')
                ax2.imshow(maske)
                ax2.axis('off')
                st.pyplot(fig2)
                
    else:
        st.sidebar.error("Lütfen önce bir .tif dosyası yükleyin!")
