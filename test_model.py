import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from transformers import pipeline

categories = ["Okul", "Finans", "Müzik", "Resim", "Yazılım"]
test_data = [
    ("fizik_odevi_final.pdf", "Okul"),
    ("matematik_notlari.docx", "Okul"),
    ("elektrik_faturasi_aralik.pdf", "Finans"),
    ("banka_dekontu_kira.pdf", "Finans"),
    ("tarkan_yolla.mp3", "Müzik"),
    ("sezen_aksu_vazgectim.wav", "Müzik"),
    ("tatil_fotografi_bodrum.jpg", "Resim"),
    ("vesikalik_resim.png", "Resim"),
    ("python_proje_kodu.py", "Yazılım"),
    ("main_script.js", "Yazılım"),
    ("istanbul_gezisi_raporu.png", "Okul"),
    ("internet_faturasi.pdf", "Finans")
]

print("Model yükleniyor ve test ediliyor...")

#Modeli çalıştırır
classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")

y_true = []
y_pred = []

for filename, true_label in test_data:
    clean_name = filename.replace("_", " ").split(".")[0]
    
    # Model Tahmini
    result = classifier(clean_name, categories, multi_label=False)
    predicted_label = result['labels'][0]
    
    y_true.append(true_label)
    y_pred.append(predicted_label)
    print(f"Dosya: {filename} | Gerçek: {true_label} | Tahmin: {predicted_label}")

# raporlama
acc = accuracy_score(y_true, y_pred)
print(f"\n--- SONUÇLAR ---\nAccuracy (Doğruluk): %{acc*100:.2f}")
print("\nSınıflandırma Raporu:")
print(classification_report(y_true, y_pred, target_names=categories))

# Görselleştirme
cm = confusion_matrix(y_true, y_pred, labels=categories)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', xticklabels=categories, yticklabels=categories, cmap='Blues')
plt.ylabel('Gerçek Etiketler')
plt.xlabel('Tahmin Edilen Etiketler')
plt.title('Confusion Matrix (Karmaşıklık Matrisi)')
plt.show()