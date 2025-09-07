import requests

try:
    source_url = "https://raw.githubusercontent.com/troy8865/vwovov/refs/heads/main/vavoo.m3u"
    old_url = "https://vavoo.to/vavoo-iptv/play/"
    new_url = "https://goldvod.org/tv/vavoo?id="

    response = requests.get(source_url)
    response.raise_for_status()

    content = response.text
    lines = content.strip().splitlines()

    updated_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#EXTINF"):
            updated_lines.append(line.replace(old_url, new_url))
            if i + 1 < len(lines):
                updated_lines.append(lines[i + 1].replace(old_url, new_url))
        else:
            # #EXTINF olmayan satırları da korumak istiyorsan, aşağıdaki satırı ekle
            # updated_lines.append(line)
            pass
        i += 1

    with open("serby.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(updated_lines))

    print("✅ serby.m3u başarıyla oluşturuldu. (Filtre yok)")

except requests.RequestException as e:
    print(f"❌ Dosya indirilemedi veya istek başarısız oldu: {e}")
    exit(1)

except Exception as e:
    print(f"❌ Bilinmeyen hata oluştu: {e}")
    exit(1)

          
