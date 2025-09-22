import pandas as pd

# 1) Mevcut veri_seti.csv'yi oku
veri_seti_dosya = "veri_seti.csv"
df_veri_seti = pd.read_csv(veri_seti_dosya)

# 2) Eklenecek yeni dosyayı oku
yeni_dosya = "metinler_sample_puanlanmis4.csv"
df_yeni = pd.read_csv(yeni_dosya)

# 3) Sadece gerekli sütunları seç (ve sıralarını eşleştir)
sutunlar = ["id", "text", "total_score", "grammar_score", "coherence_score", "vocabulary_score"]

# metinler_sample_puanlanmis4.csv'deki sütun adları farklı sırada
df_yeni = df_yeni[["text", "total_score", "grammar_score", "coherence_score", "vocabulary_score"]]

# 4) Yeni id’leri oluştur
son_id = df_veri_seti["id"].max()
df_yeni.insert(0, "id", range(son_id + 1, son_id + 1 + len(df_yeni)))

# 5) İki veri çerçevesini birleştir
df_birlesmis = pd.concat([df_veri_seti, df_yeni], ignore_index=True)

# 6) Yeni CSV’yi kaydet
df_birlesmis.to_csv("veri_seti.csv", index=False, encoding="utf-8")

print("✅ Yeni metinler veri_seti.csv dosyasına eklendi.")
