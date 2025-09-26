import os
import shutil
import requests
import re
import sys

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

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

KANALLAR = [
    {"dosya": "yayinzirve.m3u8", "tvg_id": "BeinSports1.tr", "kanal_adi": "Bein Sports 1 HD (VIP)"},
    {"dosya": "yayin1.m3u8", "tvg_id": "BeinSports1.tr", "kanal_adi": "Bein Sports 1 HD"},
    {"dosya": "yayinb2.m3u8", "tvg_id": "BeinSports2.tr", "kanal_adi": "Bein Sports 2 HD"},
    {"dosya": "yayinb3.m3u8", "tvg_id": "BeinSports3.tr", "kanal_adi": "Bein Sports 3 HD"},
    {"dosya": "yayinb4.m3u8", "tvg_id": "BeinSports4.tr", "kanal_adi": "Bein Sports 4 HD"},
    {"dosya": "yayinb5.m3u8", "tvg_id": "BeinSports5.tr", "kanal_adi": "Bein Sports 5 HD"},
    {"dosya": "yayinbm1.m3u8", "tvg_id": "BeinMax1.tr", "kanal_adi": "Bein Max 1 HD"},
    {"dosya": "yayinbm2.m3u8", "tvg_id": "BeinMax2.tr", "kanal_adi": "Bein Max 2 HD"},
    {"dosya": "yayinss.m3u8", "tvg_id": "SSport1.tr", "kanal_adi": "S Sport 1 HD"},
    {"dosya": "yayinss2.m3u8", "tvg_id": "SSport2.tr", "kanal_adi": "S Sport 2 HD"},
    {"dosya": "yayinssp2.m3u8", "tvg_id": "SSportPlus.tr", "kanal_adi": "S Sport Plus HD"},
    {"dosya": "yayint1.m3u8", "tvg_id": "TivibuSpor1.tr", "kanal_adi": "Tivibu Spor 1 HD"},
    {"dosya": "yayint2.m3u8", "tvg_id": "TivibuSpor2.tr", "kanal_adi": "Tivibu Spor 2 HD"},
    {"dosya": "yayint3.m3u8", "tvg_id": "TivibuSpor3.tr", "kanal_adi": "Tivibu Spor 3 HD"},
    {"dosya": "yayinsmarts.m3u8", "tvg_id": "SmartSpor1.tr", "kanal_adi": "Smart Spor 1 HD"},
    {"dosya": "yayinsms2.m3u8", "tvg_id": "SmartSpor2.tr", "kanal_adi": "Smart Spor 2 HD"},
    {"dosya": "yayintrtspor.m3u8", "tvg_id": "TRTSpor.tr", "kanal_adi": "TRT Spor HD"},
    {"dosya": "yayintrtspor2.m3u8", "tvg_id": "TRTSporYildiz.tr", "kanal_adi": "TRT Spor Yıldız HD"},
    {"dosya": "yayinas.m3u8", "tvg_id": "ASpor.tr", "kanal_adi": "A Spor HD"},
    {"dosya": "yayinatv.m3u8", "tvg_id": "ATV.tr", "kanal_adi": "ATV HD"},
    {"dosya": "yayintv8.m3u8", "tvg_id": "TV8.tr", "kanal_adi": "TV8 HD"},
    {"dosya": "yayintv85.m3u8", "tvg_id": "TV85.tr", "kanal_adi": "TV8.5 HD"},
    {"dosya": "yayinnbatv.m3u8", "tvg_id": "NBATV.tr", "kanal_adi": "NBA TV HD"},
    {"dosya": "yayinex1.m3u8", "tvg_id": "ExxenSpor1.tr", "kanal_adi": "Exxen Spor 1 HD"},
    {"dosya": "yayinex2.m3u8", "tvg_id": "ExxenSpor2.tr", "kanal_adi": "Exxen Spor 2 HD"},
    {"dosya": "yayinex3.m3u8", "tvg_id": "ExxenSpor3.tr", "kanal_adi": "Exxen Spor 3 HD"},
    {"dosya": "yayinex4.m3u8", "tvg_id": "ExxenSpor4.tr", "kanal_adi": "Exxen Spor 4 HD"},
    {"dosya": "yayinex5.m3u8", "tvg_id": "ExxenSpor5.tr", "kanal_adi": "Exxen Spor 5 HD"},
    {"dosya": "yayinex6.m3u8", "tvg_id": "ExxenSpor6.tr", "kanal_adi": "Exxen Spor 6 HD"},
    {"dosya": "yayinex7.m3u8", "tvg_id": "ExxenSpor7.tr", "kanal_adi": "Exxen Spor 7 HD"},
    {"dosya": "yayinex8.m3u8", "tvg_id": "ExxenSpor8.tr", "kanal_adi": "Exxen Spor 8 HD"},
]

stream_folder = "stream"
output_file = os.path.join(stream_folder, "all_channels.m3u")

if os.path.exists(stream_folder):
    shutil.rmtree(stream_folder)
os.makedirs(stream_folder)

def extract_m3u8(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        matches = re.findall(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*', r.text)
        return matches[0] if matches else None
    except Exception:
        return None

def siteyi_bul():
    for i in range(1400, 2454):
        url = f"https://trgoals{i}.xyz/"
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200 and "channel.html?id=" in r.text:
                return url
        except:
            continue
    return None

def find_baseurl(channel_url):
    try:
        r = requests.get(channel_url, timeout=10)
        r.raise_for_status()
        match = re.search(r'baseurl\s*[:=]\s*["\']([^"\']+)["\']', r.text)
        return match.group(1) if match else None
    except:
        return None

def write_combined_m3u8(filepath, web_links, trgoals_base_url, referer, user_agent):
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

if __name__ == "__main__":
    web_links = {}
    for name, url in source_urls.items():
        m3u8 = extract_m3u8(url)
        if m3u8:
            web_links[name] = m3u8

    site = siteyi_bul()
    if not site:
        sys.exit(1)

    base_url = find_baseurl(site + "/channel.html?id=yayinzirve")
    if not base_url:
        sys.exit(1)

    write_combined_m3u8(output_file, web_links, base_url, site, "Mozilla/5.0")