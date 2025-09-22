import csv
import time
import google.generativeai as genai

# Gemini API ayarı
genai.configure(api_key="AIzaSyAd-HYq6ybwY2tWmVGldP2LTln3Vk7JDRw")
model = genai.GenerativeModel("models/gemini-2.5-flash")

# Kaç tane toplam metin olmasını istediğin
TARGET_COUNT = 285

# CSV dosya adı
OUTPUT_CSV = "dusuk_kalite_metinler.csv"

# Var olan dosyadaki son id'yi bul
def get_last_id(filename):
    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # başlığı atla
            ids = [int(row[0]) for row in reader if row]
            return max(ids) if ids else 0
    except FileNotFoundError:
        return 0

last_id = get_last_id(OUTPUT_CSV)
print(f"Var olan son ID: {last_id}")

def generate_low_quality_text(index):
    prompt = f"""
Aşağıdaki istekleri dikkate alarak kısa bir Türkçe kompozisyon yaz:

- Dil bilgisi, tutarlilik ve/veya kelime bilgisi açısından orta-yuksek kaliteli bir metin oluştur.
- Metnin toplam kalitesi 6 ile 10 arasında puanlanabilecek düzeyde olsun.
- Metin kısa veya uzun ve hatalar içerebilir ya da icermeyebilir.
- Lütfen sadece metni yaz, ekstra açıklama yapma.
- Metin 3 cumleden de , 7 cumleden de , 3-10 arasinda cumleden de olusabilir, fark etmez.
- Turkcede siklikla yapilan yazim hatalari da icerebilir , istersen
- metin 'bugun , dun , o gun, bir gun, sabah ' gibi baslayabilir, bir kisinin nelerden gectigi anlatabilir, farkli konularla ilgili olabilir metin.

Kompozisyon:
""" 
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        print(f"{index}. metin üretildi.")
        return text
    except Exception as e:
        print(f"Hata oluştu: {e}")
        return None

# Üretim döngüsü
with open(OUTPUT_CSV, mode='a', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    count = last_id
    while count < TARGET_COUNT:
        count += 1
        text = generate_low_quality_text(count)
        if text:
            writer.writerow([count, text])
        else:
            count -= 1  # hata olursa aynı id ile tekrar dene
        time.sleep(2)  # API hız limiti için bekleme

print(f"✅ Toplam {TARGET_COUNT} düşük kaliteli metin üretildi ve '{OUTPUT_CSV}' dosyasına kaydedildi.")
