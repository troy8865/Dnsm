import requests

# M3U kaynak dosya
source_url = "https://raw.githubusercontent.com/troy8865/vwovov/refs/heads/main/vavoo.m3u"
old_url = "https://vavoo.to/vavoo-iptv/play/"
new_url = "https://goldvod.org/tv/vavoo?id="

# Türkiye ile ilgili filtre anahtar kelimeleri
turkey_keywords = ["turkey", "türkiye", "turkiye", "tr"]

response = requests.get(source_url)

if response.status_code == 200:
    content = response.text
    lines = content.strip().splitlines()

    filtered_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#EXTINF"):
            # EXTINF satırındaki metin Türkiye'ye aitse
            if any(keyword in line.lower() for keyword in turkey_keywords):
                # Link satırını da al (#EXTINF + link)
                filtered_lines.append(line.replace(old_url, new_url))
                if i + 1 < len(lines):
                    filtered_lines.append(lines[i + 1].replace(old_url, new_url))
        i += 1

    # Dosyayı kaydet
    with open("serby.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(filtered_lines))

    print("✅ serby.m3u başarıyla oluşturuldu. (Sadece Türkiye)")
else:
    print("❌ Dosya indirilemedi. HTTP Kodu:", response.status_code)
