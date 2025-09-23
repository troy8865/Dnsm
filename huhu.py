import requests

# M3U dosyasının URL'si
url = "https://raw.githubusercontent.com/doGior/doGiorsHadEnough/refs/heads/master/Huhu/src/main/kotlin/it/dogior/hadEnough/Huhu.kt"

# İndirilen dosyanın adı
output_file = "huhu.m3u"

try:
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()  # Hata varsa exception fırlatır

    # Dosyayı UTF-8 olarak kaydet
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(r.text)

    print(f"M3U dosyası başarıyla indirildi: {output_file}")

except requests.exceptions.RequestException as e:
    print(f"Dosya indirilemedi: {e}")