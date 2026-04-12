import streamlit as st
import numpy as np
import pandas as pd
import requests
from sklearn.ensemble import RandomForestClassifier

# Sayfa Ayarları
st.set_page_config(page_title="Marmara Erken Uyarı", page_icon="🌊", layout="wide")
st.title("🌊 Marmara Denizi Müsilaj Erken Uyarı Sistemi")

# 1. Yapay Zeka Eğitimi (Arka Plan)
@st.cache_resource
def modeli_egit():
    np.random.seed(42)
    temp = np.random.uniform(8, 28, 1500)
    chl = np.random.uniform(0.1, 12.0, 1500)
    poll = np.random.uniform(10, 100, 1500)
    oxy = np.random.uniform(1.0, 10.0, 1500)
    wind = np.random.uniform(0, 15, 1500)
    
    risk = (temp > 15) & (chl > 3.0) & (poll > 55) & (wind < 4.0) & (oxy < 5.5)
    y = np.where(risk, 1, 0)
    df = pd.DataFrame({'Sıcaklık': temp, 'Klorofil_a': chl, 'Kirlilik': poll, 'Oksijen': oxy, 'Rüzgar': wind})
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(df, y)
    return model

model = modeli_egit()

# 2. Canlı Hava Durumu
@st.cache_data(ttl=600)
def hava_durumu_cek():
    try:
        res = requests.get("https://api.open-meteo.com/v1/forecast?latitude=40.8&longitude=28.5&current_weather=true").json()
        return res['current_weather']['temperature'], res['current_weather']['windspeed'] / 3.6
    except:
        return 14.5, 4.2

anlik_sicaklik, anlik_ruzgar = hava_durumu_cek()

# 3. Kontrol Paneli (Sol Menü)
st.sidebar.header("🎛️ Oşinografik Sensörler")
st.sidebar.info("Meteorolojik veriler API'den canlı çekilmektedir. Kimyasal değerleri aşağıdan simüle edebilirsiniz.")

klorofil = st.sidebar.slider("Klorofil (µg/L)", 0.0, 15.0, 2.0, 0.1)
kirlilik = st.sidebar.slider("Kirlilik Endeksi", 0.0, 100.0, 30.0, 1.0)
oksijen = st.sidebar.slider("Oksijen (mg/L)", 0.0, 12.0, 7.0, 0.1)

# 4. Analiz ve Sonuç
st.subheader("📡 Canlı Veri İstasyonu (Marmara)")
col1, col2 = st.columns(2)
col1.metric("API Sıcaklık", f"{anlik_sicaklik} °C")
col2.metric("API Rüzgar", f"{anlik_ruzgar:.1f} m/s")

veriler = pd.DataFrame({'Sıcaklık': [anlik_sicaklik], 'Klorofil_a': [klorofil], 'Kirlilik': [kirlilik], 'Oksijen': [oksijen], 'Rüzgar': [anlik_ruzgar]})
olasilik = model.predict_proba(veriler)[0][1] * 100

st.markdown("---")
st.subheader("🤖 Yapay Zeka Karar Mekanizması")

if olasilik > 70:
    st.error(f"🚨 KRİTİK ALARM: %{olasilik:.1f} İhtimalle Müsilaj Riski!")
elif olasilik > 40:
    st.warning(f"⚠️ UYARI: %{olasilik:.1f} İhtimalle Değerler Riskli.")
else:
    st.success(f"✅ GÜVENLİ: %{olasilik:.1f} İhtimalle Sular Temiz.")
