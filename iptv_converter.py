import yaml
import requests

def load_config(path='config.yaml'):
    """YAML yapılandırma dosyasını oku."""
    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    # Gerekli anahtarların var olduğundan emin ol
    if 'source_playlist_url' not in config:
        raise KeyError("config.yaml içinde 'source_playlist_url' tanımlı olmalı")
    if 'output_file' not in config:
        raise KeyError("config.yaml içinde 'output_file' tanımlı olmalı")
    return config

def download_playlist(url):
    """Verilen URL’den M3U içeriğini indir."""
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text

def parse_playlist(playlist_content):
    """
    Basit bir M3U parser. Örneğin:
    #EXTINF:-1, Kanal Adı
    http://stream.url/kanal1
    """
    lines = playlist_content.splitlines()
    channels = []
    current_info = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("#EXTINF"):
            # Kanal ismi al
            # Örnek: "#EXTINF:-1, Kanal Adı"
            parts = line.split(',', 1)
            if len(parts) == 2:
                current_info = parts[1].strip()
            else:
                current_info = None
        elif line.startswith("http://") or line.startswith("https://"):
            # URL satırı
            url = line
            channels.append({
                'name': current_info,
                'url': url
            })
            current_info = None
        else:
            # Diğer yorum ya da # ile başlayan satırlar
            pass
    return channels

def build_new_playlist(channels_list):
    """
    Yeni M3U içeriği oluştur.
    Burada her kanal için:
    #EXTINF satırı + kanal adı
    URL satırı (orijinal URL’yi kullanıyoruz)
    """
    lines = ["#EXTM3U"]
    for ch in channels_list:
        name = ch.get('name') or "Unnamed"
        url = ch.get('url')
        lines.append(f"#EXTINF:-1,{name}")
        lines.append(url)
    return "\n".join(lines)

def save_playlist(content, filepath):
    """Metni verilen dosyaya kaydet."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    config = load_config()
    print("Kaynak liste indiriliyor:", config['source_playlist_url'])
    playlist_text = download_playlist(config['source_playlist_url'])
    print("Analiz ediliyor...")
    channels = parse_playlist(playlist_text)
    print(f"Toplam {len(channels)} kanal bulundu.")
    new_content = build_new_playlist(channels)
    save_playlist(new_content, config['output_file'])
    print("Yeni liste kaydedildi:", config['output_file'])

if __name__ == "__main__":
    main()
