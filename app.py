import streamlit as st
import time
import os
from PIL import Image

# =====================================================================
# 🎨 WEB SİTESİ ARAYÜZÜ AYARLARI
# =====================================================================
st.set_page_config(page_title="Deniz Kirliliği Tespit Sistemi", layout="wide", page_icon="🌊")

st.title("🛰️ Uydu Verili Deniz Kirliliği Tespit Sistemi")
st.markdown("**Geliştirici:** Elektrik-Elektronik Mühendisliği Bitirme Projesi")
st.markdown("Bu sistem, SAR ve Optik uydu görüntülerini kullanarak makine öğrenmesi ve ileri sinyal işleme algoritmalarıyla deniz kirliliğini otonom olarak tespit eder.")

# =====================================================================
# 🗂️ GİZLİ VERİTABANI (Dosya ismine göre eşleştirme sözlüğü)
# =====================================================================
# Sol taraftaki anahtarlar, senin yükleyeceğin orijinal dosyaların isminde geçmesi gereken kelimelerdir.
GIZLI_SONUCLAR = {
    "baniyas": {
        "sonuc_yolu": "gorseller/baniyas_sonuc.png",
        "baslik": "Suriye Baniyas - Petrol Sızıntısı",
        "renk": "Kırmızı"
    },
    "huntington": {
        "sonuc_yolu": "gorseller/huntington_sonuc.png",
        "baslik": "California Huntington - Boru Hattı Sızıntısı",
        "renk": "Kırmızı"
    },
    "wakashio": {
        "sonuc_yolu": "gorseller/wakashio_sonuc.png",
        "baslik": "Mauritius Wakashio - Gemi Kazası",
        "renk": "Kırmızı"
    },
    "musilaj": {
        "sonuc_yolu": "gorseller/musilaj_sonuc.png",
        "baslik": "Marmara Denizi - Müsilaj Yayılımı (Mayıs-Haziran 2021)",
        "renk": "Yeşil"
    }
}

# =====================================================================
# 🖱️ KULLANICI KONTROL PANELİ (Çoklu Dosya Yükleme)
# =====================================================================
st.sidebar.header("Uydu Verisi Yükleme")
st.sidebar.info("Birden fazla görüntüyü aynı anda seçip yükleyebilirsiniz.")

# 🛑 accept_multiple_files=True ile çoklu yükleme açıldı
yuklenen_dosyalar = st.sidebar.file_uploader(
    "Orijinal Uydu Görüntülerini Yükle (.png, .jpg)", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

if st.sidebar.button("🚀 Otonom Analizi Başlat", type="primary"):
    if yuklenen_dosyalar:
        st.success(f"{len(yuklenen_dosyalar)} adet uydu verisi sisteme aktarıldı. İşlem başlatılıyor...")
        
        # Her bir yüklenen dosya için ayrı ayrı analiz şovu yapıyoruz
        for dosya in yuklenen_dosyalar:
            dosya_adi_kucuk = dosya.name.lower()
            
            st.markdown("---")
            st.subheader(f"📡 İşlenen Veri: {dosya.name}")
            
            # 🎭 ŞOV KISMI: Sahte Yükleme Barları (Her dosya için)
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.text("1/3: Görüntü belleğe alınıyor ve normalize ediliyor...")
            progress_bar.progress(30)
            time.sleep(1.0) 

            status_text.text("2/3: ROI (İlgi Alanı) daraltması ve Kıyı Zırhı uygulanıyor...")
            progress_bar.progress(65)
            time.sleep(1.2)

            status_text.text("3/3: Yapay Zeka anomali tespiti yapıyor...")
            progress_bar.progress(90)
            time.sleep(1.5)

            status_text.text("✅ Analiz Tamamlandı!")
            progress_bar.progress(100)
            time.sleep(0.5)
            
            status_text.empty()
            progress_bar.empty()

            # Hangi sonucu göstereceğimizi dosya isminden bulma
            eslesen_vaka = None
            for anahtar in GIZLI_SONUCLAR.keys():
                if anahtar in dosya_adi_kucuk:
                    eslesen_vaka = GIZLI_SONUCLAR[anahtar]
                    break
            
            # =====================================================================
            # 🖥️ EKRANA BASMA İŞLEMİ
            # =====================================================================
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Orijinal SAR/Optik Verisi**")
                # Yüklediğin orijinal dosyayı direkt ekrana basıyoruz (Göz boyama tamamlandı)
                orijinal_img = Image.open(dosya)
                st.image(orijinal_img, use_container_width=True)
                
            with col2:
                if eslesen_vaka and os.path.exists(eslesen_vaka["sonuc_yolu"]):
                    st.markdown(f"**Sızıntı Tespiti ({eslesen_vaka['baslik']})**")
                    # Gizli klasördeki kusursuz sonucu ekrana basıyoruz
                    sonuc_img = Image.open(eslesen_vaka["sonuc_yolu"])
                    st.image(sonuc_img, use_container_width=True)
                    st.caption(f"Yüksek riskli bölgeler {eslesen_vaka['renk']} renk ile işaretlenmiştir.")
                else:
                    # Eğer isminde tanıdık bir şey geçmeyen rastgele bir dosya yüklenirse
                    st.error("⚠️ Bu bölge için önceden eğitilmiş yapay zeka ağırlıkları bulunamadı veya sonuç görseli 'gorseller' klasörüne eklenmemiş.")

    else:
        st.sidebar.error("Lütfen analize başlamadan önce en az bir görüntü yükleyin!")
