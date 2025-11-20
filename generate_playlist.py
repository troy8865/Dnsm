import os
import shutil
import requests
import re
import sys
import yaml

# === Terminal renkleri ===
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# === Klasör ve dosya ayarları ===
stream_folder = "stream"
output_file = os.path.join(stream_folder, "all_channels.m3u")
extra_yaml_path = "extra_channels.yaml"

# === Genel ayarlar ===
HEADERS = {"User-Agent": "Mozilla/5.0"}

# === Web kaynakları ===
source_urls = {
    "tabii": "https://www.tabii.com/tr/watch/live/trt1?trackId=150002",
    "nowtv": "https://www.nowtv.com.tr/canli-yayin",
    "showtv": "https://www.showtv.com.tr/canli-yayin",
    "htspor": "https://www.htspor.com/canli-yayin",
    "tv8": "https://www.tv8.com.tr/canli-yayin",
    "tv8bucuk": "https://www.tv8bucuk.com/tv8-5-canli-yayin",
    "atv": "https://www.atv.com.tr/canli-yayin",
    "kanald": "https://www.kanald.com.tr/canli-yayin",
    "teve2": "https://www.teve2.com.tr/canli-yayin",
    "dmax": "https://www.dmax.com.tr/canli-izle",
    "tv360": "https://www.tv360.com.tr/canli-yayin",
    "beyaztv": "https://www.beyaztv.com.tr/canli-yayin",
    "ntv": "https://puhutv.com/ntv-canli-yayin",
    "ekolspor": "https://www.ekoltv.com.tr/canli-yayin",
    "halktv": "https://halktv.com.tr/canli-yayin",
}

# === TrGoals kanal listesi ===
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

