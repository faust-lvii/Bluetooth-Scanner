import customtkinter as ctk
import asyncio
from bleak import BleakScanner
from datetime import datetime
import threading

class BluetoothScannerApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Bluetooth Scanner")
        self.window.geometry("800x600")
        
        # Tema ayarları
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Ana frame
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Progress bar frame
        self.progress_frame = ctk.CTkFrame(self.main_frame)
        self.progress_frame.pack(pady=10, fill="x", padx=20)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(pady=5, fill="x")
        self.progress_bar.set(0)
        self.progress_bar.configure(mode="indeterminate")
        
        # Başlık
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Bluetooth Cihaz Tarayıcı",
            font=("Helvetica", 24, "bold")
        )
        self.title_label.pack(pady=20)
        
        # Tarama butonu
        self.scan_button = ctk.CTkButton(
            self.main_frame,
            text="Taramayı Başlat",
            command=self.start_scan,
            font=("Helvetica", 14),
            height=40
        )
        self.scan_button.pack(pady=10)
        
        # Durum etiketi
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Hazır",
            font=("Helvetica", 12)
        )
        self.status_label.pack(pady=5)
        
        # Sonuçlar için text kutusu
        self.results_text = ctk.CTkTextbox(
            self.main_frame,
            width=700,
            height=400,
            font=("Courier New", 12)
        )
        self.results_text.pack(pady=10, padx=10)
        
        self.scanning = False
    
    async def scan_devices(self):
        # Ana thread'de UI güncellemelerini yap
        self.window.after(0, lambda: self.results_text.delete("1.0", "end"))
        self.window.after(0, lambda: self.status_label.configure(text="Taranıyor..."))
        self.window.after(0, lambda: self.scan_button.configure(state="disabled"))
        self.window.after(0, lambda: self.progress_bar.start())
        
        try:
            devices = await BleakScanner.discover(timeout=5)
            
            def update_ui():
                if not devices:
                    self.results_text.insert("end", "Hiçbir Bluetooth cihazı bulunamadı.\n")
                else:
                    for i, device in enumerate(devices, 1):
                        # Advertisement data'yı güvenli bir şekilde al
                        adv_data = device.advertisement_data if hasattr(device, 'advertisement_data') else None
                        rssi = adv_data.rssi if adv_data else "Bilinmiyor"
                        
                        device_info = f"""
{'='*50}
Cihaz {i}:
İsim: {device.name or 'Bilinmiyor'}
Adres: {device.address}
RSSI: {rssi} dBm
"""
                        # Detaylı advertisement verilerini ekle
                        if adv_data:
                            device_info += "\nReklam Verileri:\n"
                            if adv_data.local_name:
                                device_info += f"Yerel İsim: {adv_data.local_name}\n"
                            if adv_data.manufacturer_data:
                                device_info += f"Üretici Verileri: {adv_data.manufacturer_data}\n"
                            if adv_data.service_data:
                                device_info += f"Servis Verileri: {adv_data.service_data}\n"
                            if adv_data.service_uuids:
                                device_info += f"Servis UUIDleri: {adv_data.service_uuids}\n"
                            if adv_data.tx_power:
                                device_info += f"TX Gücü: {adv_data.tx_power} dBm\n"
                        
                        self.results_text.insert("end", device_info)
                
                self.progress_bar.stop()
                self.progress_bar.set(0)
                self.status_label.configure(text="Tarama tamamlandı")
                self.scan_button.configure(state="normal")
            
            # UI güncellemelerini ana thread'de yap
            self.window.after(0, update_ui)
            
        except Exception as e:
            def show_error():
                self.results_text.insert("end", f"Hata oluştu: {str(e)}\n")
                self.progress_bar.stop()
                self.progress_bar.set(0)
                self.status_label.configure(text="Tarama tamamlandı")
                self.scan_button.configure(state="normal")
            
            # Hata mesajını ana thread'de göster
            self.window.after(0, show_error)
    
    def start_scan(self):
        # Asenkron taramayı ayrı bir thread'de başlat
        threading.Thread(target=lambda: asyncio.run(self.scan_devices())).start()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = BluetoothScannerApp()
    app.run()
