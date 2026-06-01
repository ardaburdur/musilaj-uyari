import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image

# =====================================================================
# 🎨 WEB SİTESİ ARAYÜZÜ AYARLARI
# =====================================================================
st.set_page_config(page_title="Deniz Kirliliği Tespit Sistemi", layout="wide", page_icon="🌊")

st.title("🛰️ Uydu Verili Deniz Kirliliği Tespit Sistemi")
st.markdown("**Geliştirici:** Elektrik-Elektronik Mühendisliği Bitirme Projesi")
st.markdown("Bu sistem, SAR ve Optik uydu görüntülerini (PNG/JPG formatında) kullanarak ileri sinyal işleme algoritmalarıyla deniz kirliliğini otonom olarak tespit eder.")

# =====================================================================
# ⚙️ PNG UYUMLU TESPİT ALGORİTMALARI (8-Bit Motor)
# =====================================================================
def petrol_tespit_et(sar_8bit):
    # Görüntünün etrafındaki zifiri karanlık boşlukları (eğer varsa) yoksay
    gecerli_maske = sar_8bit > 0
    
    # 1. Kıyı Zırhı (Otsu Algoritması)
    th, _ = cv2.threshold(sar_8bit[gecerli_maske], 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kara_maskesi = (sar_8bit > th).astype(np.uint8)
    
    # Karayı denize doğru şişir ki gölgeler kapansın
    kara_zirhi = cv2.dilate(kara_maskesi, np.ones((5, 5), np.uint8), iterations=1)
    deniz_maskesi = gecerli_maske & (kara_zirhi == 0)

    # 2. Sızıntıyı Bul (Denizin en karanlık %8'i)
    deniz_pikselleri = sar_8bit[deniz_maskesi]
    if len(deniz_pikselleri) > 0:
        karanlik_esik = np.percentile(deniz_pikselleri, 8)
        petrol_ham = ((sar_8bit <= karanlik_esik) & deniz_maskesi).astype(np.uint8)
    else:
        petrol_ham = np.zeros_like(sar_8bit)

    # 3. Kırmızı Katman (RGBA) Ekrana Çizim İçin
    h, w = sar_8bit.shape
    kirmizi_katman = np.zeros((h, w, 4), dtype=np.float32)
    kirmizi_katman[petrol_ham == 1] = [1.0, 0.0, 0.0, 0.8] # Kırmızı ve yarı saydam

    return sar_8bit, kirmizi_katman

def musilaj_tespit_et(optik_8bit):
    # Müsilaj deniz yüzeyinde genelde parlak (beyaza/sarıya dönük) görünür
    # Otsu ile en parlak yerleri ayırıyoruz
    _, th = cv2.threshold(optik_8bit, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    h, w = optik_8bit.shape
    yesil_katman = np.zeros((h, w, 4), dtype=np.float32)
    yesil_katman[(optik_8bit > th)] = [0.0, 1.0, 0.0, 0.7] # Yeşil ve yarı saydam
    
    return optik_8bit, yesil_katman

# =====================================================================
# 🖱️ KULLANICI KONTROL PANELİ
# =====================================================================
st.sidebar.header("Ayarlar ve Yükleme")
mod = st.sidebar.radio("Çalışma Modunu Seçin:", ["Petrol Sızıntısı (SAR)", "Müsilaj Tespiti (Optik)"])

# 🛑 TIF YERİNE PNG/JPG DESTEĞİ EKLENDİ 🛑
yuklenen_dosya = st.sidebar.file_uploader("Uydu Görüntüsü Yükle (.png, .jpg)", type=["png", "jpg", "jpeg"])

if st.sidebar.button("Analizi Başlat", type="primary"):
    if yuklenen_dosya is not None:
        with st.spinner('Sinyal İşleme Motoru Çalışıyor...'):
            
            # 🖼️ Resmi PIL ile okuyup Numpy matrisine çevirme
            image = Image.open(yuklenen_dosya)
            img_array = np.array(image)

            # Eğer resim renkli (RGB veya RGBA) ise sinyal işleme için Gri'ye (Grayscale) çevir
            if len(img_array.shape) == 3:
                if img_array.shape[2] == 4: # RGBA (Saydamlık kanalı var)
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2GRAY)
                else: # RGB
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            band_verisi = img_array.astype(np.uint8)

            # Seçilen moda göre algoritmayı tetikle
            if mod == "Petrol Sızıntısı (SAR)":
                arkaplan, maske = petrol_tespit_et(band_verisi)
                hedef_isim = "Petrol Sızıntısı"
            else:
                arkaplan, maske = musilaj_tespit_et(band_verisi)
                hedef_isim = "Müsilaj Yayılımı"

            st.success("Analiz Tamamlandı!")

            # =====================================================================
            # 🖥️ SONUÇLARIN EKRANA BASILMASI
            # =====================================================================
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Yüklenen Uydu Görüntüsü")
                fig1, ax1 = plt.subplots()
                ax1.imshow(arkaplan, cmap='gray')
                ax1.axis('off')
                st.pyplot(fig1)
                
            with col2:
                st.subheader(f"{hedef_isim} Tespiti")
                fig2, ax2 = plt.subplots()
                ax2.imshow(arkaplan, cmap='gray')
                ax2.imshow(maske) # Kırmızı veya Yeşil maskeyi üstüne bindir
                ax2.axis('off')
                st.pyplot(fig2)
                
    else:
        st.sidebar.error("Lütfen önce bir PNG veya JPG dosyası yükleyin!")
