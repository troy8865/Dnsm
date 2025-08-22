import requests
import yaml
import sys
import re

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

def parse_source_playlist(source_content):
    """
    Kaynak M3U içeriğini analiz eder ve yapılandırılmış bir kanal listesi döndürür.
    Her kanal bir sözlük objesidir: {'group': '...', 'extinf': '...', 'url': '...'}
    """
    print("\n--- Kaynak Liste Analiz Ediliyor ---")
    channels = []
    lines = source_content.splitlines()
    
    # Satırları gezerek #EXTINF ve URL çiftlerini bul
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith('#EXTINF:'):
            extinf_line = line
            # Bir sonraki satırın URL olduğunu varsay
            if i + 1 < len(lines):
                url_line = lines[i+1].strip()
                
                # URL satırı geçerli mi kontrol et (boş veya başka bir etiket olmamalı)
                if url_line and not url_line.startswith('#'):
                    # Grup adını bul
                    group_title = "GRUPSUZ KANALLAR"
                    match = re.search(r'group-title=(["\'])(.*?)\1', extinf_line, re.IGNORECASE)
                    if match:
                        title = match.group(2).strip()
                        if title:
                            group_title = title
                    
                    # Kanal adını bul (raporlama için)
                    channel_name_match = re.search(r',(.+)$', extinf_line)
                    channel_name = channel_name_match.group(1).strip() if channel_name_match else "Bilinmeyen Kanal"
                    
                    print(f"Bulundu -> Kanal: '{channel_name}', Grup: '{group_title}'")
                    
                    # Kanal objesini listeye ekle
                    channels.append({
                        'group': group_title,
                        'extinf': extinf_line,
                        'url': url_line
                    })
    
    print(f"\nAnaliz tamamlandı. Toplam {len(channels)} kanal bulundu.")
    return channels

def build_new_playlist(channels, base_url):
    """
    Yapılandırılmış kanal listesini kullanarak yeni M3U içeriğini oluşturur.
    Grupları sıralar ve Türk gruplarını başa alır.
    """
    print("\n--- Yeni Liste Oluşturuluyor ve Sıralanıyor ---")
    
    # Kanalları önce grup adına, sonra kanal adına göre sırala
    # Bu, aynı gruptaki kanalların bir arada kalmasını sağlar
    channels.sort(key=lambda x: (x['group'].lower(), x['extinf'].lower()))

    # Grupları Türk ve diğerleri olarak ayır
    turkish_channels = []
    other_channels = []

    for channel in channels:
        group_lower = channel['group'].lower()
        if 'türk' in group_lower or 'turk' in group_lower:
            turkish_channels.append(channel)
        else:
            other_channels.append(channel)

    print(f"Türk kanalları içeren gruplar başa alınıyor.")
    
    # Yeni M3U içeriğini oluştur
    output_lines = ['#EXTM3U']
    
    # Önce Türk kanallarını ekle
    for channel in turkish_channels:
        output_lines.append(channel['extinf'])
        new_url = f"{base_url.rstrip('/')}/{channel['url']}/index.m3u8"
        output_lines.append(new_url)
        
    # Sonra diğer kanalları ekle
    for channel in other_channels:
        output_lines.append(channel['extinf'])
        new_url = f"{base_url.rstrip('/')}/{channel['url']}/index.m3u8"
        output_lines.append(new_url)
        
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
    
    # 1. Kaynak listeyi analiz et ve kanal objeleri oluştur
    channels_list = parse_source_playlist(source_content)
    
    # 2. Kanal objelerini kullanarak yeni listeyi oluştur
    new_playlist_content = build_new_playlist(channels_list, config['base_url'])
    
    # 3. Sonucu dosyaya kaydet
    save_playlist(new_playlist_content, config['output_file'])

if __name__ == "__main__":
    main()