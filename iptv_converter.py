import requests
import yaml
import sys
import os

# --- Yardımcı Fonksiyonlar ---

def load_config(config_path='config.yml'):
    """
    config.yml dosyasını okur ve ayarları bir sözlük olarak döndürür.
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            # Gerekli alanların varlığını kontrol et
            if not all(key in config for key in ['base_url', 'source_playlist_url', 'output_file']):
                print(f"HATA: '{config_path}' dosyasında 'base_url', 'source_playlist_url' veya 'output_file' anahtarlarından biri eksik.")
                sys.exit(1)
            return config
    except FileNotFoundError:
        print(f"HATA: Yapılandırma dosyası bulunamadı: '{config_path}'")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"HATA: Yapılandırma dosyası okunurken bir hata oluştu: {e}")
        sys.exit(1)

def fetch_playlist(url):
    """
    Verilen URL'den M3U listesinin içeriğini indirir.
    """
    try:
        print(f"Kaynak liste indiriliyor: {url}")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()  # HTTP 200 olmayan durumlar için hata fırlatır
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"HATA: Kaynak liste indirilemedi: {e}")
        sys.exit(1)

def process_playlist(source_content, base_url):
    """
    İndirilen M3U içeriğini işler ve yeni URL'leri oluşturur.
    """
    print("Liste işleniyor ve yeni URL'ler oluşturuluyor...")
    new_lines = []
    lines = source_content.splitlines()

    if not lines or not lines[0].strip().startswith('#EXTM3U'):
        print("UYARI: Kaynak dosya geçerli bir M3U dosyası gibi görünmüyor. Yine de işleme devam ediliyor.")
        new_lines.append('#EXTM3U')
    else:
        new_lines.append(lines[0])

    for i in range(1, len(lines)):
        line = lines[i].strip()
        if not line:
            continue
        
        if line.startswith('#EXTINF:'):
            new_lines.append(line)
        elif not line.startswith('#'):
            # URL'yi oluştur. Örnek: '6814' -> 'http://.../6814/index.m3u8'
            new_url = f"{base_url.rstrip('/')}/{line}/index.m3u8"
            new_lines.append(new_url)
            
    return "\n".join(new_lines)

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
    """
    Betiğin ana çalışma akışını yönetir.
    """
    print("--- M3U Playlist Dönüştürücü Başlatıldı ---")
    
    config = load_config()
    source_content = fetch_playlist(config['source_playlist_url'])
    new_playlist_content = process_playlist(source_content, config['base_url'])
    save_playlist(new_playlist_content, config['output_file'])

if __name__ == "__main__":
    main()