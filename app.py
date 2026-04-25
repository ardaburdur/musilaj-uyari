import streamlit as st

st.set_page_config(page_title="Marmara Sea Early Warning System", page_icon="⚓", layout="centered")

st.title("🌊 Marmara Sea Environmental Monitoring & Early Warning System")
st.markdown("---")

st.write("### Welcome to the Project Dashboard")
st.write("""
This system is developed as an Electrical-Electronics Engineering graduation project. 
Click the buttons below to directly access the monitoring and analysis modules:
""")

st.write("") # Boşluk bırak

# --- TIKLANABİLİR DEV BUTONLAR (PAGE LINKS) ---
# Not: pages klasöründeki dosyalarının adları tam olarak buradaki gibi olmalı!
try:
    st.page_link("pages/1_Autonomous_Radar.py", label="🚀 START: Autonomous Radar (Live Monitoring)", icon="📡")
    st.write("")
    st.page_link("pages/2_SAR_Pollution_Analysis.py", label="🛰️ START: SAR Pollution Analysis (AI Vision)", icon="🔍")
except Exception as e:
    st.error("⚠️ Sistem Hatası: 'pages' klasörü veya içindeki dosyalar bulunamadı. Lütfen GitHub'daki klasör ve dosya isimlerini kontrol edin.")

st.markdown("---")
st.caption("Developed for EEE Graduation Project | Real-Time Dashboard")
