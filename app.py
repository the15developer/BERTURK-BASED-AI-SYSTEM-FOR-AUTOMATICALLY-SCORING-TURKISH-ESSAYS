from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
import datetime


import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import AutoModel



from transformers import BertTokenizer, BertModel
import torch.nn as nn

from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# Cihaz seçimi
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Tokenizer yükle (tokenizer klasör yolu)
#tokenizer = BertTokenizer.from_pretrained("bert_turkish_tokenizer2")

tokenizer = BertTokenizer.from_pretrained("dbmdz/bert-base-turkish-cased")

class BertSingleOutput(nn.Module):
    def __init__(self, model_name):
        super(BertSingleOutput, self).__init__()
        self.bert = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(0.3)
        self.linear = nn.Linear(self.bert.config.hidden_size, 1)

    def forward(self, input_ids, attention_mask, token_type_ids=None):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
        pooled_output = outputs.last_hidden_state[:, 0]
        pooled_output = self.dropout(pooled_output)
        logits = self.linear(pooled_output)
        return logits


# Model nesnesini oluştur
model = BertSingleOutput("dbmdz/bert-base-turkish-cased")
model.load_state_dict(torch.load("bert_turkish_model2_state_dict.pth", map_location=device))
model.to(device)
model.eval()

# Ana sayfa
@app.route('/')
def index():
    return render_template('index.html')

# Hakkımızda sayfası
@app.route('/about')
def about():
    return render_template('about.html')

# Yardım sayfası
@app.route('/help')
def help():
    return render_template('help.html')

# İletişim sayfası
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Örnekler sayfası
@app.route('/examples')
def examples():
    return render_template('examples.html')

# Puanlama API endpoint'i
# API endpoint
@app.route("/api/score", methods=["POST"])
def score_essay():
    data = request.json
    text = data.get("text", "")

    print(text)

    if not text.strip():
        return jsonify({"error": "Metin boş olamaz"}), 400

    # Tokenize et
    inputs = tokenizer(
        text,
        truncation=True,
        padding="max_length",
        max_length=256,
        return_tensors="pt"
    )

    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        output = model(**inputs)
        predicted_score = output.cpu().numpy().flatten()[0]
        print(predicted_score)

    # Modelin 0-1 aralığında olduğunu varsayıyoruz, 1-10 skalasına çevir
    overall_score = round(float(predicted_score) * 10, 2)

    return jsonify({"overall_score": overall_score})





# İletişim formu gönderimi
@app.route('/api/contact', methods=['POST'])
def handle_contact():
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')

    print(f"Yeni iletişim formu: {name} - {email} - {subject} - {message}")

    return jsonify({'status': 'success', 'message': 'Mesajınız alındı. Teşekkür ederiz!'})

# Dosya yükleme endpoint'i
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Dosya bulunamadı'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Dosya seçilmedi'}), 400

    if file:
        filename = secure_filename(file.filename)
        upload_dir = os.path.join(app.root_path, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        scores = {
            'grammar': round(min(4, max(1, len(content) / 500 * 4)), 1),
            'coherence': round(min(3, max(1, len(content) / 500 * 3)), 1),
            'vocabulary': round(min(3, max(1, len(content) / 500 * 3)), 1),
            'overall': round(min(10, max(3, len(content) / 500 * 10)), 1)
        }

        return jsonify({
            'status': 'success',
            'filename': filename,
            'content': content,
            'scores': scores
        })

# Rapor oluşturma
@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    data = request.json
    text = data.get('text', '')
    scores = data.get('scores', {})

    report = {
        'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'text': text,
        'scores': scores,
        'feedback': {
            'grammar': "Dil bilgisi kurallarına genel olarak uygun.",
            'coherence': "Metin tutarlılığı orta seviyede.",
            'vocabulary': "Kelime çeşitliliği iyi düzeyde.",
            'overall': "Genel olarak iyi bir kompozisyon."
        }
    }

    return jsonify(report)

if __name__ == '__main__':
    app.run(debug=True)
