import pandas as pd
import google.generativeai as genai
import time
import json

# -----------------------
# 1) Gemini API ayarı
# -----------------------
genai.configure(api_key="AIzaSyBloZc7_tAg1E7yGlXbtKlNqnsmpMfpFA8")
model = genai.GenerativeModel("models/gemini-2.5-flash")

# -----------------------
# 2) Orijinal CSV'yi oku
# -----------------------
df = pd.read_csv("metinler2.csv")

# -----------------------
# 3) Rastgele 500 metin seç
# -----------------------
sample_df = df.sample(n=500, random_state=42).reset_index(drop=True)
# Başlangıçta sadece seçilen metinleri ve boş puan sütunlarını yaz
sample_df["grammar_score"] = None
sample_df["coherence_score"] = None
sample_df["vocabulary_score"] = None
sample_df["total_score"] = None
sample_df.to_csv("metinler_sample_puanlanmis2.csv", index=False)

# -----------------------
# 4) Gemini'ye puanlama fonksiyonu
# -----------------------
def puanla_gemini(metin):
    prompt = f"""
    Aşağıdaki Türkçe kompozisyonu üç ölçüte göre değerlendir:
    - Dil bilgisi (0-4)
    - Tutarlılık (0-3)
    - Kelime bilgisi (0-3)

    Her puanı sadece rakam olarak ver. Son olarak, bu puanları normalize edip (dil bilgisi + tutarlılık + kelime bilgisi)*10/10 şeklinde 0-10 arasında bir toplam puan üret.
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
# 5) Metinleri değerlendir ve anlık kaydet
# -----------------------
CSV_DOSYA = "metinler_sample_puanlanmis2.csv"

for i, row in sample_df.iterrows():
    if pd.isna(row["total_score"]):  # Daha önce puanlanmamışsa işle
        metin = row["text"]
        g, c, v, t = puanla_gemini(metin)

        print(f"{i} -> G:{g}, C:{c}, V:{v}, T:{t}")

        # CSV'yi yükle, satırı güncelle, tekrar kaydet
        df_kayit = pd.read_csv(CSV_DOSYA)
        df_kayit.at[i, "grammar_score"] = g
        df_kayit.at[i, "coherence_score"] = c
        df_kayit.at[i, "vocabulary_score"] = v
        df_kayit.at[i, "total_score"] = t
        df_kayit.to_csv(CSV_DOSYA, index=False)

        time.sleep(2)  # API hız limiti için bekleme

print("✅ İşlem tamamlandı, tüm puanlar kaydedildi.")
