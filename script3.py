import pandas as pd
import google.generativeai as genai
import time
import json

# -----------------------
# 1) Gemini API ayarı
# -----------------------
genai.configure(api_key="AIzaSyAd-HYq6ybwY2tWmVGldP2LTln3Vk7JDRw")
model = genai.GenerativeModel("models/gemini-2.5-flash")

# -----------------------
# 2) Orijinal CSV'yi oku ve 246 sonrası satırları filtrele
# -----------------------
CSV_DOSYA = "./dusuk_kalite_metinler.csv"
df = pd.read_csv(CSV_DOSYA)

# Sadece id >= 246 olan satırları al
df = df[df["id"] >= 246].reset_index(drop=True)

# -----------------------
# 3) Puan sütunları yoksa ekle
# -----------------------
for col in ["grammar_score", "coherence_score", "vocabulary_score", "total_score"]:
    if col not in df.columns:
        df[col] = None

# -----------------------
# 4) CSV'yi ilk kez kaydet (puansız haliyle)
# -----------------------
df.to_csv("metinler_sample_puanlanmis4.csv", index=False)

# -----------------------
# 5) Gemini'ye puanlama fonksiyonu
# -----------------------
def puanla_gemini(metin):
    prompt = f"""
    Aşağıdaki Türkçe kompozisyonu üç ölçüte göre değerlendir:
    - Dil bilgisi (0-4)
    - Tutarlılık (0-3)
    - Kelime bilgisi (0-3)

    Her puanı sadece rakam olarak ver. Son olarak, bu puanları normalize edip 
    (dil bilgisi + tutarlılık + kelime bilgisi)*10/10 şeklinde 0-10 arasında 
    bir toplam puan üret.

    Yanıtı şu JSON formatında ver:
    {{
        "grammar_score": X,
        "coherence_score": Y,
        "vocabulary_score": Z,
        "total_score": T
    }}

    Kompozisyon:
    {metin}
    """
    try:
        response = model.generate_content(prompt)
        cevap = response.text.strip()

        # Kod bloğu işaretlerini temizle
        if cevap.startswith("```"):
            cevap = cevap.strip("`")
            cevap = cevap.replace("json", "", 1).strip()

        puanlar = json.loads(cevap)
        return (
            puanlar.get("grammar_score", None),
            puanlar.get("coherence_score", None),
            puanlar.get("vocabulary_score", None),
            puanlar.get("total_score", None)
        )
    except Exception as e:
        print("Hata:", e)
        return (None, None, None, None)

# -----------------------
# 6) Tüm metinler için puanlama
# -----------------------
for i, row in df.iterrows():
    if pd.isna(row["total_score"]):  # Daha önce puanlanmamışsa
        # Metin sütun adınızı kontrol edin
        metin_sutunu = "text" if "text" in df.columns else "generated_text"
        metin = row[metin_sutunu]

        g, c, v, t = puanla_gemini(metin)
        print(f"{row['id']} -> G:{g}, C:{c}, V:{v}, T:{t}")

        # DataFrame'i güncelle
        df.at[i, "grammar_score"] = g
        df.at[i, "coherence_score"] = c
        df.at[i, "vocabulary_score"] = v
        df.at[i, "total_score"] = t

        # Anlık CSV güncelle
        df.to_csv("metinler_sample_puanlanmis4.csv", index=False)

        time.sleep(2)  # API hız sınırı için bekleme

print("✅ İşlem tamamlandı, tüm puanlar kaydedildi.")
