import requests
import re
import base64
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from requests.exceptions import RequestException
from time import sleep
import codecs # ROT13 için eklendi
import urllib3 # SSL uyarısını kapatmak için eklendi

# --- SSL UYARILARINI KAPAT ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Log ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- YENİ SİTE ADRESİ ---
BASE_URL = "https://www.fullhdfilmizlesene.nl"

# Ana Session objesi
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": f"{BASE_URL}/"
})
# --- SSL DOĞRULAMASINI ATLA ---
session.verify = False

# --- YENİ DECODE FONKSİYONU ---
def decode_scx_link(encoded_link):
    """ROT13 ve Base64 ile şifrelenmiş linki çözer."""
    try:
        rot13_decoded = codecs.decode(encoded_link, 'rot_13')
        return base64.b64decode(rot13_decoded).decode('utf-8')
    except Exception as e:
        logging.error(f"SCX link decode edilemedi: {e}")
        return None

# --- FARKLI OYNATICILAR İÇİN FONKSİYONLAR ---
def get_trstx_links(url):
    """TRsTX oynatıcısından M3U8 linklerini çeker."""
    try:
        page_content = session.get(url).text
        file_id = re.search(r'file":"([^"]+)"', page_content).group(1).replace("\\", "")
        api_response = session.post(f"https://trstx.org/{file_id}").json()
        
        links = []
        for item in api_response[1:]:
            title = item.get("title")
            video_file = item.get("file")
            if title and video_file:
                playlist_url = f"https://trstx.org/playlist/{video_file[1:]}.txt"
                video_link = session.post(playlist_url).text
                links.append({"quality": title, "url": video_link})
        return links
    except Exception as e:
        logging.warning(f"TRsTX linki alınamadı: {e}")
        return []

def get_rapidvid_link(url):
    """RapidVid/VidMoxy oynatıcısından M3U8 linkini çeker."""
    try:
        page_content = session.get(url).text
        match = re.search(r'file": "((?:\\x[0-9a-fA-F]{2})+)"', page_content)
        if match:
            hex_string = match.group(1).replace("\\x", "")
            return bytes.fromhex(hex_string).decode('utf-8')
        logging.warning("RapidVid için karmaşık unpack yöntemi gerekiyor, şimdilik atlanıyor.")
        return None
    except Exception as e:
        logging.warning(f"RapidVid linki alınamadı: {e}")
        return None

# --- ANA VERİ ÇEKME FONKSİYONU ---
def get_video_sources_from_slug(slug):
    """Film slug'ından tüm video kaynaklarını ve M3U8 linklerini çeker."""
    film_url = f"{BASE_URL}/film/{slug}"
    try:
        response = session.get(film_url)
        response.raise_for_status()
        
        scx_match = re.search(r'scx = (\{.*?\});', response.text)
        if not scx_match:
            logging.warning(f"{slug}: SCX verisi bulunamadı.")
            return []

        scx_data = json.loads(scx_match.group(1))
        video_links = []
        
        for source_key, source_data in scx_data.items():
            if isinstance(source_data, dict) and 'sx' in source_data and 't' in source_data['sx']:
                encoded_links = source_data['sx']['t']
                links_to_process = []
                if isinstance(encoded_links, list):
                    links_to_process.extend(encoded_links)
                elif isinstance(encoded_links, dict):
                    links_to_process.extend(encoded_links.values())

                for encoded_link in links_to_process:
                    decoded_url = decode_scx_link(encoded_link)
                    if not decoded_url: continue

                    if "trstx.org" in decoded_url:
                        tr_links = get_trstx_links(decoded_url)
                        for link_info in tr_links:
                            video_links.append(link_info['url'])
                    elif "rapidvid.net" in decoded_url or "vidmoxy.com" in decoded_url:
                        rapid_link = get_rapidvid_link(decoded_url)
                        if rapid_link: video_links.append(rapid_link)
                    elif decoded_url.endswith('.m3u8'):
                        video_links.append(decoded_url)
        
        return list(set(video_links))

    except RequestException as e:
        logging.error(f"{slug} için veri alınamadı: {e}")
        return []

def get_film_details(slug):
    """Film slug'ından başlık, poster gibi detayları çeker."""
    film_url = f"{BASE_URL}/film/{slug}"
    try:
        doc = session.get(film_url).text
        title = re.search(r'<div class="izle-titles">.*?<h1>(.*?)</h1>', doc, re.DOTALL).group(1).strip()
        poster = re.search(r'<div class="film-poster">.*?<img.*?data-src="(.*?)".*?>', doc, re.DOTALL).group(1)
        genre_match = re.search(r'<span class="dt">Tür</span>.*?<a.*?>(.*?)</a>', doc, re.DOTALL)
        genre = genre_match.group(1) if genre_match else "Bilinmeyen"
        return title, poster, genre
    except Exception:
        return slug.replace("-", " ").title(), None, "Bilinmeyen"

def build_m3u(pages=1, output_file="yelon.m3u", max_workers=10):
    """M3U çalma listesini oluşturur."""
    all_slugs = []
    for page_num in range(1, pages + 1):
        try:
            page_url = f"{BASE_URL}/yeni-filmler/{page_num}"
            response = session.get(page_url)
            slugs_on_page = re.findall(r'<a href="' + BASE_URL + r'/film/([^/]+)/"', response.text)
            if not slugs_on_page: break
            all_slugs.extend(list(set(slugs_on_page)))
            logging.info(f"Sayfa {page_num}: {len(set(slugs_on_page))} slug bulundu.")
            sleep(0.5)
        except Exception as e:
            logging.error(f"Sayfa {page_num} taranırken hata: {e}")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        
        def process_slug(slug):
            title, poster, genre = get_film_details(slug)
            video_urls = get_video_sources_from_slug(slug)
            
            if video_urls:
                video_url = video_urls[0]
                f.write(f'#EXTINF:-1 tvg-id="{slug}" tvg-logo="{poster}" group-title="{genre}",{title}\n')
                f.write(video_url + "\n")
                logging.info(f"{title} eklendi ✅")
            else:
                logging.warning(f"{title} için video kaynağı bulunamadı ⚠️")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(process_slug, all_slugs)

if __name__ == "__main__":
    build_m3u(pages=100, max_workers=5)