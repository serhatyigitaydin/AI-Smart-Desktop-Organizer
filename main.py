import os
import shutil
import threading
import pickle
import time
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog

# dark mode
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class ModernOrganizer(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere başlığı ve başlangıç boyutları
        self.title("Smart File Organizer")
        self.geometry("900x600")
        
        # solda menü sağda işlem ekranı
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Exe yapınca sorun çıkmasın
        try:
            self.current_dir = os.path.dirname(os.path.abspath(__file__))
        except:
            self.current_dir = os.getcwd()

        # Eğittiğimiz model dosyasının yolu ve varsayılan hedef klasörü
        self.model_path = os.path.join(self.current_dir, "model.pkl")
        self.target_path = ctk.StringVar(value=str(Path.home() / "Desktop"))
        self.my_model = None
        self.is_running = False

        # Arayüz elemanlarını yerleştiriyoruz
        self.init_sidebar()
        self.init_main_area()

        # Arayüz açılırken donmasın diye model yüklemeyi arka planda yaptık
        threading.Thread(target=self.load_engine, daemon=True).start()

    def init_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1) # Alt kısma boşluk bırakmak için weight verdik

        # Uygulama logosu ve ismi 
        self.lbl_logo = ctk.CTkLabel(self.sidebar, text="SMART FILE\nORGANIZER", 
                                     font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Kullanıcının düzenlenecek klasörü seçtiği buton
        self.btn_select = ctk.CTkButton(self.sidebar, text="📁 Klasör Seç", 
                                        command=self.select_directory,
                                        fg_color="#4a4a4a", hover_color="#5a5a5a")
        self.btn_select.grid(row=1, column=0, padx=20, pady=10)

        # İşlemi başlatan ana buton 
        self.btn_run = ctk.CTkButton(self.sidebar, text="▶ ANALİZİ BAŞLAT", 
                                     command=self.start_process,
                                     state="disabled",
                                     fg_color="#1f6aa5", hover_color="#144870")
        self.btn_run.grid(row=2, column=0, padx=20, pady=10)


    def init_main_area(self):
        #Sağ taraftaki log ve progress barın olduğu alan
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Üst kısımdaki path bilgisini gösteren bar
        self.top_bar = ctk.CTkFrame(self.main_frame, fg_color="#2b2b2b", corner_radius=10)
        self.top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.lbl_path_info = ctk.CTkLabel(self.top_bar, text="HEDEF:", 
                                          font=("Arial", 12, "bold"), text_color="#a1a1a1")
        self.lbl_path_info.pack(side="left", padx=(15, 5), pady=10)
        
        self.lbl_path_display = ctk.CTkLabel(self.top_bar, textvariable=self.target_path, 
                                             font=("Consolas", 12))
        self.lbl_path_display.pack(side="left", pady=10)

        # Terminal benzeri log ekranı
        self.console = ctk.CTkTextbox(self.main_frame, font=("Consolas", 12), text_color="#FFFFFF") 
        self.console.grid(row=1, column=0, sticky="nsew")
        self.console.configure(fg_color="#000000") 

        # İşlem durumu çubuğu
        self.progress = ctk.CTkProgressBar(self.main_frame, height=15)
        self.progress.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.progress.set(0)

    def select_directory(self):
        # Klasör seçme diyaloğunu açıyoruz
        path = filedialog.askdirectory()
        if path: self.target_path.set(path)

    def log(self, msg, type="INFO"):
        # Logları tiplerine göre renklendirmek yerine prefix eklndi
        prefix = "[*]" if type == "INFO" else "[!]"
        if type == "SUCCESS": prefix = "[+]"
        
        self.console.insert("end", f"{prefix} {msg}\n")
        self.console.see("end") # Scroll her zaman en aşağıyı göstermesi için

    def load_engine(self):
        #Modeli yükleyen fonksiyon. Hata olursa manuel moda geçiyor.
        self.log("Sistem başlatılıyor...", "INFO")
        self.log(f"Model yolu taranıyor: {self.model_path}")
        
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    self.my_model = pickle.load(f)
                self.log("AI Motoru yüklendi ve hazır.", "SUCCESS")
                self.btn_run.configure(state="normal", fg_color="#2cc985", hover_color="#229663")
            except Exception as e:
                self.log(f"Model yükleme hatası: {e}", "ERROR")
        else:
            # Model dosyası yoksa program çökmesin, sadece kurallarla çalışsın
            self.log("Model bulunamadı. Kural tabanlı mod aktif.", "ERROR")
            self.btn_run.configure(state="normal", text="KURALLARLA BAŞLAT", fg_color="#e59e25")

    def start_process(self):
        # Çift tıklamayı önlemek için kontrol
        if not self.is_running:
            self.is_running = True
            self.btn_run.configure(state="disabled", text="İŞLENİYOR...")
            self.progress.start()
            # Arayüz donmasın diye asıl işi threade attık
            threading.Thread(target=self.processor, daemon=True).start()

    def processor(self):
        #Dosyaları analiz edip taşıyan ana mantık bloğu.
        target = Path(self.target_path.get())
        files = [f for f in target.iterdir() if f.is_file()]
        total_files = len(files)
        
        if total_files == 0:
            self.log("Klasör boş.", "ERROR")
            self.reset_ui()
            return

        # Uzantı bazlı kesin kurallar listesi. AI'ya gerek kalmadan hızlıca ayırmak için.
        rules = {
            ".txt": "Belgeler", ".md": "Belgeler", ".lnk": "Belgeler",
            ".docx": "Ofis", ".doc": "Ofis", ".xlsx": "Ofis", ".xls": "Ofis", ".pptx": "Ofis", ".pdf": "Ofis",
            ".mp4": "Videolar", ".mov": "Videolar", ".avi": "Videolar",
            ".mp3": "Müzik", ".wav": "Müzik",
            ".jpg": "Resimler", ".png": "Resimler", ".exe": "Uygulamalar", ".zip": "Arşiv", ".rar": "Arşiv"
        }

        processed_count = 0
        self.log(f"{total_files} dosya analiz ediliyor...")

        for file in files:
            try:
                ext = file.suffix.lower()
                folder = "Diğer"
                
                # Uzantı listesinde varsa direkt oraya atıyoe
                if ext in rules:
                    folder = rules[ext]
                # Listede yoksa yapay zekaya soruyor
                elif self.my_model:
                    clean_name = file.stem.replace("_", " ")
                    folder = self.my_model.predict([clean_name])[0]
                    if folder == "Okul": folder = "Belgeler"

                # Hedef klasörü oluştur
                dest = target / folder
                dest.mkdir(exist_ok=True)
                
                # Aynı isimde dosya varsa üzerine yazmasın diye sonuna numara ekledik
                target_file = dest / file.name
                counter = 1
                while target_file.exists():
                    target_file = dest / f"{file.stem}_{counter}{file.suffix}"
                    counter += 1
                
                shutil.move(str(file), str(target_file))
                self.log(f"{file.name} -> {folder}")
                
                time.sleep(0.05) # İşlemi çok hızlı yapınca progress bar görünmüyordu, biraz bekletildi
                processed_count += 1
                
            except Exception as e:
                self.log(f"Hata: {e}", "ERROR")

        self.log("Tüm işlemler tamamlandı.", "SUCCESS")
        self.reset_ui()

    def reset_ui(self):
        # İşlem bitince butonları eski haline getir
        self.is_running = False
        self.progress.stop()
        self.progress.set(1)
        self.btn_run.configure(state="normal", text="TEKRAR BAŞLAT")

if __name__ == "__main__":
    app = ModernOrganizer()
    app.mainloop()