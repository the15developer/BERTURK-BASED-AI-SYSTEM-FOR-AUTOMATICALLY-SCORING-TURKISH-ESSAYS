import pandas as pd
import random
import google.generativeai as genai
import time

# -----------------------
# 1) Gemini API ayarı
# -----------------------
genai.configure(api_key="AIzaSyAjaRftzV0zwy-If4WSDzD_uX5XeVmHp1w")  # API anahtarını buraya yaz
model = genai.GenerativeModel("models/gemini-2.5-flash")

# -----------------------
# 2) Orijinal CSV'yi oku
# -----------------------
df = pd.read_csv("Kompozisyon_Puan/metinler.csv")

# -----------------------
# 3) Rastgele 1000 metin seç
# -----------------------
sample_df = df.sample(n=1000, random_state=42)
sample_df.to_csv("Kompozisyon_Puan/metinler_sample.csv", index=False)  # Yedek olarak kaydet

# -----------------------
# 4) Gemini'ye puanlama isteği gönderme fonksiyonu
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
            cevap = cevap.strip("`")  # tüm backtick'leri sil
            # "json" ifadesini de kaldır
            cevap = cevap.replace("json", "", 1).strip()

        print("\n--- Gemini Cevabı (Temizlenmiş) ---")
        print(cevap)
        print("----------------------\n")

        # JSON parse denemesi
        import json
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
# 5) Her metni değerlendir
# -----------------------
grammar_list, coherence_list, vocab_list, total_list = [], [], [], []

for i, row in sample_df.iterrows():
    metin = row["text"]
    g, c, v, t = puanla_gemini(metin)
    grammar_list.append(g)
    coherence_list.append(c)
    vocab_list.append(v)
    total_list.append(t)

    print(f"{i} -> G:{g}, C:{c}, V:{v}, T:{t}")

    time.sleep(2)  # API hız sınırına karşı küçük bekleme

# -----------------------
# 6) Yeni CSV olarak kaydet
# -----------------------
sample_df["grammar_score"] = grammar_list
sample_df["coherence_score"] = coherence_list
sample_df["vocabulary_score"] = vocab_list
sample_df["total_score"] = total_list

sample_df.to_csv("Kompozisyon_Puan/metinler_sample_puanlanmis.csv", index=False)
print("✅ metinler_sample_puanlanmis.csv oluşturuldu.")
