# auto_refresh.py

import time
from generate_dynamic_m3u8 import generate_live_m3u8
from source_urls import source_urls

def run_loop():
    while True:
        print("⏳ Güncelleme başlatıldı...")
        for name, url in source_urls.items():
            generate_live_m3u8(name, url)
        print("✅ Bekleniyor (5 dakika)...\n")
        time.sleep(300)

if __name__ == "__main__":
    run_loop()
