import streamlit as st
import os

st.set_page_config(page_title="Marmara Sea Early Warning System", page_icon="⚓", layout="centered")

st.title("🌊 Marmara Sea Environmental Monitoring & Early Warning System")
st.markdown("---")

st.write("### Welcome to the Project Dashboard")
st.write("""
This system is developed as an Electrical-Electronics Engineering graduation project. 
Click the buttons below to directly access the monitoring and analysis modules:
""")

st.write("") # Boşluk bırak

# --- TIKLANABİLİR YÖNLENDİRME BUTONLARI (PAGE LINKS) ---
# pages klasöründeki dosyalarınızın adları tam olarak buradaki gibi olmalı!
page1_path = "pages/1_Autonomous_Radar.py"
page2_path = "pages/2_SAR_Pollution_Analysis.py"

try:
    if os.path.exists(page1_path):
        st.page_link(page1_path, label="🚀 START: Autonomous Radar (Live Monitoring)", icon="📡")
    else:
        st.error(f"⚠️ Dosya Bulunamadı: '{page1_path}' dosyası pages klasöründe yok. Lütfen GitHub'daki isimleri kontrol edin.")

    st.write("")
    
    if os.path.exists(page2_path):
        st.page_link(page2_path, label="🛰️ START: SAR Pollution Analysis (AI Vision)", icon="🔍")
    else:
        st.error(f"⚠️ Dosya Bulunamadı: '{page2_path}' dosyası pages klasöründe yok. Lütfen GitHub'daki isimleri kontrol edin.")
        
except Exception as e:
    st.error(f"⚠️ Sistem Hatası: {e}")

st.markdown("---")
st.caption("Developed for EEE Graduation Project | Real-Time Dashboard")