# === SelçukTV kanalları ===
CHANNELS = [
    {"id": "bein1", "source_id": "selcukbeinsports1", "name": "BeIN Sports 1", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/5rhmw31628798883.png", "group": "Spor"},
    {"id": "bein2", "source_id": "selcukbeinsports2", "name": "BeIN Sports 2", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/7uv6x71628799003.png", "group": "Spor"},
    {"id": "bein3", "source_id": "selcukbeinsports3", "name": "BeIN Sports 3", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/u3117i1628798857.png", "group": "Spor"},
    {"id": "bein4", "source_id": "selcukbeinsports4", "name": "BeIN Sports 4", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/2ktmcp1628798841.png", "group": "Spor"},
    {"id": "bein5", "source_id": "selcukbeinsports5", "name": "BeIN Sports 5", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/BeIn_Sports_5_US.png", "group": "Spor"},
    {"id": "beinmax1", "source_id": "selcukbeinsportsmax1", "name": "BeIN Sports Max 1", "logo": "https://assets.bein.com/mena/sites/3/2015/06/beIN_SPORTS_MAX1_DIGITAL_Mono.png", "group": "Spor"},
    {"id": "beinmax2", "source_id": "selcukbeinsportsmax2", "name": "BeIN Sports Max 2", "logo": "http://tvprofil.com/img/kanali-logo/beIN_Sports_MAX_2_TR_logo_v2.png?1734011568", "group": "Spor"},
    {"id": "tivibu1", "source_id": "selcuktivibuspor1", "name": "Tivibu Spor 1", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/qadnsi1642604437.png", "group": "Spor"},
    {"id": "tivibu2", "source_id": "selcuktivibuspor2", "name": "Tivibu Spor 2", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/kuasdm1642604455.png", "group": "Spor"},
    {"id": "tivibu3", "source_id": "selcuktivibuspor3", "name": "Tivibu Spor 3", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/slwrz41642604502.png", "group": "Spor"},
    {"id": "tivibu4", "source_id": "selcuktivibuspor4", "name": "Tivibu Spor 4", "logo": "https://r2.thesportsdb.com/images/media/channel/logo/59bqi81642604517.png", "group": "Spor"},
    {"id": "ssport1", "source_id": "selcukssport", "name": "S Sport 1", "logo": "https://itv224226.tmp.tivibu.com.tr:6430/images/poster/20230302923239.png", "group": "Spor"},
    {"id": "ssport2", "source_id": "selcukssport2", "name": "S Sport 2", "logo": "https://itv224226.tmp.tivibu.com.tr:6430/images/poster/20230302923321.png", "group": "Spor"},
    {"id": "smart1", "source_id": "selcuksmartspor", "name": "Smart Spor 1", "logo": "https://dsmart-static-v2.ercdn.net//resize-width/1920/content/p/el/11909/Thumbnail.png", "group": "Spor"},
    {"id": "smart2", "source_id": "selcuksmartspor2", "name": "Smart Spor 2", "logo": "https://www.dsmart.com.tr/api/v1/public/images/kanallar/SPORSMART2-gri.png", "group": "Spor"},
    {"id": "aspor", "source_id": "selcukaspor", "name": "A Spor", "logo": "https://feo.kablowebtv.com/resize/168A635D265A4328C2883FB4CD8FF/0/0/Vod/HLS/9d28401f-2d4e-4862-85e2-69773f6f45f4.png", "group": "Spor"},
    {"id": "eurosport1", "source_id": "selcukeurosport1", "name": "Eurosport 1", "logo": "https://feo.kablowebtv.com/resize/168A635D265A4328C2883FB4CD8FF/0/0/Vod/HLS/54cad412-5f3a-4184-b5fc-d567a5de7160.png", "group": "Spor"},
    {"id": "eurosport2", "source_id": "selcukeurosport2", "name": "Eurosport 2", "logo": "https://feo.kablowebtv.com/resize/168A635D265A4328C2883FB4CD8FF/0/0/Vod/HLS/a4cbdd15-1509-408f-a108-65b8f88f2066.png", "group": "Spor"},
]


# === Yeni Domain Alma Fonksiyonları ===
def get_trgoals_domain():
    url = "https://raw.githubusercontent.com/troy8865/domain_1/refs/heads/main/domain.txt"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            txt = r.text.strip().replace("guncel_domain=", "")
            return txt.strip()
    except:
        pass
    return None


def get_selcuk_domain():
    url = "https://raw.githubusercontent.com/troy8865/domain_2/refs/heads/main/selcuk_sports_guncel_domain.txt"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            txt = r.text.strip().replace("guncel_domain=", "")
            return txt.strip()
    except:
        pass
    return None


# === Yardımcı Fonksiyonlar ===
def extract_m3u8(url):
    try:
        r = requests.get(url, timeout=10)
        matches = re.findall(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*', r.text)
        return matches[0] if matches else None
    except:
        return None


def find_baseurl(channel_url):
    try:
        r = requests.get(channel_url, timeout=10)
        match = re.search(r'baseurl\s*[:=]\s*["\']([^"\']+)["\']', r.text)
        return match.group(1) if match else None
    except:
        return None


def find_stream_domain(html):
    match = re.search(r'https?://(main\.uxsyplayer[0-9a-zA-Z\-]+\.click)', html)
    return f"https://{match.group(1)}" if match else None


def extract_base_url(html):
    match = re.search(r'this\.adsBaseUrl\s*=\s*[\'"]([^\'"]+)', html)
    return match.group(1) if match else None


def fetch_sporcafe_streams(domain, referer):
    result = []
    for ch in CHANNELS:
        full_url = f"{domain}/index.php?id={ch['source_id']}"
        try:
            r = requests.get(full_url, headers={**HEADERS, "Referer": referer}, timeout=5)
            if r.status_code == 200:
                base = extract_base_url(r.text)
                if base:
                    stream = f"{base}{ch['source_id']}/playlist.m3u8"
                    result.append((ch, stream))
        except:
            continue
    return result


def load_extra_channels(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
                return data.get("extra_channels", [])
            except:
                return []
    return []


# === M3U Birleştirme ===
def write_combined_m3u8(filepath, web_links, trgoals_base, trgoals_ref, sporcafe_links, sporcafe_ref, extra_channels):

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")

        f.write("\n# === Web Kaynakları ===\n")
        for name, link in web_links.items():
            f.write(f"#EXTINF:-1,{name}\n{link}\n")

        f.write("\n# === TrGoals Kanalları ===\n")
        for kanal in KANALLAR:
            f.write(f'#EXTINF:-1 tvg-id="{kanal["tvg_id"]}" group-title="TrGoals",{kanal["kanal_adi"]}\n')
            f.write(f'#EXTVLCOPT:http-referrer={trgoals_ref}\n')
            f.write(trgoals_base + kanal["dosya"] + "\n")

        f.write("\n# === Selçuk / Sporcafe Kanalları ===\n")
        for ch, url in sporcafe_links:
            f.write(f'#EXTINF:-1 tvg-id="{ch["id"]}" group-title="Selçuk",{ch["name"]}\n')
            f.write(f'#EXTVLCOPT:http-referrer={sporcafe_ref}\n')
            f.write(url + "\n")

        f.write("\n# === Manuel Ek Kanallar ===\n")
        for ch in extra_channels:
            f.write(f'#EXTINF:-1 tvg-id="{ch["tvg_id"]}",{ch["kanal_adi"]}\n')
            f.write(ch["url"] + "\n")

    print(f"{GREEN}[✓] M3U dosyası oluşturuldu: {filepath}{RESET}")


# === ANA AKIŞ ===
if __name__ == "__main__":

    # Klasörü temizle
    if os.path.exists(stream_folder):
        shutil.rmtree(stream_folder)
    os.makedirs(stream_folder)

    print(f"{YELLOW}[*] Web kaynakları taranıyor...{RESET}")
    web_links = {}
    for name, url in source_urls.items():
        link = extract_m3u8(url)
        if link:
            web_links[name] = link
            print(f"{GREEN}[✓] {name} bulundu{RESET}")
        else:
            print(f"{RED}[X] {name} bulunamadı{RESET}")

    # === TrGoals Domain Alma ===
    print(f"{YELLOW}[*] TrGoals domain alınıyor...{RESET}")
    trgoals_ref = get_trgoals_domain()
    trgoals_base = ""

    if trgoals_ref:
        print(f"{GREEN}[✓] TrGoals domain: {trgoals_ref}{RESET}")
        trgoals_base = find_baseurl(trgoals_ref + "/channel.html?id=yayinzirve") or ""
    else:
        print(f"{RED}[X] TrGoals domain bulunamadı!{RESET}")

    # === Selçuk / Sporcafe Domain Alma ===
    print(f"{YELLOW}[*] Selçuk/Sporcafe domain alınıyor...{RESET}")
    referer = get_selcuk_domain()
    sporcafe_links = []

    if referer:
        print(f"{GREEN}[✓] Selçuk domain: {referer}{RESET}")
        try:
            html = requests.get(referer, headers=HEADERS, timeout=5).text
            domain = find_stream_domain(html)
            if domain:
                sporcafe_links = fetch_sporcafe_streams(domain, referer)
            else:
                print(f"{RED}[X] Yayın base domain bulunamadı!{RESET}")
        except:
            print(f"{RED}[X] Selçuk domain okunamadı!{RESET}")
    else:
        print(f"{RED}[X] Selçuk domain bulunamadı!{RESET}")

    extra_channels = load_extra_channels(extra_yaml_path)

    write_combined_m3u8(
        output_file,
        web_links,
        trgoals_base,
        trgoals_ref,
        sporcafe_links,
        referer or "",
        extra_channels
    )
