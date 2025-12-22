import pandas as pd
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

mevcut_klasor = os.path.dirname(os.path.abspath(__file__))
# veri_seti.csv ile birleştirme
dosya_yolu = os.path.join(mevcut_klasor, 'veri_seti.csv')

# Veri okuma
try:
    print(f"Dosya aranıyor: {dosya_yolu}")
    df = pd.read_csv(dosya_yolu) # Artık tam adresi veriyoruz
    print(f"BAŞARILI! Toplam {len(df)} satır veri okundu.")
except FileNotFoundError:
    print("\n!!! HATA !!!")
    print(f"Dosya şu konumda bulunamadı: {dosya_yolu}")
    print("Lütfen dosya adının tam olarak 'veri_seti.csv' olduğundan emin ol.")
    print("Not: Dosya adında gizli .txt uzantısı kalmış olabilir mi?")
    exit()

# Model mimarisi
model = make_pipeline(TfidfVectorizer(), MultinomialNB())

# Model eğitimi
print("Model eğitiliyor...")
model.fit(df['text'], df['label'])

# Test
test = ["matematik ödevi", "elektrik faturası", "python kodu"]
print(f"\nTest Sonuçları: {model.predict(test)}")

#Kaydetme
kayit_yolu = os.path.join(mevcut_klasor, "model.pkl")
with open(kayit_yolu, "wb") as f:
    pickle.dump(model, f)

print(f"\nBAŞARILI: Model şuraya kaydedildi -> {kayit_yolu}")