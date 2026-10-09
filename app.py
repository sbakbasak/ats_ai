import streamlit as st
import json
from openai import OpenAI

st.set_page_config(page_title="LinkedIn ATS Gap Analyzer", layout="wide")
st.title("🎯 LinkedIn ATS & İş İlanı Uyum Analizi")

# OpenAI API Key Girişi
api_key = st.sidebar.text_input("OpenAI API Key", type="password")

if not api_key:
    st.info("Lütfen sol menüden OpenAI API Key giriniz.")
    st.stop()

client = OpenAI(api_key=api_key)

# Oturum Hafızası (Session State)
if "ats_profile" not in st.session_state:
    st.session_state.ats_profile = None

# Sol Sütun: Profil Yapılandırma | Sağ Sütun: İlan Analizi
col1, col2 = st.columns(2)

with col1:
    st.header("1. Profil Verisi (Tek Seferlik)")
    raw_profile = st.text_area("LinkedIn Profil Metninizi Buraya Yapıştırın:", height=300)
    
    if st.button("Profili Kaydet & ATS Formatına Çevir"):
        with st.spinner("Profiliniz dönüştürülüyor..."):
            prompt = f"Aşağıdaki LinkedIn profilini ATS sistemine uygun JSON formatında özetle:\n{raw_profile}"
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.ats_profile = response.choices[0].message.content
            st.success("Profil başarıyla kaydedildi!")

with col2:
    st.header("2. İlan Analizi")
    job_desc = st.text_area("Başvurulacak İlan Metnini Yapıştırın:", height=300)
    
    if st.button("Uyum Analizi Yap"):
        if not st.session_state.ats_profile:
            st.warning("Lütfen önce sol taraftan profilinizi kaydedin.")
        else:
            with st.spinner("İlan ile profil kıyaslanıyor..."):
                analysis_prompt = f"""
                Aşağıdaki ATS Profil verisi ile İş İlanını bir ATS sistemi gibi kıyasla.
                
                ATS Profil:
                {st.session_state.ats_profile}
                
                İş İlanı:
                {job_desc}
                
                Çıktıyı Türkçe olarak şu JSON formatında ver:
                {{
                  "uyum_skoru": 80,
                  "eksik_beceriler": ["..."],
                  "terminoloji_farklari": ["..."],
                  "oneriler": ["..."]
                }}
                """
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    response_format={"type": "json_object"},
                    messages=[{"role": "user", "content": analysis_prompt}]
                )
                result = json.loads(res.choices[0].message.content)
                
                st.metric("Uyum Skoru", f"%{result.get('uyum_skoru', 0)}")
                st.subheader("🔴 Eksik Beceriler")
                st.write(result.get("eksik_beceriler", []))
                st.subheader("🟡 Terminoloji Uyumsuzlukları")
                st.write(result.get("terminoloji_farklari", []))
                st.subheader("💡 Profil İçin Öneriler")
                st.write(result.get("oneriler", []))
