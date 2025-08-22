import requests
import yaml
import sys
import re
from collections import defaultdict

# --- Yardımcı Fonksiyonlar ---

def load_config(config_path='config.yml'):
    """
    config.yml dosyasını okur ve ayarları bir sözlük olarak döndürür.
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"HATA: Yapılandırma dosyası bulunamadı: '{config_path}'")
        sys.exit(1)
    except Exception as e:
        print(f"HATA: Yapılandırma dosyası okunurken bir hata oluştu: {e}")
        sys.exit(1)

def fetch_playlist(url):
    """
    Verilen URL'den M3U listesinin içeriğini indirir.
    """
    try:
        print(f"Kaynak liste indiriliyor: {url}")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, timeout=20, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"HATA: Kaynak liste indirilemedi: {e}")
        sys.exit(1)

def process_playlist(source_content, base_url):
    """
    İndirilen M3U içeriğini işler, kanalları ana kaynaktaki gruplara göre ayırır,
    Türk kanallarını öne alır ve yeni URL'leri oluşturur.
    """
    print("\n--- Liste İşleniyor ---")
    
    groups = defaultdict(list)
    group_order = []
    
    lines = source_content.splitlines()
    
    # --- 1. Adım: Kanalları ayrıştır ve gruplara ayır ---
    current_extinf = None
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith('#EXTINF:'):
            current_extinf = line
            continue

        if current_extinf and not line.startswith('#'):
            # Varsayılan grup adı, eğer kaynakta bulunamazsa kullanılır.
            group_title = "GRUPSUZ KANALLAR" 
            
            # Kanal adını al (raporlama için)
            channel_name_match = re.search(r',(.+)$', current_extinf)
            channel_name = channel_name_match.group(1).strip() if channel_name_match else "Bilinmeyen Kanal"

            # Hem tek hem çift tırnak ile 'group-title' etiketini ara
            match = re.search(r'group-title=(["\'])(.*?)\1', current_extinf, re.IGNORECASE)
            if match:
                title = match.group(2).strip()
                if title:
                    group_title = title
            
            print(f"-> Kanal: '{channel_name}' -> Grup: '{group_title}'")

            if group_title not in group_order:
                group_order.append(group_title)

            new_url = f"{base_url.rstrip('/')}/{line}/index.m3u8"
            
            groups[group_title].append(current_extinf)
            groups[group_title].append(new_url)
            
            current_extinf = None

    # --- 2. Adım: Yeni M3U içeriğini oluştur ve sırala ---
    print("\n--- Gruplar Sıralanıyor ---")
    output_lines = ['#EXTM3U']
    
    turkish_group_keys = []
    other_group_keys = []
    
    for key in group_order:
        key_lower = key.lower()
        if 'türk' in key_lower or 'turk' in key_lower:
            turkish_group_keys.append(key)
        else:
            other_group_keys.append(key)
            
    turkish_group_keys.sort()
    other_group_keys.sort()
    
    print(f"Türk grupları başa alınıyor: {turkish_group_keys}")
    for group_name in turkish_group_keys:
        output_lines.extend(groups[group_name])
        
    print(f"Diğer gruplar ekleniyor: {other_group_keys}")
    for group_name in other_group_keys:
        output_lines.extend(groups[group_name])

    return "\n".join(output_lines)

def save_playlist(content, output_file):
    """
    Oluşturulan yeni M3U içeriğini dosyaya kaydeder.
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\nİşlem başarıyla tamamlandı!")
        print(f"Yeni liste '{output_file}' adıyla kaydedildi.")
    except IOError as e:
        print(f"HATA: Sonuç dosyası yazılamadı: {e}")
        sys.exit(1)

# --- Ana Fonksiyon ---
def main():
    config = load_config()
    source_content = fetch_playlist(config['source_playlist_url'])
    new_playlist_content = process_playlist(source_content, config['base_url'])
    save_playlist(new_playlist_content, config['output_file'])

if __name__ == "__main__":
    main()