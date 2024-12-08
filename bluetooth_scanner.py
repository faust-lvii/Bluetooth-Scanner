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
        self.results_text.delete("1.0", "end")
        self.status_label.configure(text="Taranıyor...")
        self.scan_button.configure(state="disabled")
        
        # Progress bar'ı başlat
        self.progress_bar.start()
        
        try:
            devices = await BleakScanner.discover(timeout=5)
            
            if not devices:
                self.results_text.insert("end", "Hiçbir Bluetooth cihazı bulunamadı.\n")
            else:
                for i, device in enumerate(devices, 1):
                    device_info = f"""
{'='*50}
Cihaz {i}:
İsim: {device.name or 'Bilinmiyor'}
Adres: {device.address}
RSSI: {device.rssi} dBm
Aygıt Tipi: {device.details.get('props', {}).get('AddressType', 'Bilinmiyor')}
"""
                    if device.metadata:
                        device_info += f"Metadata: {device.metadata}\n"
                    
                    if hasattr(device, 'advertisement_data'):
                        adv_data = device.advertisement_data
                        if adv_data:
                            device_info += "\nReklam Verileri:\n"
                            for key, value in adv_data.__dict__.items():
                                if value:
                                    device_info += f"{key}: {value}\n"
                    
                    self.results_text.insert("end", device_info)
            
        except Exception as e:
            self.results_text.insert("end", f"Hata oluştu: {str(e)}\n")
        finally:
            # Progress bar'ı durdur
            self.progress_bar.stop()
            self.progress_bar.set(0)
            
        self.status_label.configure(text="Tarama tamamlandı")
        self.scan_button.configure(state="normal")
    
    def start_scan(self):
        asyncio.run(self.scan_devices())
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = BluetoothScannerApp()
    app.run()
