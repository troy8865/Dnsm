import os
import shutil
import requests
import re
import yaml

# Terminal renkleri
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Web kaynaklı kanallar (örnek)
source_urls = {
    "trt1": "https://www.tabii.com/tr/watch/live/trt1?trackId=150002",
    "trthaber": "https://www.tabii.com/watch/live/trthaber?trackId=150017",
    "trtsporyildiz": "https://www.trtspor.com.tr/trtspor2",
    "nowtv": "https://www.nowtv.com.tr/canli-yayin",
    "showtv": "https://www.showtv.com.tr/canli-yayin",
    "startv": "https://www.startv.com.tr/canli-yayin",
    "tv8": "https://www.tv8.com.tr/canli-yayin",
    "tv8bucuk": "https://www.tv8bucuk.com/tv8-5-canli-yayin",
    "atv": "https://www.atv.com.tr/canli-yayin",
    "kanald": "https://www.kanald.com.tr/canli-yayin",
    "teve2": "https://www.teve2.com.tr/canli-yayin",
    "dmax": "https://www.dmax.com.tr/canli-izle",
    "a2tv": "https://www.atv.com.tr/a2tv/canli-yayin",
    "tv360": "https://www.tv360.com.tr/canli-yayin",
    "aspor": "https://www.aspor.com.tr/webtv/canli-yayin",
    "beyaztv": "https://www.beyaztv.com.tr/canli-yayin",
    "cnnturk": "https://www.cnnturk.com/canli-yayin",
    "szctv": "https://www.szctv.com.tr/canli-yayin-izle",
    "krttv": "https://www.krttv.com.tr/canli-yayin",
    "halktv": "https://halktv.com.tr/canli-yayin",
    "tv100": "https://www.tv100.com/canli-yayin"
}

# TrGoals kanalları (örnek)
KANALLAR = [
    {"dosya": "yayinzirve.m3u8", "tvg_id": "BeinSports1.tr", "kanal_adi": "Bein Sports 1 HD (VIP)"},
    {"dosya": "yayin1.m3u8", "tvg_id": "BeinSports1.tr", "kanal_adi": "Bein Sports 1 HD"},
    {"dosya": "yayinb2.m3u8", "tvg_id": "BeinSports2.tr", "kanal_adi": "Bein Sports 2 HD"},
    # ... diğer kanalları ekleyebilirsin ...
]

stream_folder = "stream"
output_file = os.path.join(stream_folder, "all_channels.m3u")

# Klasör temizleme ve oluşturma
if os.path.exists(stream_folder):
    shutil.rmtree(stream_folder)
os.makedirs(stream_folder)

def extract_m3u8(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        matches = re.findall(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*', r.text)
        return matches[0] if matches else None
    except Exception as e:
        print(f"{RED}[HATA] {url} -> {e}{RESET}")
        return None

def siteyi_bul():
    print(f"{YELLOW}[*] trgoals sitesi aranıyor...{RESET}")
    for i in range(1400, 2454):
        url = f"https://trgoals{i}.xyz/"
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200 and "channel.html?id=" in r.text:
                print(f"{GREEN}[✓] Yayın bulundu: {url}{RESET}")
                return url
        except requests.RequestException:
            continue
    print(f"{RED}[X] trgoals sitesi bulunamadı.{RESET}")
    return None

def find_baseurl(channel_url):
    try:
        r = requests.get(channel_url, timeout=10)
        r.raise_for_status()
        match = re.search(r'baseurl\s*[:=]\s*["\']([^"\']+)["\']', r.text)
        return match.group(1) if match else None
    except requests.RequestException:
        return None

def load_extra_channels(yaml_path):
    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("extra_channels", [])
    except Exception as e:
        print(f"{RED}Ek kanallar yüklenemedi: {e}{RESET}")
        return []

def write_combined_m3u8(filepath, web_links, trgoals_base_url, referer, user_agent, extra_channels):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")

        f.write("# === Web Kaynaklı Kanallar ===\n")
        for name, link in web_links.items():
            f.write(f"#EXTINF:-1,{name}\n{link}\n")

        f.write("\n# === TrGoals Kanalları ===\n")
        for kanal in KANALLAR:
            name = kanal["kanal_adi"]
            tvg_id = kanal["tvg_id"]
            dosya = kanal["dosya"]
            f.write(f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{name}",{name}\n')
            f.write(f'#EXTVLCOPT:http-user-agent={user_agent}\n')
            f.write(f'#EXTVLCOPT:http-referrer={referer}\n')
            f.write(trgoals_base_url + dosya + "\n")

        f.write("\n# === Ek Kanallar ===\n")
        for ch in extra_channels:
            name = ch.get("name")
            url = ch.get("url")
            if name and url:
                f.write(f"#EXTINF:-1,{name}\n{url}\n")

    print(f"{GREEN}[✓] {filepath} başarıyla oluşturuldu.{RESET}")

if __name__ == "__main__":
    print(f"{YELLOW}[*] Web kaynaklı linkler toplanıyor...{RESET}")
    web_links = {}
    for name, url in source_urls.items():
        m3u8 = extract_m3u8(url)
        if m3u8:
            web_links[name] = m3u8
            print(f"{GREEN}[✓] {name} eklendi.{RESET}")
        else:
            print(f"{RED}[X] {name} için link bulunamadı.{RESET}")

    print(f"{YELLOW}[*] TrGoals verisi toplanıyor...{RESET}")
    site = siteyi_bul()
    if not site:
        exit(1)
    base_url = find_baseurl(site + "/channel.html?id=yayinzirve")
    if not base_url:
        print(f"{RED}[X] Base URL alınamadı.{RESET}")
        exit(1)

    extra_channels = load_extra_channels("extra_channels.yaml")

    write_combined_m3u8(output_file, web_links, base_url, site, "Mozilla/5.0", extra_channels)
