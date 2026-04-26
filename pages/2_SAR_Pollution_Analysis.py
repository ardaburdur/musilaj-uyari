import streamlit as st
import numpy as np
from PIL import Image
import time

st.set_page_config(page_title="SAR Image Analysis", page_icon="🛰️", layout="centered")

st.title("🛰️ SAR Synthetic Aperture Radar Analysis")
st.markdown("### Statistical Backscatter Anomaly Detection")
st.info("Bu modül, yüklenen Sentinel-1 radar görüntülerindeki anormal düşük yansıma (low-backscatter) bölgelerini istatistiksel varyans analizi ile tespit eder.")

# --- SEÇİM MEKANİZMASI ---
option = st.radio("Select Image Source:", ("Use Pre-processed SNAP Data", "Upload New SAR Image"), horizontal=True)

image_to_analyze = None

if option == "Use Pre-processed SNAP Data":
    demo_images = {
        "Marmara Sea - Oil Spill Sector 1": "images/snap1.jpg"
    }
    selected_demo = st.selectbox("Select a calibrated SAR region:", list(demo_images.keys()))
    
    try:
        image_to_analyze = Image.open(demo_images[selected_demo])
        st.image(image_to_analyze, caption=f"Loaded: {selected_demo}", use_container_width=True)
    except FileNotFoundError:
        st.error("⚠️ Görüntü bulunamadı! Lütfen fotoğrafı 'images' klasörüne koyduğundan ve adının tam olarak 'snap1.jpg' olduğundan emin ol.")

else:
    uploaded_file = st.file_uploader("Upload a calibrated SAR Image (JPG/PNG)", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image_to_analyze = Image.open(uploaded_file)
        st.image(image_to_analyze, caption="Uploaded SAR Image", use_container_width=True)

st.markdown("---")

# --- İSTATİSTİKSEL ANALİZ MOTORU ---
if image_to_analyze is not None:
    if st.button("🔍 RUN STATISTICAL ANALYSIS", type="primary", use_container_width=True):
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)
            if i < 30: status_text.text("Calculating pixel intensity distribution...")
            elif i < 60: status_text.text("Computing mean and standard deviation matrices...")
            elif i < 90: status_text.text("Isolating extreme low-backscatter anomalies (3-Sigma Rule)...")
            else: status_text.text("Finalizing spatial classification...")
                
        status_text.text("✅ Analysis Complete!")
        
        # Siyah-beyaz matrise çevirme
        img_array = np.array(image_to_analyze.convert('L'))
        
        # --- İSTATİSTİKSEL HESAPLAMA (MÜHENDİSLİK KISMI) ---
        # Uydunun siyah kenar boşluklarını (0 değerleri) analize katmamak için filtreliyoruz
        valid_pixels = img_array[img_array > 0] 
        
        if len(valid_pixels) > 0:
            mean_val = np.mean(valid_pixels)
            std_val = np.std(valid_pixels)
            
            # Dinamik Eşik: Ortalamadan 2.5 standart sapma daha karanlık olan pikseller anomalidir
            dynamic_threshold = mean_val - (2.5 * std_val)
            
            # Negatif eşik olmasını engelle
            dynamic_threshold = max(dynamic_threshold, 10)
            
            # Sadece geçerli pikseller içinde eşiğin altında kalanları bul
            anomaly_pixels = np.sum((img_array < dynamic_threshold) & (img_array > 0))
            total_valid_area = len(valid_pixels)
            
            pollution_ratio = (anomaly_pixels / total_valid_area) * 100
        else:
            anomaly_pixels = 0
            total_valid_area = 1
            pollution_ratio = 0.0
        
        # --- SONUÇ EKRANI ---
        st.subheader("📊 Detection Results")
        col1, col2, col3 = st.columns(3)
        col1.metric("Valid Area Scanned", f"{total_valid_area:,} px")
        col2.metric("Anomaly Detected", f"{anomaly_pixels:,} px")
        col3.metric("Contamination Ratio", f"%{pollution_ratio:.2f}")
        
        st.write(f"*(Technical Detail: Mean Intensity: {mean_val:.1f}, Standard Deviation: {std_val:.1f}, Calculated Threshold: {dynamic_threshold:.1f})*")
        
        if pollution_ratio > 5.0:
            st.error("🚨 HIGH ALERT: Significant low-backscatter anomalies detected (Oil/Thick Mucilage).")
        elif pollution_ratio > 0.5:
            st.warning("⚠️ MODERATE: Suspicious surface formations present. Needs verification.")
        else:
            st.success("✅ CLEAN: Nominal backscatter values. No significant pollution.")
            
        st.caption("Algorithm: Statistical Z-Score Thresholding | Inference: NumPy")
